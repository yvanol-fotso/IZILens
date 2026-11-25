import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.enums import BillingEventType
from app.core.exceptions import Conflict, NotFound, ValidationFailed
from app.core.numbering import next_value
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.billing.models import BillingEvent, BillingPlan, CreditNote, Invoice, Subscription
from app.modules.billing.schemas import (
    CreditNoteCreate,
    CreditNoteRead,
    InvoiceGenerate,
    InvoiceRead,
    PlanCreate,
    PlanUpdate,
    SubscriptionCreate,
)
from app.modules.kyc.models import KycCase

PAYMENT_TERMS_DAYS = 30
CENT = Decimal("0.01")
EVENT_LABELS = {
    "case_created": "Demandes de vérification",
    "attempt": "Tentatives supplémentaires",
    "manual_review": "Revues humaines",
    "extra_check": "Contrôles supplémentaires",
}

_CONFIG_KEY = {
    BillingEventType.CASE_CREATED: "case_created",
    BillingEventType.ATTEMPT: "attempts",
    BillingEventType.MANUAL_REVIEW: "manual_review",
    BillingEventType.EXTRA_CHECK: "extra_checks",
}


def record(db: Session, case: KycCase, event_type: BillingEventType, *, units: int = 1) -> None:
    """Journalise un événement ; la facturabilité suit la politique du parcours (incidents techniques jamais facturés)."""
    key = _CONFIG_KEY.get(event_type)
    billable = bool(key and case.journey.billing.get(key, False)) and not case.is_sandbox
    db.add(
        BillingEvent(
            organization_id=case.organization_id, case_id=case.id, event_type=event_type.value, billable=billable, units=units
        )
    )


def usage_summary(db: Session, *, organization_id: uuid.UUID | None, start: datetime | None, end: datetime | None) -> list[dict]:
    query = select(
        BillingEvent.organization_id,
        BillingEvent.event_type,
        func.count(BillingEvent.id),
        func.coalesce(func.sum(BillingEvent.units), 0),
        BillingEvent.billable,
    ).group_by(BillingEvent.organization_id, BillingEvent.event_type, BillingEvent.billable)
    if organization_id:
        query = query.where(BillingEvent.organization_id == organization_id)
    if start:
        query = query.where(BillingEvent.created_at >= start)
    if end:
        query = query.where(BillingEvent.created_at < end)
    rows = db.execute(query.order_by(BillingEvent.organization_id, BillingEvent.event_type)).all()
    return [
        {"organization_id": org, "event_type": kind, "events": count, "units": int(units), "billable": billable}
        for org, kind, count, units, billable in rows
    ]


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _dump_prices(prices: dict) -> dict:
    return {
        cur: {"monthly_fee": str(p.monthly_fee), "unit_prices": {k: str(v) for k, v in p.unit_prices.items()}}
        for cur, p in prices.items()
    }


# ----------------------------------------------------------------------------- forfaits et abonnements


def create_plan(db: Session, principal: Principal, payload: PlanCreate) -> BillingPlan:
    if db.scalar(select(BillingPlan.id).where(BillingPlan.code == payload.code)):
        raise Conflict("Ce code de forfait existe déjà", code="PLAN_CODE_ALREADY_USED")
    plan = BillingPlan(code=payload.code, name=payload.name, description=payload.description, prices=_dump_prices(payload.prices))
    db.add(plan)
    db.flush()
    audit.record(db, action="billing.plan_created", resource_type="billing_plan", resource_id=plan.id, principal=principal)
    db.commit()
    return plan


def update_plan(db: Session, principal: Principal, plan_id: uuid.UUID, payload: PlanUpdate) -> BillingPlan:
    plan = db.get(BillingPlan, plan_id)
    if plan is None:
        raise NotFound("Forfait introuvable", code="PLAN_NOT_FOUND")
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "prices" in changes:
        plan.prices = _dump_prices(payload.prices)  # type: ignore[arg-type]
        changes.pop("prices")
    for key, value in changes.items():
        setattr(plan, key, value)
    audit.record(db, action="billing.plan_updated", resource_type="billing_plan", resource_id=plan.id, principal=principal)
    db.commit()
    return plan


def list_plans(db: Session) -> list[BillingPlan]:
    return list(db.scalars(select(BillingPlan).order_by(BillingPlan.code)).all())


def subscribe(db: Session, principal: Principal, payload: SubscriptionCreate) -> Subscription:
    from app.modules.organizations.models import Organization

    plan = db.get(BillingPlan, payload.plan_id)
    if plan is None or not plan.is_active:
        raise NotFound("Forfait introuvable ou inactif", code="PLAN_NOT_FOUND")
    if payload.currency not in plan.prices:
        raise ValidationFailed("Ce forfait n'est pas tarifé dans cette devise", code="CURRENCY_NOT_IN_PLAN")
    if db.get(Organization, payload.organization_id) is None:
        raise NotFound("Organisation introuvable", code="ORGANIZATION_NOT_FOUND")
    today = utcnow().date()
    for previous in db.scalars(
        select(Subscription).where(Subscription.organization_id == payload.organization_id, Subscription.status == "active")
    ).all():
        previous.status, previous.ended_at = "cancelled", today
    subscription = Subscription(
        organization_id=payload.organization_id,
        plan_id=plan.id,
        currency=payload.currency,
        tax_rate=payload.tax_rate,
        started_at=payload.started_at or today,
    )
    db.add(subscription)
    db.flush()
    audit.record(
        db,
        action="billing.subscribed",
        resource_type="subscription",
        resource_id=subscription.id,
        principal=principal,
        organization_id=payload.organization_id,
        details={"plan": plan.code, "currency": payload.currency},
    )
    db.commit()
    return subscription


def active_subscription(db: Session, organization_id: uuid.UUID) -> Subscription | None:
    return db.scalar(select(Subscription).where(Subscription.organization_id == organization_id, Subscription.status == "active"))


# ----------------------------------------------------------------------------- consommation et factures


def _bounds(start: date, end: date) -> tuple[datetime, datetime]:
    return datetime(start.year, start.month, start.day, tzinfo=UTC), datetime(
        end.year, end.month, end.day, tzinfo=UTC
    ) + timedelta(days=1)


def _consumption(db: Session, organization_id: uuid.UUID, start: date, end: date) -> dict[str, int]:
    low, high = _bounds(start, end)
    rows = db.execute(
        select(BillingEvent.event_type, func.coalesce(func.sum(BillingEvent.units), 0))
        .where(
            BillingEvent.organization_id == organization_id,
            BillingEvent.billable.is_(True),
            BillingEvent.created_at >= low,
            BillingEvent.created_at < high,
        )
        .group_by(BillingEvent.event_type)
    ).all()
    return {kind: int(units) for kind, units in rows}


def _price_lines(db: Session, subscription: Subscription, quantities: dict[str, int], *, with_fee: bool) -> list[dict]:
    plan = db.get(BillingPlan, subscription.plan_id)
    prices = plan.prices[subscription.currency]
    lines: list[dict] = []
    fee = Decimal(prices["monthly_fee"])
    if with_fee and fee > 0:
        lines.append(
            {
                "description": f"Forfait {plan.name}",
                "event_type": "monthly_fee",
                "quantity": 1,
                "unit_price": str(_money(fee)),
                "amount": str(_money(fee)),
            }
        )
    for kind in sorted(quantities):
        unit = Decimal(prices["unit_prices"].get(kind, "0"))
        if quantities[kind] > 0 and unit > 0:
            lines.append(
                {
                    "description": EVENT_LABELS.get(kind, kind),
                    "event_type": kind,
                    "quantity": quantities[kind],
                    "unit_price": str(_money(unit)),
                    "amount": str(_money(unit * quantities[kind])),
                }
            )
    return lines


def consumption(db: Session, organization_id: uuid.UUID, start: date, end: date) -> dict:
    quantities = _consumption(db, organization_id, start, end)
    subscription = active_subscription(db, organization_id)
    if subscription is None:
        return {
            "currency": None,
            "period_start": start,
            "period_end": end,
            "lines": [{"event_type": k, "quantity": q} for k, q in sorted(quantities.items())],
            "estimated_total": None,
        }
    lines = _price_lines(db, subscription, quantities, with_fee=True)
    return {
        "currency": subscription.currency,
        "period_start": start,
        "period_end": end,
        "lines": lines,
        "estimated_total": sum((Decimal(line["amount"]) for line in lines), Decimal("0")),
    }


def generate_invoice(db: Session, principal: Principal, payload: InvoiceGenerate) -> Invoice:
    subscription = active_subscription(db, payload.organization_id)
    if subscription is None:
        raise ValidationFailed("Aucun abonnement actif pour cette organisation", code="NO_SUBSCRIPTION")
    clash = db.scalar(
        select(Invoice.id).where(
            Invoice.organization_id == payload.organization_id,
            Invoice.period_start == payload.period_start,
            Invoice.period_end == payload.period_end,
            Invoice.status != "void",
        )
    )
    if clash:
        raise Conflict("Une facture existe déjà pour cette période", code="INVOICE_ALREADY_EXISTS")
    lines = _price_lines(
        db, subscription, _consumption(db, payload.organization_id, payload.period_start, payload.period_end), with_fee=True
    )
    subtotal = _money(sum((Decimal(line["amount"]) for line in lines), Decimal("0")))
    tax = _money(subtotal * subscription.tax_rate / Decimal("100"))
    invoice = Invoice(
        organization_id=payload.organization_id,
        subscription_id=subscription.id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        currency=subscription.currency,
        lines=lines,
        subtotal=subtotal,
        tax_rate=subscription.tax_rate,
        tax_amount=tax,
        total=subtotal + tax,
    )
    db.add(invoice)
    db.flush()
    audit.record(
        db,
        action="billing.invoice_generated",
        resource_type="invoice",
        resource_id=invoice.id,
        principal=principal,
        organization_id=payload.organization_id,
    )
    db.commit()
    return invoice


def get_invoice(db: Session, invoice_id: uuid.UUID, organization_id: uuid.UUID | None = None) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if invoice is None or (
        organization_id is not None and (invoice.organization_id != organization_id or invoice.status == "draft")
    ):
        raise NotFound("Facture introuvable", code="INVOICE_NOT_FOUND")
    return invoice


def list_invoices(
    db: Session, *, organization_id: uuid.UUID | None, status: str | None, page: int, page_size: int, hide_drafts: bool
) -> tuple[list[Invoice], int]:
    query = select(Invoice)
    if organization_id:
        query = query.where(Invoice.organization_id == organization_id)
    if status:
        query = query.where(Invoice.status == status)
    if hide_drafts:
        query = query.where(Invoice.status != "draft")
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(Invoice.period_start.desc(), Invoice.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(rows), total


def issue_invoice(db: Session, principal: Principal, invoice: Invoice) -> Invoice:
    if invoice.status != "draft":
        raise Conflict("Seule une facture brouillon peut être émise", code="INVALID_STATE")
    year = utcnow().year
    invoice.number = f"INV-{year}-{next_value(db, f'INV-{year}'):06d}"
    invoice.status, invoice.issued_at = "issued", utcnow()
    invoice.due_at = utcnow().date() + timedelta(days=PAYMENT_TERMS_DAYS)
    audit.record(
        db,
        action="billing.invoice_issued",
        resource_type="invoice",
        resource_id=invoice.id,
        principal=principal,
        organization_id=invoice.organization_id,
        details={"number": invoice.number},
    )
    db.commit()
    return invoice


def mark_paid(db: Session, principal: Principal, invoice: Invoice) -> Invoice:
    if invoice.status != "issued":
        raise Conflict("Seule une facture émise peut être marquée payée", code="INVALID_STATE")
    invoice.status, invoice.paid_at = "paid", utcnow()
    audit.record(
        db,
        action="billing.invoice_paid",
        resource_type="invoice",
        resource_id=invoice.id,
        principal=principal,
        organization_id=invoice.organization_id,
    )
    db.commit()
    return invoice


def void_invoice(db: Session, principal: Principal, invoice: Invoice) -> Invoice:
    if invoice.status not in ("draft", "issued"):
        raise Conflict("Une facture payée s'annule par un avoir", code="INVALID_STATE")
    credited = db.scalar(select(func.coalesce(func.sum(CreditNote.amount), 0)).where(CreditNote.invoice_id == invoice.id)) or 0
    if credited:
        raise Conflict("Cette facture a déjà des avoirs", code="INVALID_STATE")
    invoice.status, invoice.voided_at = "void", utcnow()
    audit.record(
        db,
        action="billing.invoice_voided",
        resource_type="invoice",
        resource_id=invoice.id,
        principal=principal,
        organization_id=invoice.organization_id,
    )
    db.commit()
    return invoice


def credit_notes_of(db: Session, invoice_id: uuid.UUID) -> list[CreditNote]:
    return list(db.scalars(select(CreditNote).where(CreditNote.invoice_id == invoice_id).order_by(CreditNote.issued_at)).all())


def issue_credit_note(db: Session, principal: Principal, invoice: Invoice, payload: CreditNoteCreate) -> CreditNote:
    if invoice.status not in ("issued", "paid"):
        raise Conflict("Un avoir ne s'applique qu'à une facture émise ou payée", code="INVALID_STATE")
    already = sum((n.amount for n in credit_notes_of(db, invoice.id)), Decimal("0"))
    amount = _money(payload.amount)
    if already + amount > invoice.total:
        raise ValidationFailed("Le total des avoirs dépasse le montant de la facture", code="CREDIT_EXCEEDS_INVOICE")
    year = utcnow().year
    note = CreditNote(
        number=f"CN-{year}-{next_value(db, f'CN-{year}'):06d}",
        invoice_id=invoice.id,
        organization_id=invoice.organization_id,
        currency=invoice.currency,
        amount=amount,
        reason=payload.reason,
        issued_by_user_id=principal.actor_id,
    )
    db.add(note)
    db.flush()
    audit.record(
        db,
        action="billing.credit_note_issued",
        resource_type="credit_note",
        resource_id=note.id,
        principal=principal,
        organization_id=invoice.organization_id,
        details={"number": note.number},
    )
    db.commit()
    return note


def to_read(db: Session, invoice: Invoice) -> InvoiceRead:
    notes = credit_notes_of(db, invoice.id)
    credited = sum((n.amount for n in notes), Decimal("0"))
    data = InvoiceRead.model_validate(invoice)
    return data.model_copy(
        update={
            "credit_notes": [CreditNoteRead.model_validate(n) for n in notes],
            "credited_total": credited,
            "balance": invoice.total - credited,
        }
    )
