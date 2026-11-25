import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.exceptions import NotFound
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.billing import service
from app.modules.billing.schemas import (
    Consumption,
    CreditNoteCreate,
    CreditNoteRead,
    InvoiceGenerate,
    InvoiceRead,
    PlanCreate,
    PlanRead,
    PlanUpdate,
    SubscriptionCreate,
    SubscriptionRead,
)

router = APIRouter(prefix="/billing", tags=["Facturation (organisation)"])
admin_router = APIRouter(prefix="/admin/billing", tags=["Back-office : facturation"])
tenant_admin = require_access(UserRole.ADMIN)
manager = require_access(UserRole.SUPER_ADMIN, UserRole.BILLING_MANAGER, tenant=False)


@router.get("/subscription", response_model=SubscriptionRead, summary="Abonnement actif de l'organisation")
def my_subscription(principal: Principal = Depends(tenant_admin), db: Session = Depends(get_db)):
    subscription = service.active_subscription(db, principal.organization_id)
    if subscription is None:
        raise NotFound("Aucun abonnement actif", code="NO_SUBSCRIPTION")
    return subscription


@router.get("/consumption", response_model=Consumption, summary="Consommation et estimation sur une période")
def my_consumption(
    start: date | None = None,
    end: date | None = None,
    principal: Principal = Depends(tenant_admin),
    db: Session = Depends(get_db),
):
    today = utcnow().date()
    return service.consumption(db, principal.organization_id, start or today.replace(day=1), end or today)


@router.get("/invoices", response_model=Page[InvoiceRead], summary="Factures de l'organisation (hors brouillons)")
def my_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    principal: Principal = Depends(tenant_admin),
    db: Session = Depends(get_db),
):
    items, total = service.list_invoices(
        db, organization_id=principal.organization_id, status=None, page=page, page_size=page_size, hide_drafts=True
    )
    return Page(items=[service.to_read(db, i) for i in items], total=total, page=page, page_size=page_size)


@router.get("/invoices/{invoice_id}", response_model=InvoiceRead, summary="Détail d'une facture")
def my_invoice(invoice_id: uuid.UUID, principal: Principal = Depends(tenant_admin), db: Session = Depends(get_db)):
    return service.to_read(db, service.get_invoice(db, invoice_id, principal.organization_id))


@admin_router.get("/plans", response_model=list[PlanRead], summary="Forfaits")
def plans(_: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.list_plans(db)


@admin_router.post("/plans", response_model=PlanRead, status_code=201, summary="Créer un forfait (prix par devise)")
def create_plan(payload: PlanCreate, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.create_plan(db, principal, payload)


@admin_router.patch("/plans/{plan_id}", response_model=PlanRead, summary="Modifier un forfait")
def update_plan(plan_id: uuid.UUID, payload: PlanUpdate, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.update_plan(db, principal, plan_id, payload)


@admin_router.post(
    "/subscriptions",
    response_model=SubscriptionRead,
    status_code=201,
    summary="Abonner une organisation (remplace l'abonnement actif)",
)
def subscribe(payload: SubscriptionCreate, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.subscribe(db, principal, payload)


@admin_router.get("/consumption", response_model=Consumption, summary="Consommation d'une organisation")
def consumption(
    organization_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    _: Principal = Depends(manager),
    db: Session = Depends(get_db),
):
    today = utcnow().date()
    return service.consumption(db, organization_id, start or today.replace(day=1), end or today)


@admin_router.get("/invoices", response_model=Page[InvoiceRead], summary="Toutes les factures")
def invoices(
    organization_id: uuid.UUID | None = None,
    status: str | None = Query(None, pattern=r"^(draft|issued|paid|void)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: Principal = Depends(manager),
    db: Session = Depends(get_db),
):
    items, total = service.list_invoices(
        db, organization_id=organization_id, status=status, page=page, page_size=page_size, hide_drafts=False
    )
    return Page(items=[service.to_read(db, i) for i in items], total=total, page=page, page_size=page_size)


@admin_router.post(
    "/invoices/generate", response_model=InvoiceRead, status_code=201, summary="Générer une facture brouillon pour une période"
)
def generate(payload: InvoiceGenerate, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.to_read(db, service.generate_invoice(db, principal, payload))


@admin_router.get("/invoices/{invoice_id}", response_model=InvoiceRead, summary="Détail d'une facture")
def invoice(invoice_id: uuid.UUID, _: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.to_read(db, service.get_invoice(db, invoice_id))


@admin_router.post("/invoices/{invoice_id}/issue", response_model=InvoiceRead, summary="Émettre (numéro séquentiel, échéance)")
def issue(invoice_id: uuid.UUID, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.to_read(db, service.issue_invoice(db, principal, service.get_invoice(db, invoice_id)))


@admin_router.post("/invoices/{invoice_id}/pay", response_model=InvoiceRead, summary="Marquer payée")
def pay(invoice_id: uuid.UUID, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.to_read(db, service.mark_paid(db, principal, service.get_invoice(db, invoice_id)))


@admin_router.post(
    "/invoices/{invoice_id}/void", response_model=InvoiceRead, summary="Annuler un brouillon ou une facture émise sans avoir"
)
def void(invoice_id: uuid.UUID, principal: Principal = Depends(manager), db: Session = Depends(get_db)):
    return service.to_read(db, service.void_invoice(db, principal, service.get_invoice(db, invoice_id)))


@admin_router.post(
    "/invoices/{invoice_id}/credit-notes",
    response_model=CreditNoteRead,
    status_code=201,
    summary="Émettre un avoir (total ou partiel)",
)
def credit_note(
    invoice_id: uuid.UUID, payload: CreditNoteCreate, principal: Principal = Depends(manager), db: Session = Depends(get_db)
):
    return service.issue_credit_note(db, principal, service.get_invoice(db, invoice_id), payload)
