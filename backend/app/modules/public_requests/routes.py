import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import client_ip, require_access
from app.core.principal import Principal
from app.modules.notifications.service import dispatch_pending
from app.modules.public_requests import service
from app.modules.public_requests.schemas import (
    AssignIn,
    ContactRequestIn,
    ContactRequestOut,
    NoteIn,
    RequestDetail,
    RequestSummary,
    StatusChange,
)

public_router = APIRouter(prefix="/public", tags=["Public"])
admin_router = APIRouter(prefix="/admin/public-requests", tags=["Back-office : demandes publiques"])
staff = require_access(UserRole.SUPER_ADMIN, UserRole.SALES_AGENT, UserRole.PLATFORM_COMPLIANCE, tenant=False)


@public_router.post(
    "/contact-requests",
    response_model=ContactRequestOut,
    status_code=201,
    summary="Envoyer une demande de contact, de devis ou de démonstration",
)
def create_contact_request(
    payload: ContactRequestIn, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    created = service.create_request(db, payload, client_ip(request))
    background_tasks.add_task(dispatch_pending)
    return ContactRequestOut(reference=created.reference)


@admin_router.get("", response_model=Page[RequestSummary], summary="Lister les demandes publiques")
def list_requests(
    status: str | None = Query(None, pattern=r"^(new|in_review|contacted|qualified|closed)$"),
    kind: str | None = Query(None, pattern=r"^(contact|demo)$"),
    team: str | None = Query(None, pattern=r"^(sales|partnerships)$"),
    search: str | None = Query(None, max_length=64),
    mine: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    principal: Principal = Depends(staff),
    db: Session = Depends(get_db),
):
    items, total = service.list_requests(
        db,
        status=status,
        kind=kind,
        team=team,
        search=search,
        assigned_to=principal.actor_id if mine else None,
        page=page,
        page_size=page_size,
    )
    return Page(items=[RequestSummary.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@admin_router.get("/stats", summary="Compteurs par statut et par équipe")
def stats(_: Principal = Depends(staff), db: Session = Depends(get_db)):
    return service.stats(db)


@admin_router.get("/{request_id}", response_model=RequestDetail, summary="Détail d'une demande (coordonnées, historique)")
def get_request(request_id: uuid.UUID, _: Principal = Depends(staff), db: Session = Depends(get_db)):
    return service.detail(service.get_request(db, request_id))


@admin_router.post("/{request_id}/status", response_model=RequestDetail, summary="Changer le statut")
def change_status(
    request_id: uuid.UUID, payload: StatusChange, principal: Principal = Depends(staff), db: Session = Depends(get_db)
):
    return service.detail(service.change_status(db, principal, service.get_request(db, request_id), payload.status, payload.note))


@admin_router.post("/{request_id}/assign", response_model=RequestDetail, summary="Assigner la demande")
def assign(request_id: uuid.UUID, payload: AssignIn, principal: Principal = Depends(staff), db: Session = Depends(get_db)):
    return service.detail(service.assign(db, principal, service.get_request(db, request_id), payload.assignee_user_id))


@admin_router.post("/{request_id}/notes", response_model=RequestDetail, summary="Ajouter une note interne")
def add_note(request_id: uuid.UUID, payload: NoteIn, principal: Principal = Depends(staff), db: Session = Depends(get_db)):
    return service.detail(service.add_note(db, principal, service.get_request(db, request_id), payload.note))
