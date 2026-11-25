import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import totp
from app.core.config import get_settings
from app.core.exceptions import Conflict, NotFound, Unauthorized, ValidationFailed
from app.core.principal import Principal
from app.core.security import digests_match, keyed_digest, verify_password
from app.modules.audit import service as audit
from app.modules.users.models import User, UserMfa

RECOVERY_CODE_COUNT = 8


def _record(db: Session, user_id) -> UserMfa | None:
    return db.scalar(select(UserMfa).where(UserMfa.user_id == user_id))


def is_enabled(db: Session, user_id) -> bool:
    record = _record(db, user_id)
    return bool(record and record.enabled)


def _new_recovery_codes() -> tuple[list[str], list[str]]:
    codes = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(RECOVERY_CODE_COUNT)]
    return codes, [keyed_digest("recovery:" + c) for c in codes]


def check_login_code(db: Session, user: User, code: str) -> bool:
    """Accepte un code TOTP (non rejoué) ou un code de secours à usage unique."""
    record = _record(db, user.id)
    if record is None or not record.enabled:
        return False
    step = totp.verify(record.secret["secret"], code, last_used_step=record.last_used_step)
    if step is not None:
        record.last_used_step = step
        return True
    digest = keyed_digest("recovery:" + code.strip().lower())
    for stored in record.recovery_codes:
        if digests_match(stored, digest):
            record.recovery_codes = [c for c in record.recovery_codes if c != stored]
            return True
    return False


def status(db: Session, principal: Principal) -> dict:
    record = _record(db, principal.actor_id)
    return {
        "enabled": bool(record and record.enabled),
        "recovery_codes_left": len(record.recovery_codes) if record and record.enabled else 0,
    }


def enroll(db: Session, principal: Principal) -> dict:
    user = db.get(User, principal.actor_id)
    record = _record(db, user.id)
    if record and record.enabled:
        raise Conflict("L'authentification à deux facteurs est déjà activée", code="MFA_ALREADY_ENABLED")
    secret = totp.new_secret()
    if record is None:
        db.add(UserMfa(user_id=user.id, secret={"secret": secret}))
    else:
        record.secret = {"secret": secret}
    audit.record(db, action="auth.mfa_enrollment_started", resource_type="user", resource_id=user.id, principal=principal)
    db.commit()
    return {"secret": secret, "otpauth_uri": totp.provisioning_uri(secret, user.email, get_settings().mfa_issuer)}


def activate(db: Session, principal: Principal, code: str) -> dict:
    record = _record(db, principal.actor_id)
    if record is None or record.enabled:
        raise NotFound("Aucune activation en cours", code="MFA_ENROLLMENT_NOT_FOUND")
    step = totp.verify(record.secret["secret"], code)
    if step is None:
        raise ValidationFailed("Code invalide", code="INVALID_MFA_CODE")
    codes, digests = _new_recovery_codes()
    record.enabled, record.enrolled_at, record.recovery_codes, record.last_used_step = True, datetime.now(UTC), digests, step
    audit.record(db, action="auth.mfa_enabled", resource_type="user", resource_id=principal.actor_id, principal=principal)
    db.commit()
    return {"enabled": True, "recovery_codes": codes}


def regenerate_recovery_codes(db: Session, principal: Principal, code: str) -> dict:
    user = db.get(User, principal.actor_id)
    record = _record(db, user.id)
    if record is None or not record.enabled or not check_login_code(db, user, code):
        raise ValidationFailed("Code invalide", code="INVALID_MFA_CODE")
    codes, digests = _new_recovery_codes()
    record.recovery_codes = digests
    audit.record(db, action="auth.mfa_recovery_regenerated", resource_type="user", resource_id=user.id, principal=principal)
    db.commit()
    return {"recovery_codes": codes}


def disable(db: Session, principal: Principal, password: str, code: str) -> None:
    user = db.get(User, principal.actor_id)
    record = _record(db, user.id)
    if record is None or not record.enabled:
        raise NotFound("L'authentification à deux facteurs n'est pas activée", code="MFA_NOT_ENABLED")
    if not verify_password(password, user.password_hash) or not check_login_code(db, user, code):
        raise Unauthorized("Mot de passe ou code invalide", code="INVALID_CREDENTIALS")
    db.delete(record)
    user.token_version += 1
    audit.record(db, action="auth.mfa_disabled", resource_type="user", resource_id=user.id, principal=principal)
    db.commit()


def admin_reset(db: Session, principal: Principal, user_id) -> None:
    record = _record(db, user_id)
    if record is None:
        raise NotFound("Aucune authentification à deux facteurs à réinitialiser", code="MFA_NOT_ENABLED")
    user = db.get(User, user_id)
    db.delete(record)
    user.token_version += 1
    audit.record(
        db,
        action="security.mfa_reset",
        resource_type="user",
        resource_id=user_id,
        principal=principal,
        organization_id=user.organization_id,
    )
    db.commit()
