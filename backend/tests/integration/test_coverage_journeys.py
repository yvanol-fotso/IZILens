from tests.integration.utils import CASES, case, submit

ADMIN = "/api/v1/admin"
JOURNEYS = "/api/v1/kyc/journeys"
FULL_CHECKS = ["document_quality", "document_recognition", "ocr_extraction", "declared_match"]


def test_only_validated_documents_are_presented_and_gaps_are_reported(client, org, super_admin):
    overview = client.get("/api/v1/kyc/coverage", headers=org["viewer"]).json()
    assert [(c["country_code"], c["document_type"]) for c in overview["supported"]] == [("CM", "cni_cm")]
    assert set(overview["gaps"]) == {"CA", "CI", "SN", "BJ", "TG", "GA", "CD", "NG", "GH", "CG", "BF"}
    assert client.get("/api/v1/kyc/coverage?country_code=CI", headers=org["viewer"]).json()["supported"] == []
    new = {
        "country_code": "SN",
        "document_type": "cni_sn",
        "label_fr": "Carte d'identité (Sénégal)",
        "label_en": "ID card (Senegal)",
        "status": "testing",
    }
    row = client.post(f"{ADMIN}/kyc/coverage", json=new, headers=super_admin)
    assert row.status_code == 201 and client.post(f"{ADMIN}/kyc/coverage", json=new, headers=super_admin).status_code == 409
    assert client.get("/api/v1/kyc/coverage?country_code=SN", headers=org["viewer"]).json()["supported"] == []
    assert client.patch(f"{ADMIN}/kyc/coverage/{row.json()['id']}", json={"status": "supported"}, headers=super_admin).json()[
        "validated_at"
    ]
    assert [
        c["document_type"] for c in client.get("/api/v1/kyc/coverage?country_code=SN", headers=org["viewer"]).json()["supported"]
    ] == ["cni_sn"]
    assert "SN" not in client.get("/api/v1/kyc/coverage", headers=org["viewer"]).json()["gaps"]


def test_coverage_management_is_reserved_to_the_super_admin(client, org, platform):
    new = {"country_code": "GH", "document_type": "ghana_card", "label_fr": "Ghana Card", "label_en": "Ghana Card"}
    assert client.get(f"{ADMIN}/kyc/coverage", headers=platform).status_code == 200
    assert client.post(f"{ADMIN}/kyc/coverage", json=new, headers=platform).status_code == 403
    assert client.post(f"{ADMIN}/kyc/coverage", json=new, headers=org["admin"]).status_code == 403


def test_second_side_is_required_when_the_matrix_says_so(client, org, super_admin):
    row = client.get(f"{ADMIN}/kyc/coverage", headers=super_admin).json()[0]
    client.patch(f"{ADMIN}/kyc/coverage/{row['id']}", json={"sides_required": ["front", "back"]}, headers=super_admin)
    missing = submit(client, org["api_key"])
    assert missing.status_code == 422 and missing.json()["error"]["code"] == "DOCUMENT_SIDE_REQUIRED"
    from tests.helpers import make_image

    assert submit(client, org["api_key"], back=make_image(12)).status_code == 202


def test_client_journeys_cannot_remove_mandatory_platform_checks(client, org):
    weak = {"code": "weak", "name": "Allégé", "required_checks": ["document_quality"]}
    refused = client.post(JOURNEYS, json=weak, headers=org["admin"])
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "MANDATORY_CHECK_REMOVED"
    stricter = {
        "code": "strict",
        "name": "Renforcé",
        "required_checks": [*FULL_CHECKS, "face_match", "liveness"],
        "expiry_hours": 24,
        "max_attempts": {"recapture": 1},
        "review_team": "client",
        "auto_decision_enabled": True,
    }
    created = client.post(JOURNEYS, json=stricter, headers=org["admin"])
    assert created.status_code == 201
    body = created.json()
    assert body["organization_id"] == org["organization"]["id"] and body["parameters_validated"] is False
    assert body["max_attempts"] == {"recapture": 1, "data_correction": 2, "technical_retry": 3}
    assert client.post(JOURNEYS, json=stricter, headers=org["admin"]).status_code == 409
    assert client.post(JOURNEYS, json=stricter, headers=org["reviewer"]).status_code == 403
    assert (
        client.patch(f"{JOURNEYS}/{body['id']}", json={"required_checks": ["ocr_extraction"]}, headers=org["admin"]).status_code
        == 422
    )


def test_journey_configuration_is_validated(client, org):
    base = {"code": "cfg", "name": "Config"}
    bad = [
        {"max_attempts": {"recapture": 99}},
        {"max_attempts": {"unknown": 1}},
        {"thresholds": {"ocr_review": 1.5}},
        {"thresholds": {"x": 0.5}},
        {"decision_rules": {"underage": "ignore"}},
        {"decision_rules": {"nope": "manual_review"}},
        {"required_checks": ["nope"]},
        {"billing": {"free": True}},
        {"expiry_hours": 0},
        {"code": "Bad Code!"},
    ]
    for extra in bad:
        assert client.post(JOURNEYS, json={**base, **extra}, headers=org["admin"]).status_code == 422, extra


def test_case_uses_the_requested_journey_and_its_expiry_and_limits(client, org):
    client.post(
        JOURNEYS,
        json={"code": "short", "name": "Court", "expiry_hours": 2, "max_attempts": {"recapture": 0}},
        headers=org["admin"],
    )
    created = submit(client, org["api_key"], journey_code="short", front=None, with_documents=False).json()
    detail = case(client, org["api_key"], created["id"])
    assert detail["journey_code"] == "short" and detail["attempts_summary"]["recapture"]["max"] == 0
    from datetime import datetime

    expires = datetime.fromisoformat(created["session"]["expires_at"])
    assert 1 <= (expires - datetime.fromisoformat(created["created_at"])).total_seconds() / 3600 <= 3
    assert submit(client, org["api_key"], journey_code="unknown", reference="U").json()["error"]["code"] == "JOURNEY_NOT_FOUND"


def test_organization_default_journey_is_used_when_none_is_requested(client, org):
    client.post(JOURNEYS, json={"code": "mine", "name": "Mon parcours", "is_default": True}, headers=org["admin"])
    assert (
        case(client, org["api_key"], submit(client, org["api_key"], with_documents=False).json()["id"])["journey_code"] == "mine"
    )
    other = client.get(JOURNEYS, headers=org["viewer"]).json()
    assert {j["code"] for j in other} == {"standard", "mine"}


def test_platform_parameters_are_validated_explicitly_and_changes_reset_validation(client, org, super_admin):
    journey = next(j for j in client.get(f"{ADMIN}/kyc/journeys", headers=super_admin).json() if j["organization_id"] is None)
    assert journey["parameters_validated"] is False
    ok = client.patch(f"{ADMIN}/kyc/journeys/{journey['id']}", json={"parameters_validated": True}, headers=super_admin).json()
    assert ok["parameters_validated"] is True
    changed = client.patch(f"{ADMIN}/kyc/journeys/{journey['id']}", json={"expiry_hours": 48}, headers=super_admin).json()
    assert changed["parameters_validated"] is False and changed["expiry_hours"] == 48
    assert client.patch(f"{JOURNEYS}/{journey['id']}", json={"expiry_hours": 1}, headers=org["admin"]).status_code in (403, 404)
    mine = client.post(JOURNEYS, json={"code": "own", "name": "Propre"}, headers=org["admin"]).json()
    assert client.patch(f"{JOURNEYS}/{mine['id']}", json={"parameters_validated": True}, headers=org["admin"]).status_code == 403


def test_platform_creates_a_journey_for_a_given_organization(client, org, super_admin):
    body = {"code": "bank", "name": "Banque", "organization_id": org["organization"]["id"], "auto_decision_enabled": True}
    created = client.post(f"{ADMIN}/kyc/journeys", json=body, headers=super_admin)
    assert created.status_code == 201 and created.json()["organization_id"] == org["organization"]["id"]
    assert "bank" in {j["code"] for j in client.get(JOURNEYS, headers=org["admin"]).json()}


def test_case_listing_endpoint_still_works_for_all_client_roles(client, org):
    for who in ("admin", "reviewer", "viewer", "api_key"):
        assert client.get(CASES, headers=org[who]).status_code == 200
