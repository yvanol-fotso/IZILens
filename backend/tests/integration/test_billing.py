from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.common.enums import UserRole
from tests.helpers import make_image
from tests.integration.utils import submit

API = "/api/v1"
ADMIN = f"{API}/admin/billing"
PLAN = {
    "code": "standard",
    "name": "Standard",
    "prices": {
        "XAF": {"monthly_fee": "10000.00", "unit_prices": {"case_created": "500.00", "attempt": "100.00"}},
        "EUR": {"monthly_fee": "20.00", "unit_prices": {"case_created": "0.75"}},
    },
}
TODAY = datetime.now(UTC).date()
START, END = TODAY.replace(day=1).isoformat(), TODAY.isoformat()


def setup_billing(client, staff, org, currency="XAF", tax="19.25"):
    billing = staff(UserRole.BILLING_MANAGER)
    plan = client.post(f"{ADMIN}/plans", json=PLAN, headers=billing).json()
    sub = client.post(
        f"{ADMIN}/subscriptions",
        json={"organization_id": org["organization"]["id"], "plan_id": plan["id"], "currency": currency, "tax_rate": tax},
        headers=billing,
    )
    assert sub.status_code == 201, sub.text
    return billing, plan


def create_cases(client, org, count=3):
    for i in range(count):
        assert submit(client, org["api_key"], reference=f"B{i}", front=make_image(900 + i)).status_code == 202


def generate(client, billing, org, start=START, end=END):
    return client.post(
        f"{ADMIN}/invoices/generate",
        json={"organization_id": org["organization"]["id"], "period_start": start, "period_end": end},
        headers=billing,
    )


def test_plan_validation_and_management(client, staff):
    billing = staff(UserRole.BILLING_MANAGER)
    for bad in (
        {**PLAN, "prices": {"JPY": {"monthly_fee": "1", "unit_prices": {}}}},
        {**PLAN, "prices": {"XAF": {"monthly_fee": "-5", "unit_prices": {}}}},
        {**PLAN, "prices": {"XAF": {"monthly_fee": "1.234", "unit_prices": {}}}},
        {**PLAN, "prices": {"XAF": {"monthly_fee": "1", "unit_prices": {"free_lunch": "1"}}}},
        {**PLAN, "prices": {}},
        {**PLAN, "code": "Bad Code"},
    ):
        assert client.post(f"{ADMIN}/plans", json=bad, headers=billing).status_code == 422
    created = client.post(f"{ADMIN}/plans", json=PLAN, headers=billing)
    assert created.status_code == 201 and created.json()["prices"]["XAF"]["unit_prices"]["case_created"] == "500.00"
    assert client.post(f"{ADMIN}/plans", json=PLAN, headers=billing).json()["error"]["code"] == "PLAN_CODE_ALREADY_USED"
    updated = client.patch(
        f"{ADMIN}/plans/{created.json()['id']}", json={"name": "Standard 2026", "is_active": False}, headers=billing
    ).json()
    assert (updated["name"], updated["is_active"]) == ("Standard 2026", False)
    assert [p["code"] for p in client.get(f"{ADMIN}/plans", headers=billing).json()] == ["standard"]


def test_subscription_rules_and_organization_view(client, org, staff):
    billing = staff(UserRole.BILLING_MANAGER)
    assert client.get(f"{API}/billing/subscription", headers=org["admin"]).json()["error"]["code"] == "NO_SUBSCRIPTION"
    plan = client.post(f"{ADMIN}/plans", json={**PLAN, "prices": {"XAF": PLAN["prices"]["XAF"]}}, headers=billing).json()
    body = {"organization_id": org["organization"]["id"], "plan_id": plan["id"], "currency": "EUR"}
    assert client.post(f"{ADMIN}/subscriptions", json=body, headers=billing).json()["error"]["code"] == "CURRENCY_NOT_IN_PLAN"
    first = client.post(f"{ADMIN}/subscriptions", json={**body, "currency": "XAF"}, headers=billing).json()
    second = client.post(f"{ADMIN}/subscriptions", json={**body, "currency": "XAF", "tax_rate": "18"}, headers=billing).json()
    mine = client.get(f"{API}/billing/subscription", headers=org["admin"]).json()
    assert mine["id"] == second["id"] != first["id"] and Decimal(mine["tax_rate"]) == Decimal("18")
    assert client.post(f"{ADMIN}/subscriptions", json={**body, "currency": "JPY"}, headers=billing).status_code == 422


def test_invoice_is_computed_from_billable_events_with_fee_and_tax(client, org, staff):
    billing, _ = setup_billing(client, staff, org)
    create_cases(client, org, 3)
    invoice = generate(client, billing, org)
    assert invoice.status_code == 201
    body = invoice.json()
    assert body["status"] == "draft" and body["number"] is None and body["currency"] == "XAF"
    lines = {line["event_type"]: line for line in body["lines"]}
    assert (
        lines["monthly_fee"]["amount"] == "10000.00"
        and lines["case_created"]["quantity"] == 3
        and lines["case_created"]["amount"] == "1500.00"
    )
    assert (Decimal(body["subtotal"]), Decimal(body["tax_amount"]), Decimal(body["total"])) == (
        Decimal("11500.00"),
        Decimal("2213.75"),
        Decimal("13713.75"),
    )
    assert generate(client, billing, org).json()["error"]["code"] == "INVOICE_ALREADY_EXISTS"


def test_period_bounds_currency_and_sandbox_exclusion(client, org, staff):
    billing, _ = setup_billing(client, staff, org, currency="EUR", tax="0")
    create_cases(client, org, 2)
    sandbox = client.post(f"{API}/api-keys", json={"name": "sb", "environment": "sandbox"}, headers=org["admin"]).json()
    submit(client, {"X-API-Key": sandbox["key"]}, reference="SB", front=make_image(990))
    past = (TODAY - timedelta(days=60)).isoformat(), (TODAY - timedelta(days=40)).isoformat()
    empty = generate(client, billing, org, *past).json()
    assert [line["event_type"] for line in empty["lines"]] == ["monthly_fee"] and empty["currency"] == "EUR"
    current = generate(client, billing, org).json()
    quantities = {line["event_type"]: line["quantity"] for line in current["lines"]}
    assert quantities["case_created"] == 2 and Decimal(current["total"]) == Decimal("21.50")
    assert (
        client.post(
            f"{ADMIN}/invoices/generate",
            json={"organization_id": org["organization"]["id"], "period_start": END, "period_end": START},
            headers=billing,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{ADMIN}/invoices/generate",
            json={"organization_id": org["organization"]["id"], "period_start": "2020-01-01", "period_end": "2024-01-01"},
            headers=billing,
        ).status_code
        == 422
    )


def test_invoice_requires_an_active_subscription(client, org, staff):
    assert generate(client, staff(UserRole.BILLING_MANAGER), org).json()["error"]["code"] == "NO_SUBSCRIPTION"


def test_issue_numbering_payment_and_visibility(client, org, staff, make_org):
    billing, _ = setup_billing(client, staff, org)
    other = make_org("beta")
    create_cases(client, org, 1)
    first = generate(client, billing, org).json()
    assert client.get(f"{API}/billing/invoices", headers=org["admin"]).json()["total"] == 0
    assert client.get(f"{API}/billing/invoices/{first['id']}", headers=org["admin"]).status_code == 404
    issued = client.post(f"{ADMIN}/invoices/{first['id']}/issue", headers=billing).json()
    year = datetime.now(UTC).year
    assert issued["number"] == f"INV-{year}-000001" and issued["status"] == "issued" and issued["due_at"]
    assert client.post(f"{ADMIN}/invoices/{first['id']}/issue", headers=billing).status_code == 409
    previous = (TODAY - timedelta(days=90)).isoformat(), (TODAY - timedelta(days=60)).isoformat()
    second = generate(client, billing, org, *previous).json()
    assert client.post(f"{ADMIN}/invoices/{second['id']}/issue", headers=billing).json()["number"] == f"INV-{year}-000002"
    assert client.get(f"{API}/billing/invoices", headers=org["admin"]).json()["total"] == 2
    assert client.get(f"{API}/billing/invoices/{first['id']}", headers=org["admin"]).json()["number"] == issued["number"]
    assert client.get(f"{API}/billing/invoices/{first['id']}", headers=other["admin"]).status_code == 404
    assert client.get(f"{API}/billing/invoices", headers=other["admin"]).json()["total"] == 0
    paid = client.post(f"{ADMIN}/invoices/{first['id']}/pay", headers=billing).json()
    assert paid["status"] == "paid" and paid["paid_at"]
    assert client.post(f"{ADMIN}/invoices/{first['id']}/pay", headers=billing).status_code == 409
    assert client.get(f"{ADMIN}/invoices?status=paid", headers=billing).json()["total"] == 1


def test_void_rules_and_regeneration(client, org, staff):
    billing, _ = setup_billing(client, staff, org)
    draft = generate(client, billing, org).json()
    assert client.post(f"{ADMIN}/invoices/{draft['id']}/void", headers=billing).json()["status"] == "void"
    again = generate(client, billing, org)
    assert again.status_code == 201
    issued = client.post(f"{ADMIN}/invoices/{again.json()['id']}/issue", headers=billing).json()
    client.post(f"{ADMIN}/invoices/{issued['id']}/pay", headers=billing)
    assert client.post(f"{ADMIN}/invoices/{issued['id']}/void", headers=billing).json()["error"]["code"] == "INVALID_STATE"


def test_credit_notes_are_numbered_capped_and_visible_to_the_organization(client, org, staff):
    billing, _ = setup_billing(client, staff, org, tax="0")
    draft = generate(client, billing, org).json()
    assert (
        client.post(
            f"{ADMIN}/invoices/{draft['id']}/credit-notes", json={"amount": "100", "reason": "Geste commercial"}, headers=billing
        ).status_code
        == 409
    )
    invoice = client.post(f"{ADMIN}/invoices/{draft['id']}/issue", headers=billing).json()
    assert Decimal(invoice["total"]) == Decimal("10000.00")
    first = client.post(
        f"{ADMIN}/invoices/{invoice['id']}/credit-notes",
        json={"amount": "2500.50", "reason": "Erreur de facturation"},
        headers=billing,
    )
    assert (
        first.status_code == 201
        and first.json()["number"] == f"CN-{datetime.now(UTC).year}-000001"
        and first.json()["currency"] == "XAF"
    )
    too_much = client.post(
        f"{ADMIN}/invoices/{invoice['id']}/credit-notes", json={"amount": "7500", "reason": "Trop élevé"}, headers=billing
    )
    assert too_much.status_code == 422 and too_much.json()["error"]["code"] == "CREDIT_EXCEEDS_INVOICE"
    assert (
        client.post(
            f"{ADMIN}/invoices/{invoice['id']}/credit-notes", json={"amount": "0", "reason": "Montant nul"}, headers=billing
        ).status_code
        == 422
    )
    last = client.post(
        f"{ADMIN}/invoices/{invoice['id']}/credit-notes",
        json={"amount": "7499.50", "reason": "Annulation du solde"},
        headers=billing,
    )
    assert last.status_code == 201
    seen = client.get(f"{API}/billing/invoices/{invoice['id']}", headers=org["admin"]).json()
    assert (
        len(seen["credit_notes"]) == 2
        and Decimal(seen["credited_total"]) == Decimal("10000.00")
        and Decimal(seen["balance"]) == Decimal("0")
    )
    assert client.post(f"{ADMIN}/invoices/{invoice['id']}/void", headers=billing).json()["error"]["code"] == "INVALID_STATE"


def test_consumption_estimates_and_transparency(client, org, staff):
    assert client.get(f"{API}/billing/consumption", headers=org["admin"]).json()["estimated_total"] is None
    billing, _ = setup_billing(client, staff, org, tax="0")
    create_cases(client, org, 2)
    mine = client.get(f"{API}/billing/consumption", headers=org["admin"]).json()
    assert mine["currency"] == "XAF" and Decimal(mine["estimated_total"]) == Decimal("11000.00")
    admin_view = client.get(f"{ADMIN}/consumption?organization_id={org['organization']['id']}", headers=billing).json()
    assert admin_view["lines"] == mine["lines"]


def test_billing_access_control(client, org, staff, super_admin):
    billing, plan = setup_billing(client, staff, org)
    invoice = generate(client, billing, org).json()
    for who in ("reviewer", "viewer", "api_key"):
        assert client.get(f"{API}/billing/invoices", headers=org[who]).status_code == 403
        assert client.get(f"{API}/billing/subscription", headers=org[who]).status_code == 403
    for headers in (
        org["admin"],
        staff(UserRole.PLATFORM_COMPLIANCE),
        staff(UserRole.SALES_AGENT),
        staff(UserRole.CONTENT_EDITOR),
    ):
        assert client.get(f"{ADMIN}/plans", headers=headers).status_code == 403
        assert client.post(f"{ADMIN}/invoices/{invoice['id']}/issue", headers=headers).status_code == 403
    assert client.get(f"{ADMIN}/invoices/{invoice['id']}", headers=super_admin).status_code == 200
    audit = [
        i["action"]
        for i in client.get(f"{API}/admin/security/events?action_prefix=billing.", headers=super_admin).json()["items"]
    ]
    assert {"billing.invoice_generated", "billing.plan_created", "billing.subscribed"} <= set(audit) and plan
