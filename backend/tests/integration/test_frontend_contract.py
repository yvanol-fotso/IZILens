"""Contrat attendu par le dashboard SvelteKit (docs/BACKEND_CONTRACT.md) : chaque appel du front doit aboutir."""

from app.common.enums import UserRole
from tests.conftest import PASSWORD, _create_user, _login, outbox
from tests.helpers import make_image
from tests.integration.utils import CASES, case, submit

API = "/api/v1"


def test_health_is_available_under_the_api_prefix(client):
    assert client.get(f"{API}/health").json() == {"status": "ok"}


def test_registration_creates_an_account_without_rights_and_never_reveals_existing_emails(client, org):
    body = {"full_name": "Nouvel Utilisateur", "email": "Nouveau@Example.com", "password": "Motdepasse2026!"}
    assert client.post(f"{API}/auth/register", json=body).status_code == 202
    assert client.post(f"{API}/auth/register", json=body).status_code == 202
    assert client.post(f"{API}/auth/register", json={**body, "email": "admin@alpha.com"}).status_code == 202
    assert client.post(f"{API}/auth/register", json={**body, "password": "short"}).status_code == 422
    headers = _login(client, "nouveau@example.com", "Motdepasse2026!")
    me = client.get(f"{API}/auth/me", headers=headers).json()
    assert me["role"] == "viewer" and me["organization_id"] is None
    refused = client.get(CASES, headers=headers)
    assert refused.status_code == 403 and refused.json()["error"]["code"] == "ORGANIZATION_REQUIRED"
    assert client.post(f"{API}/auth/login", json={"email": "admin@alpha.com", "password": "Motdepasse2026!"}).status_code == 401


def test_logout_is_accepted_and_audited(client, org):
    assert client.post(f"{API}/auth/logout", headers=org["admin"]).status_code == 204
    assert client.post(f"{API}/auth/logout").status_code == 401
    actions = [i["action"] for i in client.get(f"{API}/audit-logs?page_size=200", headers=org["admin"]).json()["items"]]
    assert "auth.logout" in actions


def test_case_list_accepts_the_page_size_and_filters_used_by_the_dashboard(client, org):
    created = submit(client, org["api_key"], reference="DASH-1").json()["id"]
    submit(client, org["api_key"], reference="OTHER-2", front=make_image(77))
    assert client.get(f"{CASES}?page_size=200&limit=200", headers=org["viewer"]).json()["total"] == 2
    assert client.get(f"{CASES}?search=DASH", headers=org["viewer"]).json()["items"][0]["id"] == created
    assert client.get(f"{CASES}?search={created[:8]}", headers=org["viewer"]).json()["total"] == 1
    assert client.get(f"{CASES}?risk_level=high", headers=org["viewer"]).json()["total"] == 0
    assert client.get(f"{CASES}?risk_level=low", headers=org["viewer"]).json()["total"] >= 1
    assert client.get(f"{CASES}?risk_level=bogus", headers=org["viewer"]).status_code == 422
    assert client.get(f"{CASES}?page_size=201", headers=org["viewer"]).status_code == 422


def test_case_detail_keeps_the_fields_read_by_the_dashboard(client, org):
    detail = case(client, org["api_key"], submit(client, org["api_key"]).json()["id"])
    assert (
        detail["extracted_data"]["surname"] == "Atángana Mohammadou" and detail["extracted_data"]["date_of_birth"] == "1992-06-15"
    )
    assert all(set(d) >= {"id", "side"} for d in detail["documents"]) and isinstance(detail["flags"], list)
    assert {"status", "risk_level", "ocr_confidence", "reference", "created_at"} <= set(detail)


def test_organization_creation_with_admin_email_invites_the_administrator(client, super_admin):
    body = {
        "name": "Banque Alpha",
        "slug": "banque-alpha",
        "enabled_modules": ["kyc", "liveness", "aml", "api"],
        "admin_email": "directeur@banque-alpha.com",
    }
    created = client.post(f"{API}/organizations", json=body, headers=super_admin)
    assert created.status_code == 201 and created.json()["enabled_modules"] == ["aml", "api", "kyc", "liveness"]
    users = client.get(f"{API}/users?organization_id={created.json()['id']}", headers=super_admin).json()["items"]
    assert [(u["email"], u["role"]) for u in users] == [("directeur@banque-alpha.com", "admin")]
    mail = next(m for m in outbox() if m["to"] == "directeur@banque-alpha.com")
    assert (
        mail["template"] == "account_invitation"
        and "Mot de passe temporaire" in mail["body"]
        and "Banque Alpha" in mail["subject"]
    )
    password = mail["body"].split("Mot de passe temporaire : ")[1].split(" ")[0]
    assert client.post(f"{API}/auth/login", json={"email": "directeur@banque-alpha.com", "password": password}).status_code == 200
    duplicate = client.post(f"{API}/organizations", json={**body, "slug": "autre-slug"}, headers=super_admin)
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "EMAIL_ALREADY_USED"
    assert client.get(f"{API}/organizations", headers=super_admin).json()["total"] == 1


def test_organization_default_modules_match_the_dashboard(client, super_admin):
    created = client.post(f"{API}/organizations", json={"name": "Défaut", "slug": "defaut"}, headers=super_admin).json()
    assert created["enabled_modules"] == ["kyc", "api"] and created["production_enabled"] is True


def test_user_update_roles_status_and_session_revocation(client, org, make_org):
    other = make_org("beta")
    reviewer = client.get(f"{API}/auth/me", headers=org["reviewer"]).json()["id"]
    changed = client.patch(f"{API}/users/{reviewer}", json={"role": "viewer", "full_name": "Nouveau Nom"}, headers=org["admin"])
    assert changed.status_code == 200 and (changed.json()["role"], changed.json()["full_name"]) == ("viewer", "Nouveau Nom")
    assert client.get(f"{API}/auth/me", headers=org["reviewer"]).status_code == 401
    admin_id = client.get(f"{API}/auth/me", headers=org["admin"]).json()["id"]
    assert client.patch(f"{API}/users/{admin_id}", json={"role": "viewer"}, headers=org["admin"]).status_code == 403
    foreign = client.get(f"{API}/auth/me", headers=other["reviewer"]).json()["id"]
    assert client.patch(f"{API}/users/{foreign}", json={"is_active": False}, headers=org["admin"]).status_code == 404
    assert client.patch(f"{API}/users/{reviewer}", json={"role": "platform_compliance"}, headers=org["admin"]).status_code == 403
    assert (
        client.patch(
            f"{API}/users/{reviewer}", json={"organization_id": other["organization"]["id"]}, headers=org["admin"]
        ).status_code
        == 403
    )
    assert client.patch(f"{API}/users/{reviewer}", json={"role": "super_admin"}, headers=org["admin"]).status_code == 422


def test_integration_role_is_assignable_and_profile_can_be_edited(client, org):
    body = {"email": "bot@alpha.com", "full_name": "Service Bot", "password": "Motdepasse2026!", "role": "integration"}
    created = client.post(f"{API}/users", json=body, headers=org["admin"])
    assert created.status_code == 201 and created.json()["role"] == "integration"
    token = _login(client, "bot@alpha.com", "Motdepasse2026!")
    assert client.get(CASES, headers=token).status_code == 200
    assert client.patch(f"{API}/users/me", json={"full_name": "Robot Alpha"}, headers=token).json()["full_name"] == "Robot Alpha"
    assert client.patch(f"{API}/users/me", json={"full_name": "x"}, headers=token).status_code == 422


def test_super_admin_attaches_a_self_registered_account_and_creates_staff(client, org, super_admin):
    client.post(
        f"{API}/auth/register", json={"full_name": "Jean Dupont", "email": "jean@example.com", "password": "Motdepasse2026!"}
    )
    users = client.get(f"{API}/users?page_size=200", headers=super_admin).json()["items"]
    jean = next(u for u in users if u["email"] == "jean@example.com")
    assert (
        client.patch(f"{API}/users/{jean['id']}", json={"role": "reviewer"}, headers=super_admin).json()["error"]["code"]
        == "ORGANIZATION_REQUIRED"
    )
    attached = client.patch(
        f"{API}/users/{jean['id']}", json={"organization_id": org["organization"]["id"], "role": "reviewer"}, headers=super_admin
    )
    assert attached.status_code == 200 and attached.json()["organization_id"] == org["organization"]["id"]
    staff_body = {"email": "editor@izilens.com", "full_name": "Éditeur", "password": "Motdepasse2026!", "role": "content_editor"}
    assert client.post(f"{API}/users", json=staff_body, headers=org["admin"]).status_code == 403
    created = client.post(f"{API}/users", json=staff_body, headers=super_admin)
    assert created.status_code == 201 and created.json()["organization_id"] is None


def test_user_lists_are_not_truncated_at_twenty(client, org):
    for i in range(23):
        _create_user(f"bulk{i}@alpha.com", UserRole.VIEWER, __import__("uuid").UUID(org["organization"]["id"]))
    assert client.get(f"{API}/users", headers=org["admin"]).json()["total"] == 26
    assert len(client.get(f"{API}/users", headers=org["admin"]).json()["items"]) == 26


def test_api_keys_return_the_environment(client, org):
    keys = client.get(f"{API}/api-keys", headers=org["admin"]).json()
    assert keys[0]["environment"] == "production" and PASSWORD
