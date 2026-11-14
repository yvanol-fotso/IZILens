import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.core.exceptions import Conflict, Forbidden, NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.security import hash_password
from app.modules.audit import service as audit
from app.modules.organizations.models import Organization
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


def _target_organization(principal: Principal, requested: uuid.UUID | None) -> uuid.UUID:
    if principal.role == UserRole.SUPER_ADMIN:
        if requested is None:
            raise ValidationFailed("organization_id est requis", code="ORGANIZATION_REQUIRED")
        return requested
    return principal.organization_id  # type: ignore[return-value]  # un ADMIN a toujours une organisation


def create_user(db: Session, principal: Principal, payload: UserCreate) -> User:
    organization_id = _target_organization(principal, payload.organization_id)
    if db.get(Organization, organization_id) is None:
        raise NotFound("Organisation introuvable", code="ORGANIZATION_NOT_FOUND")
    user = User(
        organization_id=organization_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Cet email est déjà utilisé", code="EMAIL_ALREADY_USED") from exc
    audit.record(
        db,
        action="user.created",
        resource_type="user",
        resource_id=user.id,
        principal=principal,
        organization_id=organization_id,
        details={"role": user.role.value},
    )
    db.commit()
    return user


def list_users(
    db: Session, principal: Principal, organization_id: uuid.UUID | None, page: int, page_size: int
) -> tuple[list[User], int]:
    query = select(User)
    scope = principal.organization_id if principal.role != UserRole.SUPER_ADMIN else organization_id
    if scope:
        query = query.where(User.organization_id == scope)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return list(rows), total


def set_user_active(db: Session, principal: Principal, user_id: uuid.UUID, is_active: bool) -> User:
    user = db.get(User, user_id)
    in_scope = user is not None and (principal.role == UserRole.SUPER_ADMIN or user.organization_id == principal.organization_id)
    if not in_scope:
        raise NotFound("Utilisateur introuvable", code="USER_NOT_FOUND")
    if user.id == principal.actor_id:
        raise Forbidden("Vous ne pouvez pas modifier votre propre statut", code="SELF_UPDATE_FORBIDDEN")
    if user.role == UserRole.SUPER_ADMIN and principal.role != UserRole.SUPER_ADMIN:
        raise Forbidden("Action interdite", code="FORBIDDEN")
    user.is_active = is_active
    audit.record(
        db,
        action="user.activated" if is_active else "user.deactivated",
        resource_type="user",
        resource_id=user.id,
        principal=principal,
        organization_id=user.organization_id,
    )
    db.commit()
    return user
