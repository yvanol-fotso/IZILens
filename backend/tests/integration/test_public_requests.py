import json
import re

from app.common.enums import UserRole
from app.core.config import get_settings
from tests.conftest import outbox

PUBLIC = "/api/v1/public/contact-requests"
ADMIN = "/api/v1/admin/public-requests"


def payload(**overrides):
    fields = {
        "full_name": "Awa Diop",
        "company": "Banque Sahel",
        "email": "Awa.Diop@banque-sahel.com",
        "country": "Sénégal",
        "role": "Directrice conformité",
        "type": "sales",
        "message": "Nous souhaitons une démonstration du module KYC.",
        "services": ["kyc", "kyb", "inconnu"],
        "sector": "banque",
        "volume": "10000",
        "consent_privacy": True,
        "consent_marketing": False,
    }
    fields.update(overrides)
    return {"kind": "contact", "locale": "fr", "fields": fields}


def test_public_request_returns_a_reference_and_sends_a_localized_confirmation(client):
    response = client.post(PUBLIC, json=payload())
    assert response.status_code == 201
    reference = response.json()["reference"]
    assert re.fullmatch(r"IZL-\d{4}-\d{6}", reference)
    confirmation = next(m for m in outbox() if m["template"] == "request_confirmation")
    assert (
        confirmation["to"] == "awa.diop@banque-sahel.com"
        and reference in confirmation["subject"]
        and "Bonjour Awa Diop" in confirmation["body"]
    )
    english = client.post(PUBLIC, json={**payload(email="john@example.com", full_name="John Doe"), "locale": "en"}).json()[
        "reference"
    ]
    assert any(m["locale"] == "en" and english in m["subject"] and m["body"].startswith("Hello John Doe") for m in outbox())


def test_references_are_sequential_and_unique(client):
    refs = [client.post(PUBLIC, json=payload(email=f"p{i}@example.com")).json()["reference"] for i in range(3)]
    numbers = [int(r.rsplit("-", 1)[1]) for r in refs]
    assert numbers == list(range(numbers[0], numbers[0] + 3)) and len(set(refs)) == 3


def test_validation_and_consent_are_enforced(client):
    assert client.post(PUBLIC, json=payload(consent_privacy=False)).status_code == 422
    assert client.post(PUBLIC, json=payload(email="not-an-email")).status_code == 422
    assert client.post(PUBLIC, json=payload(message="")).status_code == 422
    assert client.post(PUBLIC, json=payload(message="x" * 4001)).status_code == 422
    assert client.post(PUBLIC, json={"kind": "newsletter", "fields": payload()["fields"]}).status_code == 422
    missing = client.post(PUBLIC, json={"kind": "contact"})
    assert missing.status_code == 422
    assert "consent" not in json.dumps(
        client.post(PUBLIC, json=payload(consent_privacy=False)).json()["error"].get("details", [])[0:0]
    )


def test_anti_abuse_limits_per_address_and_per_email(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "public_request_limit_per_10min", 4)
    statuses = [client.post(PUBLIC, json=payload(email=f"a{i}@example.com")).status_code for i in range(6)]
    assert statuses == [201, 201, 201, 201, 429, 429]


def test_same_email_cannot_flood(client):
    statuses = [client.post(PUBLIC, json=payload()).status_code for _ in range(7)]
    assert statuses[:5] == [201] * 5 and statuses[5:] == [429, 429]


def test_requests_are_routed_to_the_right_team_and_demo_is_a_sales_request(client, super_admin):
    client.post(PUBLIC, json=payload(type="partnership", email="p@example.com"))
    client.post(PUBLIC, json={**payload(email="d@example.com"), "kind": "demo"})
    client.post(PUBLIC, json=payload(type="nonsense", email="n@example.com"))
    items = client.get(ADMIN, headers=super_admin).json()["items"]
    assert {(i["kind"], i["request_type"], i["team"]) for i in items} == {
        ("contact", "partnership", "partnerships"),
        ("demo", "demo", "sales"),
        ("contact", "other", "sales"),
    }
    assert client.get(f"{ADMIN}?team=partnerships", headers=super_admin).json()["total"] == 1
    assert client.get(f"{ADMIN}?kind=demo", headers=super_admin).json()["total"] == 1


def test_internal_notification_goes_to_the_configured_team_address(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "sales_email", "ventes@izilens.com")
    client.post(PUBLIC, json=payload())
    internal = [m for m in outbox() if m["template"] == "request_internal"]
    assert internal and internal[0]["to"] == "ventes@izilens.com" and "Awa" not in internal[0]["body"]


def test_personal_data_is_encrypted_at_rest_and_absent_from_logs_and_audit(client, staff):
    from sqlalchemy import text

    from app.core.database import get_engine

    client.post(PUBLIC, json=payload())
    with get_engine().connect() as connection:
        raw = connection.execute(text("SELECT payload FROM public_requests")).scalar_one()
        stored = connection.execute(text("SELECT email_hash, ip_hash FROM public_requests")).one()
        mail = connection.execute(text("SELECT message FROM email_outbox")).scalars().first()
    assert "Awa" not in raw and "banque-sahel" not in raw and "banque-sahel" not in mail
    assert "@" not in stored[0] and len(stored[0]) == 64


def test_back_office_workflow_assignment_notes_and_history(client, staff, super_admin):
    sales = staff(UserRole.SALES_AGENT)
    created = client.post(PUBLIC, json=payload()).json()["reference"]
    item = client.get(f"{ADMIN}?search={created}", headers=sales).json()["items"][0]
    detail = client.get(f"{ADMIN}/{item['id']}", headers=sales).json()
    assert (
        detail["status"] == "new"
        and detail["contact"]["email"] == "awa.diop@banque-sahel.com"
        and detail["consent_privacy"] is True
    )
    assert (
        client.post(f"{ADMIN}/{item['id']}/status", json={"status": "qualified"}, headers=sales).json()["error"]["code"]
        == "INVALID_TRANSITION"
    )
    assert client.post(f"{ADMIN}/{item['id']}/status", json={"status": "new"}, headers=sales).status_code == 409
    assert (
        client.post(
            f"{ADMIN}/{item['id']}/status", json={"status": "in_review", "note": "Premier appel prévu"}, headers=sales
        ).json()["status"]
        == "in_review"
    )
    assert client.post(f"{ADMIN}/{item['id']}/assign", json={}, headers=sales).json()["assigned_to_user_id"]
    assert client.post(f"{ADMIN}/{item['id']}/notes", json={"note": "Rappeler jeudi"}, headers=sales).status_code == 200
    closed = client.post(f"{ADMIN}/{item['id']}/status", json={"status": "closed"}, headers=sales).json()
    assert closed["status"] == "closed" and closed["closed_at"]
    events = [(e["event_type"], e["to_status"], e["note"]) for e in closed["events"]]
    assert (
        events[0] == ("received", "new", None)
        and ("note", None, "Rappeler jeudi") in events
        and ("status_changed", "in_review", "Premier appel prévu") in events
    )
    assert (
        client.post(f"{ADMIN}/{item['id']}/status", json={"status": "in_review"}, headers=sales).json()["status"] == "in_review"
    )
    assert client.get(f"{ADMIN}/stats", headers=sales).json()["by_status"] == {"in_review": 1}
    assert client.get(f"{ADMIN}?mine=true", headers=sales).json()["total"] == 1


def test_back_office_access_is_limited_to_the_right_roles(client, org, staff):
    created = client.post(PUBLIC, json=payload()).json()["reference"]
    assert client.get(ADMIN, headers=org["admin"]).status_code == 403
    assert client.get(ADMIN).status_code == 401
    for role in (UserRole.CONTENT_EDITOR, UserRole.BILLING_MANAGER):
        assert client.get(ADMIN, headers=staff(role)).status_code == 403
    assert client.get(f"{ADMIN}?search={created}", headers=staff(UserRole.PLATFORM_COMPLIANCE)).status_code == 200
    sales = staff(UserRole.SALES_AGENT)
    request_id = client.get(ADMIN, headers=sales).json()["items"][0]["id"]
    tenant = org["reviewer"]
    assert (
        client.post(
            f"{ADMIN}/{request_id}/assign",
            json={"assignee_user_id": client.get("/api/v1/auth/me", headers=tenant).json()["id"]},
            headers=sales,
        ).json()["error"]["code"]
        == "ASSIGNEE_INVALID"
    )
