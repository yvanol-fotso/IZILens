from tests.helpers import files, form, make_flat_image, make_image
from tests.integration.utils import case, submit

SESSION = "/api/v1/kyc/session"
IDENTITY = {"surname": "Atangana Mohammadou", "given_names": "Salah", "date_of_birth": "1992-06-15"}


def headers(token):
    return {"X-Session-Token": token}


def start(client, org, **kwargs):
    created = submit(client, org["api_key"], declared=False, with_documents=False, **kwargs).json()
    return created["id"], headers(created["session"]["token"])


def test_hosted_journey_end_to_end_in_french(client, org):
    case_id, session = start(client, org)
    view = client.get(SESSION, headers=session).json()
    assert view["next_action"] == "accept_terms" and view["consent_required"] and len(view["instructions"]) == 4
    assert view["documents_allowed"] == [
        {"document_type": "cni_cm", "label": "Carte nationale d'identité (Cameroun)", "sides_required": ["front"]}
    ]
    assert client.post(f"{SESSION}/documents", files=files(), headers=session).json()["error"]["code"] == "CONSENT_REQUIRED"
    assert (
        client.post(f"{SESSION}/consent", json={"accepted": False, "terms_version": "2026-11"}, headers=session).status_code
        == 422
    )
    accepted = client.post(f"{SESSION}/consent", json={"accepted": True, "terms_version": "2026-11"}, headers=session).json()
    assert accepted["next_action"] == "provide_identity" and accepted["status"] == "in_progress"
    assert (
        client.post(f"{SESSION}/documents", files=files(), headers=session).json()["error"]["code"]
        == "DECLARED_IDENTITY_REQUIRED"
    )
    identity = client.put(f"{SESSION}/declared-identity", json=IDENTITY, headers=session)
    assert identity.status_code == 202 and identity.json()["next_action"] == "upload_document"
    assert client.post(f"{SESSION}/documents", files=files(), headers=session).status_code == 202
    result = client.get(f"{SESSION}/result", headers=session).json()
    assert (
        result["status"] == "manual_review"
        and result["final"]
        and "analyste" in result["message"]
        and "approbation complète" in result["scope"]["disclaimer"]
    )
    assert client.get(SESSION, headers=session).json()["can_upload"] is False


def test_hosted_journey_in_english_and_recapture_guidance(client, org):
    _, session = start(client, org, lang="en")
    client.post(f"{SESSION}/consent", json={"accepted": True, "terms_version": "2026-11"}, headers=session)
    client.put(f"{SESSION}/declared-identity", json=IDENTITY, headers=session)
    client.post(f"{SESSION}/documents", files=files(front=make_flat_image()), headers=session)
    view = client.get(SESSION, headers=session).json()
    assert (
        view["status"] == "action_required"
        and view["can_upload"]
        and view["message"].startswith("The image quality is insufficient")
    )
    assert view["instructions"][0].startswith("Accept the terms") and view["attempts"]["recapture"] == {"used": 0, "max": 3}
    assert client.post(f"{SESSION}/documents", files=files(front=make_image(50)), headers=session).status_code == 202
    assert client.get(SESSION, headers=session).json()["attempts"]["recapture"]["used"] == 1


def test_session_endpoints_reject_missing_wrong_and_foreign_tokens(client, org, make_org):
    assert client.get(SESSION).status_code == 401
    assert client.get(SESSION, headers=headers("izs_invalid")).status_code == 401
    case_id, session = start(client, org)
    other = make_org("beta")
    assert client.get(SESSION, headers=other["api_key"]).status_code == 401
    assert case(client, org["api_key"], case_id)["status"] == "created"


def test_session_never_exposes_extracted_data_or_other_cases(client, org):
    _, session = start(client, org)
    client.post(f"{SESSION}/consent", json={"accepted": True, "terms_version": "2026-11"}, headers=session)
    client.put(f"{SESSION}/declared-identity", json=IDENTITY, headers=session)
    client.post(f"{SESSION}/documents", files=files(), headers=session)
    for path in ("", "/result"):
        text = client.get(f"{SESSION}{path}", headers=session).text
        assert "Atángana" not in text and "storage_key" not in text and "extracted" not in text and "ocr_confidence" not in text


def test_hosted_session_of_expired_case_is_closed(client, org):
    import uuid
    from datetime import UTC, datetime, timedelta

    from app.core.database import session_scope
    from app.models_registry import KycCase

    case_id, session = start(client, org)
    with session_scope() as db:
        db.get(KycCase, uuid.UUID(case_id)).expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()
    view = client.get(SESSION, headers=session).json()
    assert view["status"] == "expired" and view["next_action"] == "done" and view["can_upload"] is False
    assert "pas un refus" in client.get(f"{SESSION}/result", headers=session).json()["message"]
    assert client.post(
        f"{SESSION}/consent", json={"accepted": True, "terms_version": "2026-11"}, headers=session
    ).status_code in (200, 409)


def test_api_and_hosted_modes_give_the_same_business_result(client, org, make_org):
    other = make_org("beta")
    api_case = case(client, org["api_key"], submit(client, org["api_key"], front=make_image(70)).json()["id"])
    case_id, session = start(client, other)
    client.post(f"{SESSION}/consent", json={"accepted": True, "terms_version": "2026-11"}, headers=session)
    client.put(f"{SESSION}/declared-identity", json=IDENTITY, headers=session)
    client.post(f"{SESSION}/documents", files=files(front=make_image(71)), headers=session)
    hosted_case = case(client, other["api_key"], case_id)
    assert (hosted_case["status"], hosted_case["status_reason"], hosted_case["risk_level"]) == (
        api_case["status"],
        api_case["status_reason"],
        api_case["risk_level"],
    )
    assert hosted_case["extracted"]["surname"]["value"] == api_case["extracted"]["surname"]["value"]


def test_client_can_pass_legal_consent_evidence_in_api_mode(client, org):
    created = client.post("/api/v1/kyc/cases", data=form(consent_terms_version="2026-11"), headers=org["api_key"])
    assert created.status_code == 202
    session = headers(created.json()["session"]["token"])
    assert client.get(SESSION, headers=session).json()["consent_given"] is True
