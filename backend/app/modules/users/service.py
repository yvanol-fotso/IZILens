import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import STAFF_ROLES, UserRole
from app.core.config import get_settings
from app.core.exceptions import Conflict, Forbidden, NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.security import hash_password
from app.modules.audit import service as audit
from app.modules.organizations.models import Organization
from app.modules.users.models import User
from app.modules.users.schemas import STAFF_ASSIGNABLE, TENANT_ROLES, UserCreate, UserUpdate


def _target_organization(principal: Principal, requested: uuid.UUID | None) -> uuid.UUID:
    if principal.role == UserRole.SUPER_ADMIN:
        if requested is None:
            raise ValidationFailed("organization_id est requis", code="ORGANIZATION_REQUIRED")
        return requested
    return principal.organization_id  # type: ignore[return-value]  # un ADMIN a toujours une organisation


def create_user(db: Session, principal: Principal, payload: UserCreate) -> User:
    if payload.password is None and not get_settings().oidc_enabled:
        raise ValidationFailed("Un mot de passe est requis tant que la connexion Google est désactivée", code="PASSWORD_REQUIRED")
    if payload.role in STAFF_ASSIGNABLE:
        if principal.role != UserRole.SUPER_ADMIN:
            raise Forbidden("Seul le super administrateur crée les comptes de la plateforme", code="INSUFFICIENT_ROLE")
        organization_id = None
    else:
        organization_id = _target_organization(principal, payload.organization_id)
        if db.get(Organization, organization_id) is None:
            raise NotFound("Organisation introuvable", code="ORGANIZATION_NOT_FOUND")
    user = User(
        organization_id=organization_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password) if payload.password else None,
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


def _manageable(db: Session, principal: Principal, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    in_scope = user is not None and (principal.role == UserRole.SUPER_ADMIN or user.organization_id == principal.organization_id)
    if not in_scope:
        raise NotFound("Utilisateur introuvable", code="USER_NOT_FOUND")
    if user.role in STAFF_ROLES and principal.role != UserRole.SUPER_ADMIN:
        raise Forbidden("Action interdite", code="FORBIDDEN")
    return user


def set_user_active(db: Session, principal: Principal, user_id: uuid.UUID, is_active: bool) -> User:
    return update_user(db, principal, user_id, UserUpdate(is_active=is_active))


def update_user(db: Session, principal: Principal, user_id: uuid.UUID, payload: UserUpdate) -> User:
    user = _manageable(db, principal, user_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if user.id == principal.actor_id and ({"role", "is_active", "organization_id"} & set(changes)):
        raise Forbidden("Vous ne pouvez pas modifier votre propre rôle ou statut", code="SELF_UPDATE_FORBIDDEN")
    if user.role == UserRole.SUPER_ADMIN and principal.actor_id != user.id:
        raise Forbidden("Action interdite", code="FORBIDDEN")
    if "organization_id" in changes:
        if principal.role != UserRole.SUPER_ADMIN:
            raise Forbidden("Seul le super administrateur rattache un compte à une organisation", code="INSUFFICIENT_ROLE")
        if db.get(Organization, changes["organization_id"]) is None:
            raise NotFound("Organisation introuvable", code="ORGANIZATION_NOT_FOUND")
        user.organization_id = changes["organization_id"]
    if "role" in changes:
        new_role: UserRole = changes["role"]
        if new_role in STAFF_ASSIGNABLE:
            if principal.role != UserRole.SUPER_ADMIN:
                raise Forbidden("Seul le super administrateur attribue un rôle de la plateforme", code="INSUFFICIENT_ROLE")
            user.organization_id = None
        elif new_role in TENANT_ROLES and user.organization_id is None:
            raise ValidationFailed("Rattachez d'abord le compte à une organisation", code="ORGANIZATION_REQUIRED")
        if new_role != user.role:
            user.role = new_role
            user.token_version += 1  # les sessions ouvertes perdent l'ancien rôle
    if "full_name" in changes:
        user.full_name = changes["full_name"]
    if "is_active" in changes:
        user.is_active = changes["is_active"]
        if not user.is_active:
            user.token_version += 1
    audit.record(
        db,
        action="user.updated",
        resource_type="user",
        resource_id=user.id,
        principal=principal,
        organization_id=user.organization_id,
        details={"fields": sorted(changes)},
    )
    db.commit()
    return user


def update_profile(db: Session, principal: Principal, full_name: str) -> User:
    user = db.get(User, principal.actor_id)
    if user is None:
        raise NotFound("Utilisateur introuvable", code="USER_NOT_FOUND")
    user.full_name = full_name
    audit.record(db, action="user.profile_updated", resource_type="user", resource_id=user.id, principal=principal)
    db.commit()
    return user
