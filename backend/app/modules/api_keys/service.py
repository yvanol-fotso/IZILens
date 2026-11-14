import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.core.exceptions import Forbidden, NotFound, Unauthorized
from app.core.principal import Principal
from app.core.security import digests_match, generate_api_key, keyed_digest, parse_api_key_prefix
from app.core.time import as_utc, utcnow
from app.modules.api_keys.models import ApiKey
from app.modules.api_keys.schemas import ApiKeyCreate
from app.modules.audit import service as audit
from app.modules.organizations.models import Organization

_LAST_USED_REFRESH = timedelta(minutes=1)


def create_api_key(db: Session, principal: Principal, payload: ApiKeyCreate) -> tuple[ApiKey, str]:
    if principal.organization_id is None:
        raise Forbidden("Une organisation est requise", code="ORGANIZATION_REQUIRED")
    full_key, prefix, key_hash = generate_api_key()
    api_key = ApiKey(
        organization_id=principal.organization_id,
        created_by_user_id=principal.actor_id,
        name=payload.name,
        prefix=prefix,
        key_hash=key_hash,
        expires_at=utcnow() + timedelta(days=payload.expires_in_days) if payload.expires_in_days else None,
    )
    db.add(api_key)
    db.flush()
    audit.record(
        db,
        action="api_key.created",
        resource_type="api_key",
        resource_id=api_key.id,
        principal=principal,
        details={"prefix": prefix},
    )
    db.commit()
    return api_key, full_key


def list_api_keys(db: Session, principal: Principal) -> list[ApiKey]:
    return list(
        db.scalars(
            select(ApiKey).where(ApiKey.organization_id == principal.organization_id).order_by(ApiKey.created_at.desc())
        ).all()
    )


def revoke_api_key(db: Session, principal: Principal, key_id: uuid.UUID) -> ApiKey:
    api_key = db.get(ApiKey, key_id)
    if api_key is None or api_key.organization_id != principal.organization_id:
        raise NotFound("Clé API introuvable", code="API_KEY_NOT_FOUND")
    if api_key.revoked_at is None:
        api_key.is_active = False
        api_key.revoked_at = utcnow()
        audit.record(
            db,
            action="api_key.revoked",
            resource_type="api_key",
            resource_id=api_key.id,
            principal=principal,
            details={"prefix": api_key.prefix},
        )
        db.commit()
    return api_key


def authenticate_api_key(db: Session, raw_key: str, ip: str | None) -> Principal:
    """Résout une clé API en identité ; toute anomalie renvoie le même message pour ne rien révéler."""
    invalid = Unauthorized("Clé API invalide", code="INVALID_API_KEY")
    prefix = parse_api_key_prefix(raw_key)
    if prefix is None:
        raise invalid
    row = db.execute(
        select(ApiKey, Organization).join(Organization, Organization.id == ApiKey.organization_id).where(ApiKey.prefix == prefix)
    ).first()
    if row is None:
        raise invalid
    api_key, organization = row
    if not digests_match(keyed_digest(raw_key), api_key.key_hash):
        raise invalid
    now = utcnow()
    expired = api_key.expires_at is not None and as_utc(api_key.expires_at) <= now
    if not api_key.is_active or api_key.revoked_at is not None or expired or not organization.is_active:
        raise invalid
    if api_key.last_used_at is None or now - as_utc(api_key.last_used_at) > _LAST_USED_REFRESH:
        api_key.last_used_at = now
        db.commit()
    return Principal(
        kind="api_key",
        actor_id=api_key.id,
        organization_id=organization.id,
        role=UserRole.INTEGRATION,
        enabled_modules=frozenset(organization.enabled_modules),
        ip=ip,
    )
