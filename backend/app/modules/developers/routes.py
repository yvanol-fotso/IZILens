import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import get_principal, require_access
from app.core.exceptions import Forbidden
from app.core.principal import Principal
from app.modules.developers import service
from app.modules.developers.schemas import AccessDecision, AccessRequestCreate, AccessRequestRead, DeveloperOverview

router = APIRouter(prefix="/developers", tags=["Portail développeur"])
admin_router = APIRouter(prefix="/admin/developers", tags=["Back-office : accès développeur"])
staff = require_access(UserRole.SUPER_ADMIN, UserRole.SALES_AGENT, UserRole.PLATFORM_COMPLIANCE, tenant=False)


def user_only(principal: Principal = Depends(get_principal)) -> Principal:
    if principal.kind != "user":
        raise Forbidden("Réservé aux utilisateurs du portail", code="INSUFFICIENT_ROLE")
    return principal


@router.get("/overview", response_model=DeveloperOverview, summary="État de l'accès Sandbox et Production")
def overview(principal: Principal = Depends(user_only), db: Session = Depends(get_db)):
    return service.overview(db, principal)


@router.post(
    "/access-requests",
    response_model=AccessRequestRead,
    status_code=201,
    summary="Demander l'accès Sandbox (compte sans organisation) ou Production (administrateur)",
)
def create_request(payload: AccessRequestCreate, principal: Principal = Depends(user_only), db: Session = Depends(get_db)):
    return service.create_request(db, principal, payload)


@router.get("/access-requests", response_model=list[AccessRequestRead], summary="Mes demandes d'accès")
def my_requests(principal: Principal = Depends(user_only), db: Session = Depends(get_db)):
    return service.my_requests(db, principal)


@admin_router.get("/access-requests", response_model=Page[AccessRequestRead], summary="Demandes d'accès à traiter")
def list_requests(
    status: str | None = Query(None, pattern=r"^(pending|approved|rejected)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: Principal = Depends(staff),
    db: Session = Depends(get_db),
):
    items, total = service.list_requests(db, status, page, page_size)
    return Page(items=[AccessRequestRead.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@admin_router.post(
    "/access-requests/{request_id}/decision",
    response_model=AccessRequestRead,
    summary="Approuver (crée l'organisation Sandbox ou active la Production) ou refuser",
)
def decide(request_id: uuid.UUID, payload: AccessDecision, principal: Principal = Depends(staff), db: Session = Depends(get_db)):
    return service.decide(db, principal, request_id, payload)
