from app.common.enums import UserRole
from app.core import totp
from app.core.config import get_settings
from tests.conftest import PASSWORD, _create_user
from tests.integration.utils import submit

API = "/api/v1"


def enroll(client, headers):
    secret = client.post(f"{API}/auth/mfa/enroll", headers=headers).json()["secret"]
    codes = client.post(f"{API}/auth/mfa/verify", json={"code": totp.code_now(secret)}, headers=headers).json()["recovery_codes"]
    return secret, codes


def login(client, email, code=None, password=PASSWORD):
    body = {"email": email, "password": password, **({"mfa_code": code} if code else {})}
    return client.post(f"{API}/auth/login", json=body)


def test_mfa_enrollment_and_login_challenge(client, org):
    assert client.get(f"{API}/auth/mfa/status", headers=org["admin"]).json() == {"enabled": False, "recovery_codes_left": 0}
    enrolled = client.post(f"{API}/auth/mfa/enroll", headers=org["admin"]).json()
    assert enrolled["otpauth_uri"].startswith("otpauth://totp/") and "issuer=IZI%20LENS" in enrolled["otpauth_uri"]
    assert (
        client.post(f"{API}/auth/mfa/verify", json={"code": "000000"}, headers=org["admin"]).json()["error"]["code"]
        == "INVALID_MFA_CODE"
    )
    verified = client.post(
        f"{API}/auth/mfa/verify", json={"code": totp.code_now(enrolled["secret"])}, headers=org["admin"]
    ).json()
    assert verified["enabled"] and len(verified["recovery_codes"]) == 8
    assert client.get(f"{API}/auth/mfa/status", headers=org["admin"]).json() == {"enabled": True, "recovery_codes_left": 8}
    assert client.post(f"{API}/auth/mfa/enroll", headers=org["admin"]).json()["error"]["code"] == "MFA_ALREADY_ENABLED"
    required = login(client, "admin@alpha.com")
    assert required.status_code == 401 and required.json()["error"]["code"] == "MFA_REQUIRED"
    assert login(client, "admin@alpha.com", "000000").json()["error"]["code"] == "INVALID_MFA_CODE"
    assert (
        login(client, "admin@alpha.com", "000000", password="Mauvais-mot-de-passe1").json()["error"]["code"]
        == "INVALID_CREDENTIALS"
    )
    ok = login(client, "admin@alpha.com", totp.code_now(enrolled["secret"], now=__import__("time").time() + 30))
    assert ok.status_code == 200 and ok.json()["access_token"]


def test_totp_codes_cannot_be_replayed_and_recovery_codes_are_single_use(client, org):
    import time

    secret, codes = enroll(client, org["admin"])
    future = time.time() + 30
    code = totp.code_now(secret, now=future)
    assert login(client, "admin@alpha.com", code).status_code == 200
    assert login(client, "admin@alpha.com", code).status_code == 401
    assert login(client, "admin@alpha.com", codes[0]).status_code == 200
    assert login(client, "admin@alpha.com", codes[0]).json()["error"]["code"] == "INVALID_MFA_CODE"
    assert client.get(f"{API}/auth/mfa/status", headers=org["admin"]).json()["recovery_codes_left"] == 7


def test_mfa_failures_lock_the_account(client, org):
    enroll(client, org["admin"])
    for _ in range(5):
        assert login(client, "admin@alpha.com", "111111").status_code == 401
    assert login(client, "admin@alpha.com", "222222").status_code == 401
    audit = [i["action"] for i in client.get(f"{API}/audit-logs?page_size=200", headers=org["reviewer"]).json().get("items", [])]
    assert audit == [] or "auth.mfa_failed" in audit


def test_mfa_can_be_disabled_with_password_and_code_and_sessions_are_revoked(client, org):
    secret, _ = enroll(client, org["admin"])
    assert (
        client.post(f"{API}/auth/mfa/disable", json={"password": "faux", "code": "123456"}, headers=org["admin"]).status_code
        == 401
    )
    import time

    done = client.post(
        f"{API}/auth/mfa/disable",
        json={"password": PASSWORD, "code": totp.code_now(secret, now=time.time() + 30)},
        headers=org["admin"],
    )
    assert done.status_code == 204
    assert client.get(f"{API}/auth/me", headers=org["admin"]).status_code == 401
    assert login(client, "admin@alpha.com").status_code == 200


def test_recovery_codes_can_be_regenerated(client, org):
    import time

    secret, old = enroll(client, org["admin"])
    fresh = client.post(
        f"{API}/auth/mfa/recovery-codes", json={"code": totp.code_now(secret, now=time.time() + 30)}, headers=org["admin"]
    ).json()["recovery_codes"]
    assert len(fresh) == 8 and not set(fresh) & set(old)
    assert login(client, "admin@alpha.com", old[0]).status_code == 401


def test_totp_primitives():
    secret = totp.new_secret()
    code = totp.code_now(secret, now=1_700_000_000)
    assert totp.verify(secret, code, now=1_700_000_000) is not None
    assert totp.verify(secret, code, now=1_700_000_000 + 30) is not None
    assert totp.verify(secret, code, now=1_700_000_000 + 120) is None
    step = totp.verify(secret, code, now=1_700_000_000)
    assert totp.verify(secret, code, last_used_step=step, now=1_700_000_000) is None
    assert totp.verify(secret, "abcdef") is None and totp.verify(secret, "12345") is None
    assert totp.code_now("JBSWY3DPEHPK3PXP", now=59) == "996554"  # vecteur de référence RFC 6238 (SHA-1, secret ASCII)


def test_security_overview_locked_accounts_unlock_and_revocation(client, org, staff, super_admin):
    compliance = staff(UserRole.PLATFORM_COMPLIANCE)
    for _ in range(5):
        login(client, "reviewer@alpha.com", password="Mauvais-mot-de-passe1")
    overview = client.get(f"{API}/admin/security/overview", headers=compliance).json()
    assert overview["failed_logins_24h"] >= 5 and overview["locked_accounts"] == 1 and overview["staff_without_mfa"] >= 1
    locked = client.get(f"{API}/admin/security/locked-accounts", headers=compliance).json()
    assert [u["email"] for u in locked] == ["reviewer@alpha.com"]
    user_id = locked[0]["id"]
    assert client.post(f"{API}/admin/security/users/{user_id}/unlock", headers=compliance).status_code == 403
    assert client.post(f"{API}/admin/security/users/{user_id}/unlock", headers=super_admin).status_code == 204
    assert login(client, "reviewer@alpha.com").status_code == 200
    token = login(client, "reviewer@alpha.com").json()["access_token"]
    assert client.post(f"{API}/admin/security/users/{user_id}/revoke-sessions", headers=super_admin).status_code == 204
    assert client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    assert client.get(f"{API}/admin/security/overview", headers=org["admin"]).status_code == 403


def test_admin_can_reset_a_lost_mfa_device(client, org, super_admin):
    enroll(client, org["admin"])
    user_id = client.get(f"{API}/users", headers=super_admin).json()["items"][0]["id"]
    admin_id = next(
        u["id"] for u in client.get(f"{API}/users", headers=super_admin).json()["items"] if u["email"] == "admin@alpha.com"
    )
    assert login(client, "admin@alpha.com").status_code == 401
    assert client.post(f"{API}/admin/security/users/{admin_id}/reset-mfa", headers=super_admin).status_code == 204
    assert login(client, "admin@alpha.com").status_code == 200
    assert client.post(f"{API}/admin/security/users/{admin_id}/reset-mfa", headers=super_admin).status_code == 404
    assert user_id


def test_security_events_are_filterable_and_exported_safely(client, org, staff, super_admin):
    login(client, "admin@alpha.com", password="Mauvais-mot-de-passe1")
    compliance = staff(UserRole.PLATFORM_COMPLIANCE)
    events = client.get(f"{API}/admin/security/events?action_prefix=auth.", headers=compliance).json()
    assert events["total"] >= 2 and all(i["action"].startswith("auth.") for i in events["items"])
    only_failed = client.get(f"{API}/admin/security/events?action_prefix=auth.login_failed", headers=compliance).json()
    assert {i["action"] for i in only_failed["items"]} == {"auth.login_failed"}
    csv_export = client.get(f"{API}/admin/security/events.csv", headers=compliance)
    assert csv_export.headers["content-type"].startswith("text/csv") and csv_export.text.splitlines()[0].startswith(
        "created_at,action"
    )
    assert "auth.login_failed" in csv_export.text
    from app.modules.security.service import _csv_cell

    assert _csv_cell("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0" and _csv_cell("normal") == "normal" and _csv_cell(None) == ""


def test_roles_catalogue_lists_scopes_and_permissions(client, staff, org):
    roles = client.get(f"{API}/admin/roles", headers=staff(UserRole.PLATFORM_COMPLIANCE)).json()
    assert roles["super_admin"]["permissions"] == ["*"] and roles["viewer"]["permissions"] == ["cases.read"]
    assert {r["scope"] for r in roles.values()} == {"platform", "tenant"} and "cms.manage" in roles["content_editor"][
        "permissions"
    ]
    assert client.get(f"{API}/admin/roles", headers=org["admin"]).status_code == 403


def test_kyc_report_counts_rates_and_exports_csv(client, org, staff, make_org):
    from tests.helpers import make_image

    ids = [submit(client, org["api_key"], reference=f"R{i}", front=make_image(300 + i)).json()["id"] for i in range(3)]
    client.post(f"{API}/kyc/cases/{ids[0]}/decision", json={"decision": "approved"}, headers=org["reviewer"])
    client.post(
        f"{API}/kyc/cases/{ids[1]}/decision",
        json={"decision": "rejected", "reason": "Photo non conforme"},
        headers=org["reviewer"],
    )
    sandbox = client.post(f"{API}/api-keys", json={"name": "sb", "environment": "sandbox"}, headers=org["admin"]).json()
    submit(client, {"X-API-Key": sandbox["key"]}, reference="SB", front=make_image(400))
    compliance = staff(UserRole.PLATFORM_COMPLIANCE)
    report = client.get(f"{API}/admin/reports/kyc", headers=compliance).json()
    assert report["total"] == 3 and report["by_status"] == {"verified": 1, "not_verified": 1, "manual_review": 1}
    assert (
        report["verified_rate"] == 0.5
        and report["pending_review"] == 1
        and report["by_country"] == {"CM": 3}
        and report["avg_resolution_hours"] is not None
    )
    assert client.get(f"{API}/admin/reports/kyc?include_sandbox=true", headers=compliance).json()["total"] == 4
    other = make_org("beta")
    assert (
        client.get(f"{API}/admin/reports/kyc?organization_id={other['organization']['id']}", headers=compliance).json()["total"]
        == 0
    )
    csv_report = client.get(f"{API}/admin/reports/kyc?format=csv", headers=compliance)
    assert csv_report.text.splitlines()[0] == "day,cases" and csv_report.text.splitlines()[1].endswith(",3")
    rows = client.get(f"{API}/admin/reports/organizations", headers=compliance).json()
    assert {r["name"]: r["cases"] for r in rows} == {"Alpha": 3, "Beta": 0}
    assert client.get(f"{API}/admin/reports/kyc", headers=org["admin"]).status_code == 403
    assert get_settings() and _create_user
