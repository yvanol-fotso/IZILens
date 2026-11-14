import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import Unauthorized, ValidationFailed
from app.core.principal import Principal
from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.core.time import as_utc, utcnow
from app.modules.audit import service as audit
from app.modules.auth.schemas import TokenPair
from app.modules.organizations.models import Organization
from app.modules.users.models import User

_INVALID = "Identifiants invalides"


def _invalid_credentials() -> Unauthorized:
    return Unauthorized(_INVALID, code="INVALID_CREDENTIALS")


def _organization_usable(db: Session, user: User) -> bool:
    if user.organization_id is None:
        return True
    organization = db.get(Organization, user.organization_id)
    return organization is not None and organization.is_active


def issue_tokens(user: User) -> TokenPair:
    access, expires_in = create_token(user_id=user.id, organization_id=user.organization_id, role=user.role, token_type="access")
    refresh, _ = create_token(user_id=user.id, organization_id=user.organization_id, role=user.role, token_type="refresh")
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=expires_in)


def authenticate(db: Session, email: str, password: str, ip: str | None) -> TokenPair:
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == email.lower()))
    now = utcnow()
    locked = user is not None and user.locked_until is not None and as_utc(user.locked_until) > now
    password_ok = verify_password(password, user.password_hash if user else None)

    if user is None or locked or not password_ok or not user.is_active or not _organization_usable(db, user):
        if user is not None and not locked:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.login_max_attempts:
                user.locked_until = now + timedelta(minutes=settings.login_lockout_minutes)
                user.failed_login_attempts = 0
        audit.record(
            db,
            action="auth.login_failed",
            resource_type="user",
            resource_id=user.id if user else None,
            organization_id=user.organization_id if user else None,
            details={"ip": ip, "locked": bool(locked)},
        )
        db.commit()
        raise _invalid_credentials()

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    audit.record(
        db,
        action="auth.login_succeeded",
        resource_type="user",
        resource_id=user.id,
        organization_id=user.organization_id,
        details={"ip": ip},
    )
    db.commit()
    return issue_tokens(user)


def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
    claims = decode_token(refresh_token, "refresh")
    user = db.get(User, uuid.UUID(claims["sub"]))
    if user is None or not user.is_active or not _organization_usable(db, user):
        raise Unauthorized("Session invalide", code="INVALID_TOKEN")
    return issue_tokens(user)


def change_password(db: Session, principal: Principal, current_password: str, new_password: str) -> None:
    user = db.get(User, principal.actor_id)
    if user is None or not verify_password(current_password, user.password_hash):
        raise ValidationFailed("Mot de passe actuel incorrect", code="WRONG_PASSWORD")
    if current_password == new_password:
        raise ValidationFailed("Le nouveau mot de passe doit être différent", code="PASSWORD_UNCHANGED")
    user.password_hash = hash_password(new_password)
    audit.record(db, action="auth.password_changed", resource_type="user", resource_id=user.id, principal=principal)
    db.commit()
