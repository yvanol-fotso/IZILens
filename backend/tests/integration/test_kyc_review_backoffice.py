from tests.helpers import make_image
from tests.integration.utils import CASES, case, codes, submit

ADMIN = "/api/v1/admin"


def review_case(client, org, **kwargs):
    created = submit(client, org["api_key"], **kwargs).json()["id"]
    assert case(client, org["api_key"], created)["status"] == "manual_review"
    return created


def journey_id(client, super_admin, organization_id=None):
    journeys = client.get(f"{ADMIN}/kyc/journeys", headers=super_admin).json()
    return next(j["id"] for j in journeys if j["organization_id"] == organization_id)


def patch_journey(client, super_admin, **changes):
    response = client.patch(f"{ADMIN}/kyc/journeys/{journey_id(client, super_admin)}", json=changes, headers=super_admin)
    assert response.status_code == 200, response.text
    return response.json()


def test_review_queue_assignment_and_decision_rules(client, org):
    first, second = review_case(client, org), review_case(client, org, front=make_image(81), reference="B")
    queue = client.get("/api/v1/kyc/review-queue", headers=org["reviewer"]).json()
    assert queue["total"] == 2 and queue["items"][0]["id"] == first
    assert client.get("/api/v1/kyc/review-queue", headers=org["viewer"]).status_code == 403
    assert client.get("/api/v1/kyc/review-queue?unassigned=true", headers=org["reviewer"]).json()["total"] == 2
    assigned = client.post(f"{CASES}/{first}/assign", json={}, headers=org["reviewer"])
    assert assigned.status_code == 200 and assigned.json()["assigned_to_user_id"]
    assert client.get("/api/v1/kyc/review-queue?mine=true", headers=org["reviewer"]).json()["total"] == 1
    assert client.get("/api/v1/kyc/review-queue?unassigned=true", headers=org["reviewer"]).json()["total"] == 1
    other_reviewer = client.get("/api/v1/auth/me", headers=org["admin"]).json()["id"]
    assert (
        client.post(f"{CASES}/{second}/assign", json={"assignee_user_id": other_reviewer}, headers=org["reviewer"]).status_code
        == 403
    )
    assert (
        client.post(f"{CASES}/{second}/assign", json={"assignee_user_id": other_reviewer}, headers=org["admin"]).status_code
        == 200
    )
    blocked = client.post(f"{CASES}/{second}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert blocked.status_code == 403 and blocked.json()["error"]["code"] == "ASSIGNED_TO_ANOTHER"
    assert client.post(f"{CASES}/{second}/decision", json={"decision": "approved"}, headers=org["admin"]).status_code == 200


def test_decision_requirements_and_trace(client, org):
    created = review_case(client, org, front=make_image(82))
    assert client.post(f"{CASES}/{created}/decision", json={"decision": "rejected"}, headers=org["reviewer"]).status_code == 422
    assert client.post(f"{CASES}/{created}/decision", json={"decision": "approved"}, headers=org["viewer"]).status_code == 403
    assert client.post(f"{CASES}/{created}/decision", json={"decision": "approved"}, headers=org["api_key"]).status_code == 403
    decided = client.post(
        f"{CASES}/{created}/decision", json={"decision": "rejected", "reason": "Photo non conforme"}, headers=org["reviewer"]
    ).json()
    assert (decided["status"], decided["status_reason"], decided["decision_reason"]) == (
        "not_verified",
        "REJECTED_MANUAL",
        "Photo non conforme",
    )
    assert decided["decided_by_user_id"] and decided["decided_at"]
    again = client.post(f"{CASES}/{created}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert again.status_code == 409 and again.json()["error"]["code"] == "INVALID_STATE"
    events = client.get(f"{CASES}/{created}/timeline", headers=org["admin"]).json()
    last = events[-1]
    assert (last["to_status"], last["actor_type"], last["actor_id"]) == ("not_verified", "user", decided["decided_by_user_id"])


def test_high_risk_approval_needs_a_justification(client, org):
    from tests.helpers import DECLARED, files, form

    response = client.post(
        CASES, data=form(**{**DECLARED, "declared_surname": "Ndongo"}), files=files(front=make_image(84)), headers=org["api_key"]
    )
    created = response.json()["id"]
    assert case(client, org["api_key"], created)["risk_level"] == "high"
    refused = client.post(f"{CASES}/{created}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "REASON_REQUIRED_FOR_HIGH_RISK"
    ok = client.post(
        f"{CASES}/{created}/decision",
        json={"decision": "approved", "reason": "Nom d'usage vérifié par téléphone"},
        headers=org["reviewer"],
    )
    assert ok.status_code == 200 and ok.json()["status"] == "verified"


def test_complement_request_reopens_the_case_for_the_person(client, org):
    created = review_case(client, org, front=make_image(85))
    assert client.post(f"{CASES}/{created}/request-action", json={"reason": "ok"}, headers=org["reviewer"]).status_code == 422
    response = client.post(
        f"{CASES}/{created}/request-action", json={"reason": "Merci de refaire la photo du recto"}, headers=org["reviewer"]
    )
    assert response.json()["status"] == "action_required" and response.json()["status_reason"] == "COMPLEMENT_REQUESTED"
    assert (
        client.post(
            f"{CASES}/{created}/documents", files={"front": ("a.png", make_image(86), "image/png")}, headers=org["api_key"]
        ).status_code
        == 202
    )
    assert case(client, org["api_key"], created)["status"] == "manual_review"


def test_two_review_teams_share_the_work_according_to_the_journey(client, org, platform, super_admin):
    patch_journey(client, super_admin, review_team="platform")
    created = review_case(client, org, front=make_image(87))
    detail = case(client, org["reviewer"], created)
    assert detail["review_team"] == "platform"
    assert client.get("/api/v1/kyc/review-queue", headers=org["reviewer"]).json()["total"] == 0
    refused = client.post(f"{CASES}/{created}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    assert refused.status_code == 403 and refused.json()["error"]["code"] == "REVIEW_TEAM_MISMATCH"
    assert client.get(f"{ADMIN}/kyc/review-queue", headers=platform).json()["total"] == 1
    assert client.post(f"{ADMIN}/kyc/cases/{created}/assign", json={}, headers=platform).status_code == 200
    done = client.post(f"{ADMIN}/kyc/cases/{created}/decision", json={"decision": "approved"}, headers=platform)
    assert done.status_code == 200 and done.json()["status"] == "verified"


def test_client_team_cases_are_not_decided_by_the_platform_team(client, org, platform, super_admin):
    patch_journey(client, super_admin, review_team="client")
    created = review_case(client, org, front=make_image(88))
    refused = client.post(f"{ADMIN}/kyc/cases/{created}/decision", json={"decision": "approved"}, headers=platform)
    assert refused.status_code == 403 and refused.json()["error"]["code"] == "REVIEW_TEAM_MISMATCH"
    assert (
        client.post(f"{ADMIN}/kyc/cases/{created}/decision", json={"decision": "approved"}, headers=super_admin).status_code
        == 200
    )


def test_backoffice_is_closed_to_clients_and_open_to_platform_roles(client, org, platform, super_admin):
    for who in ("admin", "reviewer", "viewer", "api_key"):
        assert client.get(f"{ADMIN}/kyc/cases", headers=org[who]).status_code == 403
    assert client.get(f"{ADMIN}/kyc/cases", headers=platform).status_code == 200
    assert client.get("/api/v1/kyc/cases", headers=platform).status_code == 403


def test_backoffice_sees_all_organizations_and_filters(client, org, make_org, platform):
    other = make_org("beta")
    a, b = review_case(client, org, front=make_image(90)), review_case(client, other, front=make_image(91))
    everything = client.get(f"{ADMIN}/kyc/cases", headers=platform).json()
    assert everything["total"] == 2
    only = client.get(f"{ADMIN}/kyc/cases?organization_id={other['organization']['id']}", headers=platform).json()
    assert [i["id"] for i in only["items"]] == [b]
    assert client.get(f"{ADMIN}/kyc/stats", headers=platform).json() == {"manual_review": 2}
    detail = client.get(f"{ADMIN}/kyc/cases/{a}", headers=platform).json()
    assert detail["extracted"]["surname"]["value"] == "Atángana Mohammadou" and "view_documents" in detail["allowed_actions"]
    assert client.get(f"{ADMIN}/kyc/cases/{a}/timeline", headers=platform).status_code == 200


def test_status_override_is_restricted_validated_and_audited(client, org, platform, super_admin):
    created = review_case(client, org, front=make_image(92))
    body = {"to_status": "verified", "reason": "Vérification manuelle complémentaire validée"}
    assert client.post(f"{ADMIN}/kyc/cases/{created}/transition", json=body, headers=platform).status_code == 403
    assert (
        client.post(f"{ADMIN}/kyc/cases/{created}/transition", json={**body, "reason": "court"}, headers=super_admin).status_code
        == 422
    )
    assert (
        client.post(
            f"{ADMIN}/kyc/cases/{created}/transition", json={**body, "to_status": "processing"}, headers=super_admin
        ).json()["error"]["code"]
        == "INVALID_TRANSITION"
    )
    done = client.post(f"{ADMIN}/kyc/cases/{created}/transition", json=body, headers=super_admin).json()
    assert (done["status"], done["status_reason"]) == ("verified", "ADMIN_TRANSITION")
    final = client.post(
        f"{ADMIN}/kyc/cases/{created}/transition", json={**body, "to_status": "not_verified"}, headers=super_admin
    )
    assert final.status_code == 409 and final.json()["error"]["code"] == "INVALID_TRANSITION"
    assert "kyc.case.admin_transition" in [
        i["action"]
        for i in client.get(f"{ADMIN.replace('/admin', '')}/audit-logs?page_size=200", headers=super_admin).json()["items"]
    ]


def test_mandatory_biometrics_hold_the_case_and_gate_the_decision(client, org, platform, super_admin):
    patch_journey(
        client,
        super_admin,
        required_checks=[
            "document_quality",
            "document_recognition",
            "ocr_extraction",
            "declared_match",
            "face_match",
            "liveness",
        ],
    )
    created = submit(client, org["api_key"], front=make_image(93)).json()["id"]
    waiting = case(client, org["api_key"], created)
    assert (waiting["status"], waiting["status_reason"]) == ("in_progress", "AWAITING_FACE_MATCH")

    def check(kind, status):
        return client.post(
            f"{ADMIN}/kyc/cases/{created}/checks",
            json={"check_type": kind, "status": status, "engine": "izilens-bio", "version": "0.1"},
            headers=super_admin,
        )

    assert (
        client.post(
            f"{ADMIN}/kyc/cases/{created}/checks", json={"check_type": "face_match", "status": "passed"}, headers=platform
        ).status_code
        == 403
    )
    assert check("face_match", "passed").json()["status_reason"] == "AWAITING_LIVENESS"
    failed = check("liveness", "failed").json()
    assert (failed["status"], failed["status_reason"]) == ("manual_review", "REVIEW_REQUIRED") and "LIVENESS_FAILED" in codes(
        failed
    )
    refused = client.post(
        f"{CASES}/{created}/decision",
        json={"decision": "approved", "reason": "Vu en visioconférence avec le client"},
        headers=org["reviewer"],
    )
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "REQUIRED_CHECKS_NOT_SATISFIED"
    no_exception = client.post(
        f"{ADMIN}/kyc/cases/{created}/decision",
        json={"decision": "approved", "reason": "Exception formelle accordée"},
        headers=platform,
    )
    assert no_exception.status_code == 422
    formal = client.post(
        f"{ADMIN}/kyc/cases/{created}/decision",
        json={"decision": "approved", "reason": "Exception formelle accordée", "exception": True},
        headers=platform,
    )
    assert formal.status_code == 200 and formal.json()["status"] == "verified"
    events = [e["event_type"] for e in client.get(f"{CASES}/{created}/timeline", headers=org["admin"]).json()]
    assert "exception_granted" in events and "check_recorded" in events


def test_biometric_results_complete_the_flow_without_changing_the_document_data(client, org, super_admin):
    patch_journey(
        client,
        super_admin,
        required_checks=[
            "document_quality",
            "document_recognition",
            "ocr_extraction",
            "declared_match",
            "face_match",
            "liveness",
        ],
        auto_decision_enabled=True,
    )
    created = submit(client, org["api_key"], front=make_image(94)).json()["id"]
    before = case(client, org["api_key"], created)["extracted"]
    for kind in ("face_match", "liveness"):
        response = client.post(
            f"{ADMIN}/kyc/cases/{created}/checks", json={"check_type": kind, "status": "passed"}, headers=super_admin
        )
        assert response.status_code == 200
    final = case(client, org["api_key"], created)
    assert (final["status"], final["status_reason"]) == ("verified", "VERIFIED_AUTOMATIC") and final["extracted"] == before
    assert {"face_match", "liveness"} <= set(final["scope"]["executed_checks"])
    late = client.post(
        f"{ADMIN}/kyc/cases/{created}/checks", json={"check_type": "liveness", "status": "passed"}, headers=super_admin
    )
    assert late.status_code == 409
