import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import get_principal, require_access
from app.core.exceptions import NotFound
from app.core.principal import Principal
from app.modules.organizations import service
from app.modules.organizations.schemas import OrganizationCreate, OrganizationRead, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["Organisations"])
super_admin_only = require_access(UserRole.SUPER_ADMIN, tenant=False)


@router.post("", response_model=OrganizationRead, status_code=201, summary="Créer une organisation cliente")
def create_organization(
    payload: OrganizationCreate, principal: Principal = Depends(super_admin_only), db: Session = Depends(get_db)
):
    return service.create_organization(db, principal, payload)


@router.get("", response_model=Page[OrganizationRead], summary="Lister les organisations")
def list_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    _: Principal = Depends(super_admin_only),
    db: Session = Depends(get_db),
):
    items, total = service.list_organizations(db, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/me", response_model=OrganizationRead, summary="Organisation de l'utilisateur connecté")
def my_organization(principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    if principal.organization_id is None:
        raise NotFound("Aucune organisation rattachée", code="ORGANIZATION_NOT_FOUND")
    return service.get_organization(db, principal.organization_id)


@router.get("/{organization_id}", response_model=OrganizationRead, summary="Détail d'une organisation")
def get_organization(organization_id: uuid.UUID, _: Principal = Depends(super_admin_only), db: Session = Depends(get_db)):
    return service.get_organization(db, organization_id)


@router.patch("/{organization_id}", response_model=OrganizationRead, summary="Modifier nom, statut ou modules souscrits")
def update_organization(
    organization_id: uuid.UUID,
    payload: OrganizationUpdate,
    principal: Principal = Depends(super_admin_only),
    db: Session = Depends(get_db),
):
    return service.update_organization(db, principal, organization_id, payload)
