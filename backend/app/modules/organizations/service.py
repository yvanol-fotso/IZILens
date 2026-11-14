import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import Conflict, NotFound
from app.core.principal import Principal
from app.modules.audit import service as audit
from app.modules.organizations.models import Organization
from app.modules.organizations.schemas import OrganizationCreate, OrganizationUpdate


def create_organization(db: Session, principal: Principal, payload: OrganizationCreate) -> Organization:
    organization = Organization(name=payload.name, slug=payload.slug, enabled_modules=payload.enabled_modules)
    db.add(organization)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Ce slug est déjà utilisé", code="SLUG_ALREADY_USED") from exc
    audit.record(
        db,
        action="organization.created",
        resource_type="organization",
        resource_id=organization.id,
        principal=principal,
        organization_id=organization.id,
        details={"modules": organization.enabled_modules},
    )
    db.commit()
    return organization


def get_organization(db: Session, organization_id: uuid.UUID) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise NotFound("Organisation introuvable", code="ORGANIZATION_NOT_FOUND")
    return organization


def list_organizations(db: Session, page: int, page_size: int) -> tuple[list[Organization], int]:
    total = db.scalar(select(func.count()).select_from(Organization)) or 0
    rows = db.scalars(
        select(Organization).order_by(Organization.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(rows), total


def update_organization(
    db: Session, principal: Principal, organization_id: uuid.UUID, payload: OrganizationUpdate
) -> Organization:
    organization = get_organization(db, organization_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(organization, field, value)
    audit.record(
        db,
        action="organization.updated",
        resource_type="organization",
        resource_id=organization.id,
        principal=principal,
        organization_id=organization.id,
        details={"fields": sorted(changes)},
    )
    db.commit()
    return organization
