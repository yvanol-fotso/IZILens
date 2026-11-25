import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.common.enums import UserRole
from app.core.config import get_settings
from app.modules.auth import oidc
from tests.conftest import PASSWORD, _create_user

CLIENT_ID = "client-123.apps.googleusercontent.com"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
GOOGLE = "/api/v1/auth/oidc/google"


class FakeResolver:
    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=KEY.public_key())


@pytest.fixture(autouse=True)
def google(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "oidc_enabled", True)
    monkeypatch.setattr(settings, "google_client_id", CLIENT_ID)
    monkeypatch.setattr(settings, "google_client_secret", "secret")
    monkeypatch.setattr(settings, "oidc_allowed_redirect_uris", ["http://localhost:5173/auth/callback"])
    oidc.set_key_resolver(FakeResolver())
    yield
    oidc.set_key_resolver(None)


def token(email="invite@alpha.com", sub="google-sub-1", key=KEY, **overrides):
    now = int(time.time())
    claims = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "sub": sub,
        "email": email,
        "email_verified": True,
        "iat": now,
        "exp": now + 600,
        **overrides,
    }
    return jwt.encode({k: v for k, v in claims.items() if v is not None}, key, algorithm="RS256")


def login(client, **kwargs):
    nonce = kwargs.pop("nonce", None)
    return client.post(f"{GOOGLE}/token", json={"id_token": token(**kwargs), **({"nonce": nonce} if nonce else {})})


def provision(org, **kwargs):
    import uuid

    return _create_user(
        kwargs.get("email", "invite@alpha.com"),
        kwargs.get("role", UserRole.REVIEWER),
        uuid.UUID(org["organization"]["id"]),
        kwargs.get("password"),
    )


def test_providers_endpoint_reports_availability(client, monkeypatch):
    assert client.get("/api/v1/auth/oidc/providers").json() == {"google": {"enabled": True, "client_id": CLIENT_ID}}
    monkeypatch.setattr(get_settings(), "oidc_enabled", False)
    assert client.get("/api/v1/auth/oidc/providers").json() == {"google": {"enabled": False, "client_id": None}}


def test_invited_user_signs_in_with_google_without_password(client, org):
    provision(org)
    response = login(client)
    assert response.status_code == 200
    tokens = response.json()
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}).json()
    assert me["email"] == "invite@alpha.com" and me["role"] == "reviewer" and me["organization_id"] == org["organization"]["id"]
    assert client.post("/api/v1/auth/login", json={"email": "invite@alpha.com", "password": PASSWORD}).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 200


def test_identity_is_bound_to_the_google_subject(client, org):
    provision(org)
    assert login(client).status_code == 200
    assert login(client, sub="another-subject").json()["error"]["code"] == "IDENTITY_MISMATCH"
    assert login(client).status_code == 200


def test_unknown_accounts_are_not_created_automatically(client, org):
    response = login(client, email="stranger@evil.com", sub="s2")
    assert response.status_code == 403 and response.json()["error"]["code"] == "ACCOUNT_NOT_PROVISIONED"


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"aud": "someone-else"}, "INVALID_ID_TOKEN"),
        ({"iss": "https://evil.example"}, "INVALID_ID_TOKEN"),
        ({"exp": int(time.time()) - 60}, "INVALID_ID_TOKEN"),
        ({"email_verified": False}, "EMAIL_NOT_VERIFIED"),
        ({"email": None}, "EMAIL_NOT_VERIFIED"),
    ],
)
def test_invalid_google_tokens_are_rejected(client, org, overrides, code):
    provision(org)
    response = login(client, **overrides)
    assert response.status_code == 401 and response.json()["error"]["code"] == code


def test_forged_signature_and_wrong_nonce_are_rejected(client, org):
    provision(org)
    assert login(client, key=OTHER_KEY).json()["error"]["code"] == "INVALID_ID_TOKEN"
    mismatch = client.post(f"{GOOGLE}/token", json={"id_token": token(nonce="abc12345"), "nonce": "different1"})
    assert mismatch.status_code == 401
    assert client.post(f"{GOOGLE}/token", json={"id_token": token(nonce="abc12345"), "nonce": "abc12345"}).status_code == 200


def test_inactive_user_or_disabled_organization_cannot_sign_in(client, org, super_admin):
    user_id = provision(org)
    client.patch(f"/api/v1/users/{user_id}/status", json={"is_active": False}, headers=org["admin"])
    assert login(client).status_code == 401
    client.patch(f"/api/v1/users/{user_id}/status", json={"is_active": True}, headers=org["admin"])
    client.patch(f"/api/v1/organizations/{org['organization']['id']}", json={"is_active": False}, headers=super_admin)
    assert login(client).status_code == 401


def test_feature_can_be_switched_off(client, org, monkeypatch):
    provision(org)
    monkeypatch.setattr(get_settings(), "oidc_enabled", False)
    response = login(client)
    assert response.status_code == 403 and response.json()["error"]["code"] == "OIDC_DISABLED"


def test_password_is_optional_only_when_oidc_is_enabled(client, org, monkeypatch):
    body = {"email": "oidc.only@alpha.com", "full_name": "Oidc Only", "role": "reviewer"}
    assert client.post("/api/v1/users", json=body, headers=org["admin"]).status_code == 201
    monkeypatch.setattr(get_settings(), "oidc_enabled", False)
    refused = client.post("/api/v1/users", json={**body, "email": "other@alpha.com"}, headers=org["admin"])
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "PASSWORD_REQUIRED"


def test_authorization_code_flow_with_pkce(client, org):
    provision(org)
    query = {
        "redirect_uri": "http://localhost:5173/auth/callback",
        "state": "state-12345",
        "nonce": "nonce-12345",
        "code_challenge": "c" * 43,
    }
    url = client.get(f"{GOOGLE}/authorize", params=query).json()["authorization_url"]
    parts = parse_qs(urlsplit(url).query)
    assert (
        url.startswith("https://accounts.google.com/")
        and parts["code_challenge_method"] == ["S256"]
        and parts["client_id"] == [CLIENT_ID]
    )
    assert (
        client.get(f"{GOOGLE}/authorize", params={**query, "redirect_uri": "https://evil.example/cb"}).json()["error"]["code"]
        == "REDIRECT_URI_NOT_ALLOWED"
    )


def test_code_exchange_then_login(client, org, monkeypatch):
    provision(org)
    seen = {}

    def handler(request):
        seen["body"] = parse_qs(request.content.decode())
        return httpx.Response(200, json={"id_token": token(nonce="nonce-12345")})

    real = httpx.Client
    monkeypatch.setattr(oidc.httpx, "Client", lambda **_: real(transport=httpx.MockTransport(handler)))
    body = {
        "code": "auth-code-1",
        "redirect_uri": "http://localhost:5173/auth/callback",
        "code_verifier": "v" * 50,
        "nonce": "nonce-12345",
    }
    response = client.post(f"{GOOGLE}/callback", json=body)
    assert (
        response.status_code == 200
        and seen["body"]["code_verifier"] == ["v" * 50]
        and seen["body"]["grant_type"] == ["authorization_code"]
    )
    assert client.post(f"{GOOGLE}/callback", json={**body, "redirect_uri": "https://evil.example/cb"}).status_code == 422


def test_failed_code_exchange_is_reported(client, org, monkeypatch):
    provision(org)
    real = httpx.Client
    monkeypatch.setattr(
        oidc.httpx,
        "Client",
        lambda **_: real(transport=httpx.MockTransport(lambda r: httpx.Response(400, json={"error": "invalid_grant"}))),
    )
    body = {"code": "auth-code-1", "redirect_uri": "http://localhost:5173/auth/callback", "code_verifier": "v" * 50}
    assert client.post(f"{GOOGLE}/callback", json=body).json()["error"]["code"] == "OIDC_EXCHANGE_FAILED"


def test_oidc_logins_are_audited(client, org):
    provision(org)
    login(client)
    actions = [i["action"] for i in client.get("/api/v1/audit-logs?page_size=200", headers=org["admin"]).json()["items"]]
    assert "auth.oidc_login_succeeded" in actions


def test_platform_staff_can_be_invited_for_google_sign_in(client, super_admin):
    body = {"email": "staff@izilens.com", "full_name": "Staff Conformité", "role": "platform_compliance"}
    assert client.post("/api/v1/users", json=body, headers=super_admin).status_code == 201
    assert login(client, email="staff@izilens.com", sub="staff-sub").status_code == 200


def test_dashboard_alias_route_uses_the_same_verification(client, org):
    provision(org)
    ok = client.post("/api/v1/auth/oauth/google", json={"id_token": token(), "nonce": None})
    assert ok.status_code == 200 and ok.json()["access_token"]
    forged = client.post("/api/v1/auth/oauth/google", json={"id_token": token(key=OTHER_KEY)})
    assert forged.status_code == 401 and forged.json()["error"]["code"] == "INVALID_ID_TOKEN"
    stranger = client.post("/api/v1/auth/oauth/google", json={"id_token": token(email="stranger@evil.com", sub="s9")})
    assert stranger.status_code == 403 and stranger.json()["error"]["code"] == "ACCOUNT_NOT_PROVISIONED"
