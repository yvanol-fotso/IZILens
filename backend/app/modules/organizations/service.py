import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import Conflict, NotFound
from app.core.principal import Principal
from app.modules.audit import service as audit
from app.modules.organizations.models import Organization
from app.modules.organizations.schemas import OrganizationCreate, OrganizationUpdate


def _invite_admin(db: Session, organization: Organization, payload: OrganizationCreate) -> None:
    """Crée l'administrateur de l'organisation : accès Google si activé, sinon mot de passe temporaire envoyé par e-mail."""
    import secrets

    from app.common.enums import UserRole
    from app.core.config import get_settings
    from app.core.security import hash_password
    from app.modules.notifications.service import queue_email
    from app.modules.users.models import User

    settings = get_settings()
    temporary = None if settings.oidc_enabled else secrets.token_urlsafe(12) + "A1"
    admin = User(
        organization_id=organization.id,
        email=str(payload.admin_email).lower(),
        full_name=payload.admin_full_name or str(payload.admin_email).split("@")[0],
        role=UserRole.ADMIN,
        password_hash=hash_password(temporary) if temporary else None,
    )
    db.add(admin)
    db.flush()
    credentials = (
        f"Mot de passe temporaire : {temporary} (à modifier dès la première connexion)"
        if temporary
        else "Connexion avec votre compte Google."
    )
    queue_email(
        db,
        to=admin.email,
        template="account_invitation",
        locale="fr",
        related_id=admin.id,
        params={
            "full_name": admin.full_name,
            "organization": organization.name,
            "login_url": f"{settings.frontend_url.rstrip('/')}/login",
            "credentials": credentials,
        },
    )
    audit.record(
        db,
        action="user.created",
        resource_type="user",
        resource_id=admin.id,
        organization_id=organization.id,
        details={"role": "admin", "invited": True},
    )


def create_organization(db: Session, principal: Principal, payload: OrganizationCreate) -> Organization:
    organization = Organization(
        name=payload.name,
        slug=payload.slug,
        enabled_modules=payload.enabled_modules,
        production_enabled=payload.production_enabled,
    )
    db.add(organization)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Ce slug est déjà utilisé", code="SLUG_ALREADY_USED") from exc
    if payload.admin_email:
        try:
            _invite_admin(db, organization, payload)
        except IntegrityError as exc:
            db.rollback()
            raise Conflict("Cet email est déjà utilisé", code="EMAIL_ALREADY_USED") from exc
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
