from app.common.enums import UserRole
from tests.conftest import _login, outbox
from tests.integration.utils import CASES, submit

API = "/api/v1"
ACCESS = f"{API}/developers/access-requests"
ADMIN_ACCESS = f"{API}/admin/developers/access-requests"
BODY = {
    "environment": "sandbox",
    "company_name": "Fintech Kribi SARL",
    "country": "Cameroun",
    "use_case": "Vérifier l'identité des clients à l'ouverture de compte.",
    "expected_volume": "500/mois",
}


def register(client, email="dev@example.com"):
    client.post(f"{API}/auth/register", json={"full_name": "Dev Ouvert", "email": email, "password": "Motdepasse2026!"})
    return _login(client, email, "Motdepasse2026!")


def test_developer_journey_from_signup_to_sandbox_organization(client, staff):
    dev = register(client)
    assert client.get(f"{API}/developers/overview", headers=dev).json()["has_organization"] is False
    created = client.post(ACCESS, json=BODY, headers=dev)
    assert created.status_code == 201 and created.json()["status"] == "pending" and created.json()["reference"].startswith("DEV-")
    assert client.post(ACCESS, json=BODY, headers=dev).json()["error"]["code"] == "REQUEST_ALREADY_PENDING"
    assert len(client.get(ACCESS, headers=dev).json()) == 1
    sales = staff(UserRole.SALES_AGENT)
    pending = client.get(f"{ADMIN_ACCESS}?status=pending", headers=sales).json()
    assert pending["total"] == 1
    approved = client.post(f"{ADMIN_ACCESS}/{created.json()['id']}/decision", json={"decision": "approved"}, headers=sales)
    assert approved.status_code == 200 and approved.json()["organization_id"]
    assert client.get(f"{API}/auth/me", headers=dev).status_code == 401  # rôle modifié : nouvelle connexion requise
    dev = _login(client, "dev@example.com", "Motdepasse2026!")
    me = client.get(f"{API}/auth/me", headers=dev).json()
    assert me["role"] == "admin" and me["organization_id"] == approved.json()["organization_id"]
    organization = client.get(f"{API}/organizations/me", headers=dev).json()
    assert (
        organization["name"] == "Fintech Kribi SARL"
        and organization["production_enabled"] is False
        and organization["enabled_modules"] == ["kyc", "api"]
    )
    assert any(
        m["template"] == "access_decision" and m["to"] == "dev@example.com" and "approuvée" in m["subject"] for m in outbox()
    )
    assert client.post(ACCESS, json=BODY, headers=dev).json()["error"]["code"] == "ALREADY_HAS_ORGANIZATION"


def test_sandbox_keys_create_unbilled_sandbox_cases_and_production_is_refused(client, staff):
    dev = register(client)
    request_id = client.post(ACCESS, json=BODY, headers=dev).json()["id"]
    client.post(f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "approved"}, headers=staff(UserRole.SALES_AGENT))
    dev = _login(client, "dev@example.com", "Motdepasse2026!")
    key = client.post(f"{API}/api-keys", json={"name": "bac à sable"}, headers=dev).json()
    assert key["environment"] == "sandbox" and key["key"].startswith("izl_test_")
    assert (
        client.post(f"{API}/api-keys", json={"name": "prod", "environment": "production"}, headers=dev).json()["error"]["code"]
        == "PRODUCTION_ACCESS_REQUIRED"
    )
    api = {"X-API-Key": key["key"]}
    assert submit(client, api).status_code == 202
    usage = client.get(f"{API}/kyc/usage", headers=dev).json()
    assert all(u["billable"] is False for u in usage) and usage
    assert client.get(f"{API}/developers/overview", headers=dev).json()["api_keys"] == {"sandbox": 1, "production": 0}


def test_production_access_request_and_approval(client, staff):
    dev = register(client)
    request_id = client.post(ACCESS, json=BODY, headers=dev).json()["id"]
    sales = staff(UserRole.SALES_AGENT)
    client.post(f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "approved"}, headers=sales)
    dev = _login(client, "dev@example.com", "Motdepasse2026!")
    production = {**BODY, "environment": "production", "use_case": "Passage en production après recette complète."}
    created = client.post(ACCESS, json=production, headers=dev)
    assert created.status_code == 201 and created.json()["organization_id"]
    client.post(
        f"{ADMIN_ACCESS}/{created.json()['id']}/decision", json={"decision": "approved", "note": "Recette validée"}, headers=sales
    )
    assert client.get(f"{API}/organizations/me", headers=dev).json()["production_enabled"] is True
    key = client.post(f"{API}/api-keys", json={"name": "prod"}, headers=dev).json()
    assert key["environment"] == "production" and key["key"].startswith("izl_live_")
    assert submit(client, {"X-API-Key": key["key"]}).status_code == 202
    assert any(u["billable"] for u in client.get(f"{API}/kyc/usage", headers=dev).json())
    assert client.post(ACCESS, json=production, headers=dev).json()["error"]["code"] == "ALREADY_PRODUCTION"


def test_a_sandbox_key_stays_sandbox_even_when_production_is_enabled(client, org):
    sandbox = client.post(f"{API}/api-keys", json={"name": "sb", "environment": "sandbox"}, headers=org["admin"]).json()
    assert submit(client, {"X-API-Key": sandbox["key"]}, reference="SB-1").status_code == 202
    assert submit(client, org["api_key"], reference="LIVE-1").status_code == 202
    usage = client.get(f"{API}/kyc/usage", headers=org["admin"]).json()
    assert sum(u["events"] for u in usage if u["event_type"] == "case_created" and u["billable"]) == 1


def test_rejection_requires_a_reason_and_is_final(client, staff):
    dev = register(client)
    request_id = client.post(ACCESS, json=BODY, headers=dev).json()["id"]
    sales = staff(UserRole.SALES_AGENT)
    assert (
        client.post(f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "rejected"}, headers=sales).json()["error"]["code"]
        == "NOTE_REQUIRED"
    )
    rejected = client.post(
        f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "rejected", "note": "Activité hors périmètre"}, headers=sales
    )
    assert rejected.json()["status"] == "rejected"
    assert (
        client.post(f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "approved"}, headers=sales).json()["error"]["code"]
        == "INVALID_STATE"
    )
    assert client.get(f"{API}/auth/me", headers=dev).json()["organization_id"] is None
    assert client.post(ACCESS, json=BODY, headers=dev).status_code == 201


def test_access_rules_and_permissions(client, org, staff):
    assert client.post(ACCESS, json=BODY, headers=org["admin"]).json()["error"]["code"] == "ALREADY_HAS_ORGANIZATION"
    production = {**BODY, "environment": "production"}
    assert client.post(ACCESS, json=production, headers=org["reviewer"]).json()["error"]["code"] == "ORGANIZATION_ADMIN_REQUIRED"
    assert client.post(ACCESS, json=production, headers=org["admin"]).json()["error"]["code"] == "ALREADY_PRODUCTION"
    assert client.post(ACCESS, json={**BODY, "use_case": "court"}, headers=register(client)).status_code == 422
    assert client.get(f"{API}/developers/overview", headers=org["api_key"]).status_code == 403
    for headers in (org["admin"], staff(UserRole.CONTENT_EDITOR)):
        assert client.get(ADMIN_ACCESS, headers=headers).status_code == 403


def test_organization_slug_is_unique_when_derived(client, staff):
    sales = staff(UserRole.SALES_AGENT)
    slugs = []
    for i in range(2):
        dev = register(client, f"dev{i}@example.com")
        request_id = client.post(ACCESS, json=BODY, headers=dev).json()["id"]
        client.post(f"{ADMIN_ACCESS}/{request_id}/decision", json={"decision": "approved"}, headers=sales)
        slugs.append(_login(client, f"dev{i}@example.com", "Motdepasse2026!"))
    names = {client.get(f"{API}/organizations/me", headers=h).json()["slug"] for h in slugs}
    assert len(names) == 2 and CASES
