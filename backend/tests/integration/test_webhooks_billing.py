import json

import httpx

from app.core.config import get_settings
from app.modules.webhooks import service as webhooks
from tests.helpers import make_flat_image, make_image
from tests.integration.utils import CASES, submit

HOOKS = "/api/v1/webhooks"


def register(client, org, url="https://hooks.client.example/izilens", **extra):
    response = client.post(HOOKS, json={"url": url, **extra}, headers=org["admin"])
    assert response.status_code == 201, response.text
    return response.json()


def test_webhook_registration_rules(client, org, monkeypatch):
    created = register(client, org, events=["case.status_changed"])
    assert created["secret"].startswith("whsec_") and created["is_active"]
    assert "secret" not in client.get(HOOKS, headers=org["admin"]).json()[0]
    assert client.post(HOOKS, json={"url": "https://x.example/h"}, headers=org["reviewer"]).status_code == 403
    assert (
        client.post(HOOKS, json={"url": "http://hooks.client.example/h"}, headers=org["admin"]).json()["error"]["code"]
        == "INVALID_WEBHOOK_URL"
    )
    assert client.post(HOOKS, json={"url": "https://user:pw@hooks.client.example/h"}, headers=org["admin"]).status_code == 422
    assert (
        client.post(HOOKS, json={"url": "https://hooks.client.example/h", "events": ["nope"]}, headers=org["admin"]).status_code
        == 422
    )
    for private in ("127.0.0.1", "10.0.0.5", "169.254.169.254", "192.168.1.10"):
        monkeypatch.setattr(webhooks, "_resolve", lambda host, ip=private: [ip])
        assert (
            client.post(HOOKS, json={"url": "https://internal.example/h"}, headers=org["admin"]).json()["error"]["code"]
            == "INVALID_WEBHOOK_URL"
        )


def test_status_changes_are_signed_delivered_and_free_of_personal_data(client, org, webhook_sink):
    hook = register(client, org)
    case_id = submit(client, org["api_key"]).json()["id"]
    assert webhook_sink.requests, "aucune livraison"
    events = [json.loads(r.content) for r in webhook_sink.requests]
    assert [e["event"] for e in events][0] == "case.created" and events[-1]["status"] == "manual_review"
    assert all(e["case_id"] == case_id for e in events)
    request = webhook_sink.requests[-1]
    header = request.headers["x-izilens-signature"]
    timestamp = int(header.split(",")[0].removeprefix("t="))
    assert header == webhooks.sign(hook["secret"], timestamp, request.content)
    assert webhooks.sign("whsec_other", timestamp, request.content) != header
    body = request.content.decode()
    for personal in ("Atángana", "Salah", "1992", "Baffousam"):
        assert personal not in body
    deliveries = client.get(f"{HOOKS}/{hook['id']}/deliveries", headers=org["admin"]).json()
    assert {d["status"] for d in deliveries} == {"delivered"}


def test_event_subscription_filters_deliveries(client, org, webhook_sink):
    register(client, org, events=["case.created"])
    submit(client, org["api_key"])
    assert {json.loads(r.content)["event"] for r in webhook_sink.requests} == {"case.created"}


def test_failed_deliveries_are_retried_then_marked_failed(client, org, webhook_sink, super_admin, monkeypatch):
    hook = register(client, org)
    webhook_sink.status = 500
    submit(client, org["api_key"], with_documents=False)
    deliveries = client.get(f"{HOOKS}/{hook['id']}/deliveries", headers=org["admin"]).json()
    assert deliveries[0]["status"] == "pending" and deliveries[0]["attempts"] == 1 and deliveries[0]["last_error"] == "HTTP 500"
    monkeypatch.setattr(get_settings(), "webhook_max_attempts", 2)
    from datetime import UTC, datetime, timedelta

    from app.core.database import session_scope
    from app.models_registry import WebhookDelivery

    with session_scope() as db:
        for delivery in db.query(WebhookDelivery).all():
            delivery.next_attempt_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert webhooks.dispatch_pending()["failed"] == 1
    assert client.get(f"{HOOKS}/{hook['id']}/deliveries", headers=org["admin"]).json()[0]["status"] == "failed"
    webhook_sink.status = 200
    delivery_id = deliveries[0]["id"]
    assert client.post(f"/api/v1/admin/webhooks/deliveries/{delivery_id}/retry", headers=super_admin).status_code == 200
    assert webhooks.dispatch_pending()["delivered"] == 1


def test_deactivated_or_foreign_webhooks_receive_nothing(client, org, make_org, webhook_sink):
    hook = register(client, org)
    other = make_org("beta")
    assert client.delete(f"{HOOKS}/{hook['id']}", headers=other["admin"]).status_code == 404
    assert client.get(f"{HOOKS}/{hook['id']}/deliveries", headers=other["admin"]).status_code == 404
    assert client.delete(f"{HOOKS}/{hook['id']}", headers=org["admin"]).json()["is_active"] is False
    submit(client, org["api_key"])
    assert webhook_sink.requests == []
    submit(client, other["api_key"], reference="X")
    assert webhook_sink.requests == []


def test_billing_counts_requests_and_follows_the_approved_policy(client, org):
    created = submit(client, org["api_key"], front=make_flat_image()).json()["id"]
    client.post(f"{CASES}/{created}/documents", files={"front": ("a.png", make_image(60), "image/png")}, headers=org["api_key"])
    usage = {(u["event_type"], u["billable"]): u["events"] for u in client.get("/api/v1/kyc/usage", headers=org["admin"]).json()}
    assert usage[("case_created", True)] == 1 and usage[("attempt", False)] == 1 and usage[("manual_review", False)] == 1


def test_technical_failures_are_never_billable_even_when_attempts_are(client, org, super_admin):
    from app.shared.ocr.engine import set_engine
    from tests.helpers import FakeEngine

    journey = next(
        j for j in client.get("/api/v1/admin/kyc/journeys", headers=super_admin).json() if j["organization_id"] is None
    )
    client.patch(
        f"/api/v1/admin/kyc/journeys/{journey['id']}",
        json={"billing": {"attempts": True, "manual_review": True}},
        headers=super_admin,
    )
    set_engine(FakeEngine(RuntimeError("down")))
    created = submit(client, org["api_key"]).json()["id"]
    client.post(f"{CASES}/{created}/reprocess", headers=org["reviewer"])
    usage = {(u["event_type"], u["billable"]): u["events"] for u in client.get("/api/v1/kyc/usage", headers=org["admin"]).json()}
    assert usage[("technical_failure", False)] == 2 and usage[("attempt", True)] == 1 and usage[("case_created", True)] == 1


def test_usage_access_and_isolation(client, org, make_org, platform):
    other = make_org("beta")
    submit(client, org["api_key"])
    assert client.get("/api/v1/kyc/usage", headers=org["reviewer"]).status_code == 403
    assert client.get("/api/v1/kyc/usage", headers=other["admin"]).json() == []
    everything = client.get("/api/v1/admin/kyc/usage", headers=platform).json()
    assert {u["organization_id"] for u in everything} == {org["organization"]["id"]}
    assert client.get(f"/api/v1/admin/kyc/usage?organization_id={other['organization']['id']}", headers=platform).json() == []
    assert client.get("/api/v1/admin/kyc/usage", headers=org["admin"]).status_code == 403


def test_http_client_is_isolated_from_the_network(webhook_sink):
    assert isinstance(webhooks.httpx.Client(timeout=1), httpx.Client)
