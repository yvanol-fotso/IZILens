import json

from app.shared.ocr.engine import get_engine, set_engine
from tests.helpers import FakeEngine, cni_lines, files, make_image

CASES = "/api/v1/kyc/cases"


def submit(client, who, reference=None, **kwargs):
    data = {"reference": reference} if reference else None
    return client.post(CASES, files=files(**kwargs), data=data, headers=who)


def test_full_flow_submit_ocr_review_approve(client, org):
    created = submit(client, org["api_key"], reference="CUST-001", back=make_image(9))
    assert created.status_code == 202 and created.json()["reference"] == "CUST-001"
    case_id = created.json()["id"]

    detail = client.get(f"{CASES}/{case_id}", headers=org["api_key"]).json()
    assert detail["status"] == "pending_review" and detail["risk_level"] == "low"
    assert detail["extracted"]["surname"]["value"] == "Atángana Mohammadou"
    assert detail["extracted"]["date_of_birth"]["normalized"] == "1992-06-15"
    assert detail["ocr_confidence"] == 0.96 and {d["side"] for d in detail["documents"]} == {"front", "back"}
    assert "storage_key" not in json.dumps(detail)

    assert client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["api_key"]).status_code == 403
    assert client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["viewer"]).status_code == 403
    approved = client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert approved.status_code == 200 and approved.json()["status"] == "approved" and approved.json()["decided_by_user_id"]
    again = client.post(f"{CASES}/{case_id}/decision", json={"decision": "rejected", "reason": "x"}, headers=org["reviewer"])
    assert again.status_code == 409 and again.json()["error"]["code"] == "INVALID_STATE"


def test_rejection_requires_reason_and_high_risk_approval_requires_justification(client, org):
    set_engine(FakeEngine(cni_lines(dob="01.01.2015")))
    case_id = submit(client, org["api_key"]).json()["id"]
    assert client.get(f"{CASES}/{case_id}", headers=org["api_key"]).json()["risk_level"] == "high"
    assert client.post(f"{CASES}/{case_id}/decision", json={"decision": "rejected"}, headers=org["reviewer"]).status_code == 422
    blocked = client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert blocked.status_code == 422 and blocked.json()["error"]["code"] == "REASON_REQUIRED_FOR_HIGH_RISK"
    ok = client.post(
        f"{CASES}/{case_id}/decision", json={"decision": "rejected", "reason": "Titulaire mineur"}, headers=org["reviewer"]
    )
    assert ok.status_code == 200 and ok.json()["decision_reason"] == "Titulaire mineur"


def test_document_content_is_restricted_and_audited(client, org):
    detail = client.get(f"{CASES}/{submit(client, org['api_key']).json()['id']}", headers=org["api_key"]).json()
    url = f"{CASES}/{detail['id']}/documents/{detail['documents'][0]['id']}/content"
    assert client.get(url, headers=org["api_key"]).status_code == 403
    assert client.get(url, headers=org["viewer"]).status_code == 403
    image = client.get(url, headers=org["reviewer"])
    assert (
        image.status_code == 200
        and image.headers["content-type"] == "image/jpeg"
        and image.headers["cache-control"] == "private, no-store"
    )
    actions = [i["action"] for i in client.get("/api/v1/audit-logs?page_size=200", headers=org["admin"]).json()["items"]]
    assert "kyc.document.viewed" in actions


def test_duplicate_image_and_identity_are_flagged(client, org):
    first = submit(client, org["api_key"], front=make_image(5)).json()["id"]
    same_image = submit(client, org["api_key"], front=make_image(5)).json()["id"]
    flags = client.get(f"{CASES}/{same_image}", headers=org["api_key"]).json()["flags"]
    duplicate = next(f for f in flags if f["code"] == "DUPLICATE_DOCUMENT_IMAGE")
    assert duplicate["severity"] == "high" and duplicate["related_cases"] == [first]
    other_image = submit(client, org["api_key"], front=make_image(6)).json()["id"]
    codes = {f["code"] for f in client.get(f"{CASES}/{other_image}", headers=org["api_key"]).json()["flags"]}
    assert "POSSIBLE_DUPLICATE_IDENTITY" in codes and "DUPLICATE_DOCUMENT_IMAGE" not in codes


def test_tenant_isolation(client, org, make_org):
    other = make_org("beta")
    case_id = submit(client, org["api_key"], reference="SHARED-REF").json()["id"]
    assert client.get(f"{CASES}/{case_id}", headers=other["api_key"]).status_code == 404
    assert client.get(f"{CASES}/{case_id}", headers=other["admin"]).status_code == 404
    assert client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=other["reviewer"]).status_code == 404
    assert client.get(CASES, headers=other["api_key"]).json()["total"] == 0
    assert submit(client, other["api_key"], reference="SHARED-REF").status_code == 202


def test_reference_must_be_unique_and_well_formed(client, org):
    assert submit(client, org["api_key"], reference="REF-1").status_code == 202
    duplicate = submit(client, org["api_key"], reference="REF-1")
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "REFERENCE_ALREADY_USED"
    assert submit(client, org["api_key"], reference="bad ref!").status_code == 422


def test_invalid_uploads_are_rejected_without_creating_cases(client, org):
    assert client.post(CASES, files={"front": ("a.png", b"not an image", "image/png")}, headers=org["api_key"]).status_code == 415
    assert (
        client.post(CASES, files={"front": ("a.pdf", b"%PDF-1.4 x", "application/pdf")}, headers=org["api_key"]).status_code
        == 415
    )
    assert client.post(CASES, files=files(front=make_image(1, size=(300, 200))), headers=org["api_key"]).status_code == 422
    assert client.post(CASES, files={"back": ("b.png", make_image(1), "image/png")}, headers=org["api_key"]).status_code == 422
    assert client.post(CASES, headers=org["api_key"]).status_code == 422
    assert client.get(CASES, headers=org["api_key"]).json()["total"] == 0


def test_oversized_file_rejected(client, org, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "max_upload_mb", 1)
    big = make_image(1, size=(2000, 1500))
    assert len(big) > 1024 * 1024
    response = client.post(CASES, files=files(front=big), headers=org["api_key"])
    assert response.status_code == 413 and response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_ocr_failure_marks_case_failed_then_reprocess_recovers(client, org):
    set_engine(FakeEngine(RuntimeError("boom with secret details")))
    case_id = submit(client, org["api_key"]).json()["id"]
    failed = client.get(f"{CASES}/{case_id}", headers=org["api_key"]).json()
    assert failed["status"] == "failed" and failed["failure_reason"] == "OCR_ERROR" and "boom" not in json.dumps(failed)
    assert client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["reviewer"]).status_code == 409
    set_engine(FakeEngine(cni_lines()))
    assert client.post(f"{CASES}/{case_id}/reprocess", headers=org["api_key"]).status_code == 403
    assert client.post(f"{CASES}/{case_id}/reprocess", headers=org["reviewer"]).status_code == 202
    assert client.get(f"{CASES}/{case_id}", headers=org["api_key"]).json()["status"] == "pending_review"
    assert client.post(f"{CASES}/{case_id}/reprocess", headers=org["reviewer"]).status_code == 409


def test_unreadable_document_goes_to_review_with_high_risk(client, org):
    set_engine(FakeEngine([]))
    detail = client.get(f"{CASES}/{submit(client, org['api_key']).json()['id']}", headers=org["api_key"]).json()
    assert detail["status"] == "pending_review" and detail["risk_level"] == "high"
    assert "NO_TEXT_DETECTED" in {f["code"] for f in detail["flags"]}


def test_listing_filters_and_pagination(client, org):
    ids = [submit(client, org["api_key"], reference=f"R{i}", front=make_image(20 + i)).json()["id"] for i in range(3)]
    client.post(f"{CASES}/{ids[0]}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    page = client.get(f"{CASES}?page_size=2", headers=org["viewer"]).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    assert client.get(f"{CASES}?status=approved", headers=org["viewer"]).json()["total"] == 1
    assert client.get(f"{CASES}?reference=R2", headers=org["viewer"]).json()["items"][0]["id"] == ids[2]
    assert client.get(f"{CASES}?page_size=1000", headers=org["viewer"]).status_code == 422


def test_audit_trail_covers_the_workflow_and_contains_no_personal_data(client, org):
    case_id = submit(client, org["api_key"]).json()["id"]
    client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    logs = client.get(f"/api/v1/audit-logs?resource_id={case_id}", headers=org["admin"]).json()["items"]
    assert [ln["action"] for ln in reversed(logs)] == ["kyc.case.created", "kyc.case.processed", "kyc.case.approved"]
    dump = json.dumps(logs, ensure_ascii=False)
    for personal in ("Atángana", "Mohammadou", "SALAH", "15.06.1992", "Baffousam", "1992"):
        assert personal not in dump


def test_personal_data_is_encrypted_in_database_and_storage(client, org):
    from sqlalchemy import text

    from app.core.config import get_settings
    from app.core.database import get_engine

    case_id = submit(client, org["api_key"]).json()["id"]
    with get_engine().connect() as connection:
        raw = connection.execute(text("SELECT extracted_data FROM kyc_cases")).scalar_one()
        assert "Atángana" not in raw and "SALAH" not in raw
        key = connection.execute(text("SELECT storage_key FROM kyc_documents")).scalar_one()
    stored = (get_settings().storage_dir / key).read_bytes()
    assert not stored.startswith(b"\xff\xd8\xff") and case_id


def test_engine_is_called_once_per_case(client, org):
    submit(client, org["api_key"])
    assert get_engine().calls == 1
