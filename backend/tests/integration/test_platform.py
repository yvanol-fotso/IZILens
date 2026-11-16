import uuid

from tests.conftest import PASSWORD


def test_health_endpoints_and_security_headers(client):
    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/health/ready")
    assert ready.status_code == 200 and ready.json() == {"status": "ready"}
    headers = client.get("/health").headers
    assert headers["x-content-type-options"] == "nosniff" and headers["x-frame-options"] == "DENY"
    assert headers["cache-control"] == "no-store" and len(headers["x-request-id"]) >= 8


def test_request_id_is_echoed_and_present_in_errors(client):
    response = client.get("/api/v1/kyc/cases", headers={"X-Request-ID": "trace-abc-12345"})
    assert response.status_code == 401
    assert response.headers["x-request-id"] == "trace-abc-12345"
    assert response.json()["error"] == {
        "code": "AUTHENTICATION_REQUIRED",
        "message": "Authentification requise",
        "request_id": "trace-abc-12345",
    }


def test_validation_errors_do_not_echo_input(client):
    response = client.post("/api/v1/auth/login", json={"email": "not-an-email", "password": "SECRET-VALUE"})
    assert response.status_code == 422 and "SECRET-VALUE" not in response.text


def test_oversized_request_rejected_early(client):
    response = client.post(
        "/api/v1/auth/login", content=b"x", headers={"content-length": str(50 * 1024 * 1024), "content-type": "application/json"}
    )
    assert response.status_code == 413


def test_login_refresh_me_and_change_password(client, org):
    login = client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": PASSWORD}).json()
    assert login["token_type"] == "bearer" and login["expires_in"] == 1800
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert refreshed.status_code == 200
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": login["access_token"]}).status_code == 401
    me = client.get("/api/v1/auth/me", headers=org["admin"]).json()
    assert me["email"] == "admin@alpha.com" and "password_hash" not in me
    weak = client.post(
        "/api/v1/auth/change-password", json={"current_password": PASSWORD, "new_password": "short"}, headers=org["admin"]
    )
    assert weak.status_code == 422
    ok = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "NewSecretPass2026"},
        headers=org["admin"],
    )
    assert ok.status_code == 204
    assert client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": PASSWORD}).status_code == 401
    assert (
        client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": "NewSecretPass2026"}).status_code == 200
    )


def test_oauth2_form_login_used_by_swagger(client, org):
    response = client.post("/api/v1/auth/token", data={"username": "admin@alpha.com", "password": PASSWORD})
    assert response.status_code == 200 and response.json()["access_token"]


def test_wrong_credentials_are_indistinguishable(client, org):
    unknown = client.post("/api/v1/auth/login", json={"email": "ghost@alpha.com", "password": "WhateverPass123"})
    wrong = client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": "WhateverPass123"})
    assert (
        unknown.status_code == wrong.status_code == 401 and unknown.json()["error"]["message"] == wrong.json()["error"]["message"]
    )


def test_account_locks_after_repeated_failures(client, org):
    for _ in range(5):
        assert (
            client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": "BadPassword123"}).status_code == 401
        )
    assert client.post("/api/v1/auth/login", json={"email": "admin@alpha.com", "password": PASSWORD}).status_code == 401
    assert client.get("/api/v1/auth/me", headers=org["admin"]).status_code == 401


def test_login_rate_limit(client, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "rate_limit_login_per_minute", 3)
    statuses = [client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "x"}).status_code for _ in range(5)]
    assert statuses[:3] == [401, 401, 401] and statuses[3:] == [429, 429]


def test_only_super_admin_manages_organizations(client, org, super_admin):
    payload = {"name": "Beta", "slug": "beta"}
    assert client.post("/api/v1/organizations", json=payload, headers=org["admin"]).status_code == 403
    assert client.post("/api/v1/organizations", json=payload, headers=super_admin).status_code == 201
    assert client.post("/api/v1/organizations", json=payload, headers=super_admin).status_code == 409
    assert client.post("/api/v1/organizations", json={"name": "X", "slug": "Bad Slug!"}, headers=super_admin).status_code == 422
    assert (
        client.post(
            "/api/v1/organizations", json={"name": "Gamma", "slug": "gamma", "enabled_modules": ["nope"]}, headers=super_admin
        ).status_code
        == 422
    )
    listing = client.get("/api/v1/organizations", headers=super_admin).json()
    assert listing["total"] == 2
    assert client.get("/api/v1/organizations/me", headers=org["admin"]).json()["slug"] == "alpha"


def test_admin_creates_users_only_in_own_organization(client, org, make_org):
    other = make_org("beta")
    body = {
        "email": "New.User@alpha.com",
        "full_name": "New User",
        "password": "ValidPassword123",
        "role": "reviewer",
        "organization_id": other["organization"]["id"],
    }
    created = client.post("/api/v1/users", json=body, headers=org["admin"])
    assert created.status_code == 201
    assert created.json()["organization_id"] == org["organization"]["id"] and created.json()["email"] == "new.user@alpha.com"
    assert client.post("/api/v1/users", json=body, headers=org["admin"]).status_code == 409
    assert (
        client.post(
            "/api/v1/users", json={**body, "email": "x@alpha.com", "role": "super_admin"}, headers=org["admin"]
        ).status_code
        == 422
    )
    assert client.post("/api/v1/users", json={**body, "email": "y@alpha.com"}, headers=org["reviewer"]).status_code == 403
    users = client.get("/api/v1/users", headers=org["admin"]).json()
    assert all(u["organization_id"] == org["organization"]["id"] for u in users["items"])


def test_admin_cannot_deactivate_self_or_foreign_user_and_deactivation_blocks_access(client, org, make_org):
    me = client.get("/api/v1/auth/me", headers=org["admin"]).json()
    assert client.patch(f"/api/v1/users/{me['id']}/status", json={"is_active": False}, headers=org["admin"]).status_code == 403
    foreign = make_org("beta")
    foreign_id = client.get("/api/v1/auth/me", headers=foreign["reviewer"]).json()["id"]
    assert client.patch(f"/api/v1/users/{foreign_id}/status", json={"is_active": False}, headers=org["admin"]).status_code == 404
    reviewer_id = client.get("/api/v1/auth/me", headers=org["reviewer"]).json()["id"]
    assert client.patch(f"/api/v1/users/{reviewer_id}/status", json={"is_active": False}, headers=org["admin"]).status_code == 200
    assert client.get("/api/v1/auth/me", headers=org["reviewer"]).status_code == 401


def test_api_key_lifecycle(client, org):
    listing = client.get("/api/v1/api-keys", headers=org["admin"]).json()
    assert len(listing) == 1 and "key" not in listing[0] and "key_hash" not in listing[0]
    assert client.get("/api/v1/kyc/cases", headers=org["api_key"]).status_code == 200
    assert client.get("/api/v1/kyc/cases", headers={"X-API-Key": "izl_test_deadbeef_wrongwrongwrong"}).status_code == 401
    assert client.get("/api/v1/kyc/cases", headers={"X-API-Key": "garbage"}).status_code == 401
    assert client.post("/api/v1/api-keys", json={"name": "k"}, headers=org["reviewer"]).status_code == 403
    assert client.post("/api/v1/api-keys", json={"name": "k"}, headers=org["api_key"]).status_code == 403
    assert client.delete(f"/api/v1/api-keys/{org['api_key_id']}", headers=org["admin"]).status_code == 200
    assert client.get("/api/v1/kyc/cases", headers=org["api_key"]).status_code == 401


def test_api_key_of_disabled_organization_or_expired_key_is_rejected(client, org, super_admin):
    short = client.post("/api/v1/api-keys", json={"name": "short", "expires_in_days": 1}, headers=org["admin"]).json()
    assert client.get("/api/v1/kyc/cases", headers={"X-API-Key": short["key"]}).status_code == 200
    assert (
        client.patch(
            f"/api/v1/organizations/{org['organization']['id']}", json={"is_active": False}, headers=super_admin
        ).status_code
        == 200
    )
    assert client.get("/api/v1/kyc/cases", headers=org["api_key"]).status_code == 401
    assert client.get("/api/v1/kyc/cases", headers=org["admin"]).status_code == 403


def test_module_not_enabled_blocks_kyc(client, make_org):
    nokyc = make_org("nokyc", modules=["kyb"])
    response = client.get("/api/v1/kyc/cases", headers=nokyc["api_key"])
    assert response.status_code == 403 and response.json()["error"]["code"] == "MODULE_NOT_ENABLED"


def test_super_admin_has_no_access_to_tenant_data(client, super_admin):
    assert client.get("/api/v1/kyc/cases", headers=super_admin).status_code == 403
    assert client.get("/api/v1/api-keys", headers=super_admin).status_code == 403


def test_audit_logs_scoped_by_organization(client, org, make_org, super_admin):
    other = make_org("beta")
    mine = client.get("/api/v1/audit-logs", headers=org["admin"]).json()
    assert mine["total"] > 0 and all(item["organization_id"] == org["organization"]["id"] for item in mine["items"])
    assert {"api_key.created", "auth.login_succeeded"} <= {item["action"] for item in mine["items"]}
    assert client.get("/api/v1/audit-logs", headers=org["reviewer"]).status_code == 403
    everything = client.get("/api/v1/audit-logs?page_size=200", headers=super_admin).json()
    assert {item["organization_id"] for item in everything["items"]} >= {org["organization"]["id"], other["organization"]["id"]}
    assert uuid.UUID(mine["items"][0]["id"])
