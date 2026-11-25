import json

from app.core.database import session_scope
from app.models_registry import KycCase
from app.shared.ocr.engine import get_engine, set_engine
from tests.helpers import DECLARED, FakeEngine, cni_lines, files, form, make_flat_image, make_image
from tests.integration.utils import CASES, case, codes, submit, upload


def enable_auto_decision(client, platform_admin):
    journey = next(
        j for j in client.get("/api/v1/admin/kyc/journeys", headers=platform_admin).json() if j["organization_id"] is None
    )
    response = client.patch(
        f"/api/v1/admin/kyc/journeys/{journey['id']}", json={"auto_decision_enabled": True}, headers=platform_admin
    )
    assert response.status_code == 200, response.text


def test_creation_with_documents_runs_the_whole_pipeline(client, org):
    created = submit(client, org["api_key"], reference="CUST-001", back=make_image(9))
    assert created.status_code == 202
    body = created.json()
    assert (
        body["reference"] == "CUST-001"
        and body["session"]["token"].startswith("izs_")
        and body["session"]["hosted_url"].endswith(body["session"]["token"])
    )
    detail = case(client, org["api_key"], body["id"])
    assert (detail["status"], detail["status_reason"]) == ("manual_review", "AUTO_DECISION_DISABLED")
    assert (
        detail["extracted"]["surname"]["value"] == "Atángana Mohammadou"
        and detail["declared_identity"]["surname"] == "Atangana Mohammadou"
    )
    assert detail["extracted"]["date_of_birth"]["normalized"] == "1992-06-15" and detail["ocr_confidence"] == 0.96
    assert [(a["number"], a["kind"]) for a in detail["attempts"]] == [(1, "initial")]
    assert {c["check_type"]: c["status"] for c in detail["checks"]}["declared_match"] == "passed"
    assert {"declared_match", "ocr_extraction"} <= set(detail["scope"]["executed_checks"]) and detail["scope"]["disclaimer"]
    assert {d["side"] for d in detail["documents"]} == {"front", "back"} and "storage_key" not in json.dumps(detail)
    assert detail["status_label"] == "Examen par un analyste" and detail["journey_code"] == "standard"


def test_clear_case_is_verified_automatically_when_the_journey_allows_it(client, org, super_admin):
    enable_auto_decision(client, super_admin)
    detail = case(client, org["api_key"], submit(client, org["api_key"]).json()["id"])
    assert (detail["status"], detail["status_reason"], detail["risk_level"]) == ("verified", "VERIFIED_AUTOMATIC", "low")
    assert detail["allowed_actions"] == []


def test_country_and_document_are_mandatory_and_must_be_supported(client, org, super_admin):
    derived = client.post(CASES, data={"document_type": "cni_cm"}, headers=org["api_key"])
    assert derived.status_code == 202 and derived.json()["country_code"] == "CM"
    assert (
        client.post(CASES, data={"document_type": "passport"}, headers=org["api_key"]).json()["error"]["code"]
        == "COUNTRY_REQUIRED"
    )
    unsupported = client.post(CASES, data=form(country_code="FR", document_type="cni_cm"), headers=org["api_key"])
    assert unsupported.status_code == 422 and unsupported.json()["error"]["code"] == "DOCUMENT_NOT_SUPPORTED"
    assert (
        client.post(CASES, data=form(document_type="passport"), headers=org["api_key"]).json()["error"]["code"]
        == "DOCUMENT_NOT_SUPPORTED"
    )
    coverage = next(
        c for c in client.get("/api/v1/admin/kyc/coverage", headers=super_admin).json() if c["document_type"] == "cni_cm"
    )
    assert submit(client, org["api_key"]).status_code == 202
    client.patch(f"/api/v1/admin/kyc/coverage/{coverage['id']}", json={"status": "testing"}, headers=super_admin)
    assert client.post(CASES, data=form(), headers=org["api_key"]).json()["error"]["code"] == "DOCUMENT_NOT_SUPPORTED"


def test_case_without_documents_waits_then_accepts_an_upload(client, org):
    created = submit(client, org["api_key"], with_documents=False).json()
    assert created["status"] == "created" and created["session"]["token"]
    assert upload(client, org["api_key"], created["id"]).status_code == 202
    assert case(client, org["api_key"], created["id"])["status"] == "manual_review"


def test_declared_identity_is_required_before_the_comparison(client, org):
    created = submit(client, org["api_key"], declared=False).json()
    waiting = case(client, org["api_key"], created["id"])
    assert (waiting["status"], waiting["status_reason"]) == ("action_required", "DECLARED_IDENTITY_REQUIRED")
    assert "DECLARED_IDENTITY_MISSING" in codes(waiting)
    body = {"surname": "Atangana Mohammadou", "given_names": "Salah", "date_of_birth": "1992-06-15"}
    assert client.put(f"{CASES}/{created['id']}/declared-identity", json=body, headers=org["api_key"]).status_code == 202
    done = case(client, org["api_key"], created["id"])
    assert done["status"] == "manual_review" and [a["kind"] for a in done["attempts"]] == ["initial", "initial"]
    assert done["attempts_summary"]["data_correction"]["used"] == 0


def test_declared_identity_validation(client, org):
    created = submit(client, org["api_key"], declared=False, with_documents=False).json()
    for body in (
        {"surname": "A", "given_names": "Salah", "date_of_birth": "1992-06-15"},
        {"surname": "Atangana", "given_names": "Salah", "date_of_birth": "2999-01-01"},
    ):
        assert client.put(f"{CASES}/{created['id']}/declared-identity", json=body, headers=org["api_key"]).status_code == 422
    partial = client.post(CASES, data=form(declared_surname="Atangana"), headers=org["api_key"])
    assert partial.json()["error"]["code"] == "DECLARED_IDENTITY_INCOMPLETE"


def test_discrepancy_between_declared_and_read_data_is_classified(client, org):
    wrong = {**DECLARED, "declared_surname": "Ndongo", "declared_date_of_birth": "1990-01-01"}
    response = client.post(CASES, data=form(**wrong), files=files(), headers=org["api_key"])
    detail = case(client, org["api_key"], response.json()["id"])
    assert (detail["status"], detail["status_reason"]) == ("manual_review", "DECLARED_MISMATCH")
    mismatches = {f["field"] for f in detail["flags"] if f["code"] == "DECLARED_MISMATCH"}
    assert mismatches == {"surname", "date_of_birth"} and detail["risk_level"] == "high"
    partial = client.post(
        CASES,
        data=form(**{**DECLARED, "declared_surname": "Atangana"}),
        files=files(front=make_image(31)),
        headers=org["api_key"],
    )
    assert "DECLARED_PARTIAL" in codes(case(client, org["api_key"], partial.json()["id"]))


def test_poor_image_requests_a_recapture_and_history_is_preserved(client, org):
    created = submit(client, org["api_key"], front=make_flat_image()).json()
    blurry = case(client, org["api_key"], created["id"])
    assert (blurry["status"], blurry["status_reason"]) == ("action_required", "IMAGE_QUALITY")
    assert blurry["status_message"].startswith("L'image est de qualité insuffisante") and "LOW_SHARPNESS" in codes(blurry)
    assert "upload_documents" in blurry["allowed_actions"]
    assert upload(client, org["api_key"], created["id"], front=make_image(40)).status_code == 202
    fixed = case(client, org["api_key"], created["id"])
    assert fixed["status"] == "manual_review" and fixed["attempts_summary"]["recapture"] == {"used": 1, "max": 3}
    assert [(a["number"], a["kind"], a["status"]) for a in fixed["attempts"]] == [
        (1, "initial", "action_required"),
        (2, "recapture", "completed"),
    ]
    assert len(fixed["documents"]) == 2 and [d["is_current"] for d in fixed["documents"]].count(True) == 1
    events = client.get(f"{CASES}/{created['id']}/timeline", headers=org["api_key"]).json()
    assert [e["seq"] for e in events] == list(range(1, len(events) + 1))
    assert {"case_created", "attempt_started", "documents_submitted", "status_changed"} <= {e["event_type"] for e in events}


def test_attempt_limits_then_controlled_exception(client, org, platform):
    created = submit(client, org["api_key"], front=make_flat_image()).json()["id"]
    for _ in range(3):
        assert upload(client, org["api_key"], created, front=make_flat_image()).status_code == 202
    exhausted = case(client, org["api_key"], created)
    assert (exhausted["status"], exhausted["status_reason"]) == ("manual_review", "ATTEMPTS_EXHAUSTED")
    assert exhausted["attempts_summary"]["recapture"] == {"used": 3, "max": 3}
    blocked = upload(client, org["api_key"], created)
    assert blocked.status_code == 409 and blocked.json()["error"]["code"] == "INVALID_STATE"
    grant = {"kind": "recapture", "extra": 1, "reason": "Autorisation exceptionnelle du support"}
    assert client.post(f"/api/v1/admin/kyc/cases/{created}/grant-attempts", json=grant, headers=org["admin"]).status_code == 403
    assert client.post(f"/api/v1/admin/kyc/cases/{created}/grant-attempts", json=grant, headers=platform).status_code == 200
    reopened = case(client, org["api_key"], created)
    assert reopened["status"] == "action_required" and reopened["attempts_summary"]["recapture"]["max"] == 4
    assert upload(client, org["api_key"], created, front=make_image(41)).status_code == 202
    assert case(client, org["api_key"], created)["status"] == "manual_review"


def test_data_correction_attempts_are_limited(client, org):
    created = submit(client, org["api_key"], front=make_flat_image()).json()["id"]
    body = {"surname": "Atangana Mohammadou", "given_names": "Salah", "date_of_birth": "1992-06-15"}
    for _ in range(2):
        assert client.put(f"{CASES}/{created}/declared-identity", json=body, headers=org["api_key"]).status_code == 202
    refused = client.put(f"{CASES}/{created}/declared-identity", json=body, headers=org["api_key"])
    assert refused.status_code == 409 and refused.json()["error"]["code"] == "ATTEMPTS_EXHAUSTED"
    assert case(client, org["api_key"], created)["attempts_summary"]["data_correction"] == {"used": 2, "max": 2}


def test_technical_incident_is_not_a_refusal_and_can_be_retried(client, org):
    set_engine(FakeEngine(RuntimeError("secret internal detail")))
    created = submit(client, org["api_key"]).json()["id"]
    failed = case(client, org["api_key"], created)
    assert (failed["status"], failed["failure_kind"], failed["status_reason"]) == ("failed", "technical", "TECHNICAL_ERROR")
    assert "secret internal detail" not in json.dumps(failed) and "not_verified" not in json.dumps(failed["status"])
    assert "Votre identité n'est pas refusée" in failed["status_message"]
    assert (
        client.post(
            f"{CASES}/{created}/decision", json={"decision": "rejected", "reason": "x"}, headers=org["reviewer"]
        ).status_code
        == 409
    )
    set_engine(FakeEngine(cni_lines()))
    assert client.post(f"{CASES}/{created}/reprocess", headers=org["api_key"]).status_code == 403
    assert client.post(f"{CASES}/{created}/reprocess", headers=org["reviewer"]).status_code == 202
    retried = case(client, org["api_key"], created)
    assert retried["status"] == "manual_review" and retried["attempts"][-1]["kind"] == "technical_retry"
    assert client.post(f"{CASES}/{created}/reprocess", headers=org["reviewer"]).status_code == 409


def test_technical_retries_are_limited(client, org):
    set_engine(FakeEngine(RuntimeError("down")))
    created = submit(client, org["api_key"]).json()["id"]
    for _ in range(3):
        assert client.post(f"{CASES}/{created}/reprocess", headers=org["reviewer"]).status_code == 202
    assert client.post(f"{CASES}/{created}/reprocess", headers=org["reviewer"]).json()["error"]["code"] == "ATTEMPTS_EXHAUSTED"


def test_expired_request_is_neither_verified_nor_refused(client, org, platform):
    created = submit(client, org["api_key"], with_documents=False).json()["id"]
    waiting = submit(client, org["api_key"], reference="IN-REVIEW").json()["id"]
    import uuid
    from datetime import UTC, datetime, timedelta

    with session_scope() as db:
        for case_id in (created, waiting):
            db.get(KycCase, uuid.UUID(case_id)).expires_at = datetime.now(UTC) - timedelta(hours=1)
        db.commit()
    expired = case(client, org["api_key"], created)
    assert (expired["status"], expired["status_reason"]) == ("expired", "REQUEST_EXPIRED") and "pas un refus" in expired[
        "status_message"
    ]
    assert upload(client, org["api_key"], created).status_code == 409
    assert case(client, org["api_key"], waiting)["status"] == "manual_review"
    run = client.post("/api/v1/admin/maintenance/run", headers=platform)
    assert run.status_code == 403


def test_maintenance_expires_due_cases(client, org, super_admin):
    created = [submit(client, org["api_key"], reference=f"E{i}", with_documents=False).json()["id"] for i in range(2)]
    import uuid
    from datetime import UTC, datetime, timedelta

    with session_scope() as db:
        for case_id in created:
            db.get(KycCase, uuid.UUID(case_id)).expires_at = datetime.now(UTC) - timedelta(minutes=5)
        db.commit()
    assert client.post("/api/v1/admin/maintenance/run", headers=super_admin).json()["expired_cases"] == 2
    assert {case(client, org["api_key"], i)["status"] for i in created} == {"expired"}


def test_duplicates_are_flagged_and_sent_to_review(client, org, super_admin):
    enable_auto_decision(client, super_admin)
    first = submit(client, org["api_key"], front=make_image(5)).json()["id"]
    same_image = case(client, org["api_key"], submit(client, org["api_key"], front=make_image(5)).json()["id"])
    duplicate = next(f for f in same_image["flags"] if f["code"] == "DUPLICATE_DOCUMENT_IMAGE")
    assert duplicate["related_cases"] == [first] and (same_image["status"], same_image["status_reason"]) == (
        "manual_review",
        "DUPLICATE_DOCUMENT_IMAGE",
    )
    other = case(client, org["api_key"], submit(client, org["api_key"], front=make_image(6)).json()["id"])
    assert "POSSIBLE_DUPLICATE_IDENTITY" in codes(other) and "DUPLICATE_DOCUMENT_IMAGE" not in codes(other)


def test_messages_follow_the_requested_language(client, org):
    created = submit(client, org["api_key"], front=make_flat_image(), lang="en").json()
    english = case(client, org["api_key"], created["id"])
    assert english["language"] == "en" and english["status_label"] == "Action required"
    assert english["status_message"].startswith("The image quality is insufficient") and any(
        "Blurry image" in f["message"] for f in english["flags"]
    )
    french = case(client, org["api_key"], created["id"], lang="fr")
    assert french["status_label"] == "Action requise" and any("Image floue" in f["message"] for f in french["flags"])
    catalogue = client.get("/api/v1/kyc/messages", headers=org["api_key"]).json()
    assert catalogue["statuses"]["verified"] == {"fr": "Identité vérifiée", "en": "Identity verified"}


def test_field_level_visibility_by_role(client, org):
    created = submit(client, org["api_key"]).json()["id"]
    viewer = case(client, org["viewer"], created)
    assert (
        viewer["extracted"]["surname"]["value"].startswith("A")
        and "tángana" not in json.dumps(viewer)
        and "Salah" not in json.dumps(viewer)
    )
    assert (
        viewer["allowed_actions"] == []
        and case(client, org["api_key"], created)["extracted"]["surname"]["value"] == "Atángana Mohammadou"
    )
    assert "view_documents" in case(client, org["reviewer"], created)["allowed_actions"]
    assert "decide" in case(client, org["reviewer"], created)["allowed_actions"]


def test_session_link_rotation_invalidates_the_previous_token(client, org):
    created = submit(client, org["api_key"], with_documents=False).json()
    old = created["session"]["token"]
    assert client.get("/api/v1/kyc/session", headers={"X-Session-Token": old}).status_code == 200
    fresh = client.post(f"{CASES}/{created['id']}/session", headers=org["api_key"]).json()
    assert client.get("/api/v1/kyc/session", headers={"X-Session-Token": old}).status_code == 401
    assert client.get("/api/v1/kyc/session", headers={"X-Session-Token": fresh["token"]}).status_code == 200


def test_reference_rules_and_tenant_isolation(client, org, make_org):
    other = make_org("beta")
    case_id = submit(client, org["api_key"], reference="SHARED").json()["id"]
    duplicate = submit(client, org["api_key"], reference="SHARED")
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "REFERENCE_ALREADY_USED"
    assert submit(client, org["api_key"], reference="bad ref!").status_code == 422
    assert client.get(f"{CASES}/{case_id}", headers=other["api_key"]).status_code == 404
    assert client.get(f"{CASES}/{case_id}/timeline", headers=other["admin"]).status_code == 404
    assert client.get(CASES, headers=other["api_key"]).json()["total"] == 0
    assert submit(client, other["api_key"], reference="SHARED").status_code == 202


def test_invalid_uploads_never_create_a_case(client, org):
    bad = [("a.png", b"not an image", "image/png"), ("a.pdf", b"%PDF-1.4 x", "application/pdf")]
    for name, content, mime in bad:
        assert client.post(CASES, data=form(), files={"front": (name, content, mime)}, headers=org["api_key"]).status_code == 415
    assert (
        client.post(CASES, data=form(), files=files(front=make_image(1, size=(300, 200))), headers=org["api_key"]).status_code
        == 422
    )
    assert client.get(CASES, headers=org["api_key"]).json()["total"] == 0


def test_oversized_file_is_rejected(client, org, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "max_upload_mb", 1)
    big = make_image(1, size=(2000, 1500))
    response = client.post(CASES, data=form(), files=files(front=big), headers=org["api_key"])
    assert response.status_code == 413 and response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_listing_filters_pagination_and_stats(client, org):
    ids = [submit(client, org["api_key"], reference=f"R{i}", front=make_image(20 + i)).json()["id"] for i in range(3)]
    client.post(f"{CASES}/{ids[0]}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    page = client.get(f"{CASES}?page_size=2", headers=org["viewer"]).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    assert client.get(f"{CASES}?status=verified", headers=org["viewer"]).json()["total"] == 1
    assert client.get(f"{CASES}?reference=R2", headers=org["viewer"]).json()["items"][0]["id"] == ids[2]
    assert client.get(f"{CASES}?country_code=CM", headers=org["viewer"]).json()["total"] == 3
    assert client.get(f"{CASES}?page_size=1000", headers=org["viewer"]).status_code == 422
    assert client.get("/api/v1/kyc/stats", headers=org["viewer"]).json() == {"verified": 1, "manual_review": 2}


def test_documents_are_restricted_audited_and_encrypted_at_rest(client, org):
    from sqlalchemy import text

    from app.core.config import get_settings
    from app.core.database import get_engine

    detail = case(client, org["api_key"], submit(client, org["api_key"]).json()["id"])
    url = f"{CASES}/{detail['id']}/documents/{detail['documents'][0]['id']}/content"
    assert (
        client.get(url, headers=org["api_key"]).status_code == 403 and client.get(url, headers=org["viewer"]).status_code == 403
    )
    image = client.get(url, headers=org["reviewer"])
    assert (
        image.status_code == 200
        and image.headers["content-type"] == "image/jpeg"
        and image.headers["cache-control"] == "private, no-store"
    )
    actions = [i["action"] for i in client.get("/api/v1/audit-logs?page_size=200", headers=org["admin"]).json()["items"]]
    assert "kyc.document.viewed" in actions
    with get_engine().connect() as connection:
        for column in ("extracted_data", "declared_identity"):
            raw = connection.execute(text(f"SELECT {column} FROM kyc_cases")).scalar_one()  # noqa: S608
            assert "Atángana" not in raw and "Salah" not in raw and "SALAH" not in raw
        key = connection.execute(text("SELECT storage_key FROM kyc_documents")).scalar_one()
    assert not (get_settings().storage_dir / key).read_bytes().startswith(b"\xff\xd8\xff")


def test_audit_and_events_contain_no_personal_data(client, org):
    case_id = submit(client, org["api_key"]).json()["id"]
    client.post(f"{CASES}/{case_id}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    dump = json.dumps(client.get(f"/api/v1/audit-logs?resource_id={case_id}", headers=org["admin"]).json(), ensure_ascii=False)
    dump += json.dumps(client.get(f"{CASES}/{case_id}/timeline", headers=org["admin"]).json(), ensure_ascii=False)
    for personal in ("Atángana", "Mohammadou", "SALAH", "Salah", "15.06.1992", "1992-06-15", "Baffousam"):
        assert personal not in dump


def test_engine_runs_once_per_document_attempt(client, org):
    submit(client, org["api_key"])
    assert get_engine().calls == 1
