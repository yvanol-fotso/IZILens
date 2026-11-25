import csv
import io
import uuid
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.enums import STAFF_ROLES
from app.core.exceptions import NotFound
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.api_keys.models import ApiKey
from app.modules.audit import service as audit
from app.modules.audit.models import AuditLog
from app.modules.kyc.models import KycCase
from app.modules.organizations.models import Organization
from app.modules.users.models import User, UserMfa

_CSV_DANGEROUS = ("=", "+", "-", "@", "\t", "\r")


def _csv_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(_CSV_DANGEROUS) else text


def overview(db: Session) -> dict:
    now = utcnow()
    day_ago = now - timedelta(hours=24)
    staff_active = db.scalars(select(User).where(User.role.in_(list(STAFF_ROLES)), User.is_active.is_(True))).all()
    with_mfa = set(db.scalars(select(UserMfa.user_id).where(UserMfa.enabled.is_(True))).all())
    expiring = now + timedelta(days=30)
    keys = db.scalars(select(ApiKey).where(ApiKey.is_active.is_(True))).all()
    from app.core.time import as_utc

    return {
        "failed_logins_24h": db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.action.in_(["auth.login_failed", "auth.mfa_failed"]), AuditLog.created_at >= day_ago
            )
        )
        or 0,
        "locked_accounts": sum(
            1 for u in db.scalars(select(User).where(User.locked_until.is_not(None))).all() if as_utc(u.locked_until) > now
        ),
        "users_total": db.scalar(select(func.count(User.id))) or 0,
        "users_without_organization": db.scalar(
            select(func.count(User.id)).where(User.organization_id.is_(None), User.role.notin_(list(STAFF_ROLES)))
        )
        or 0,
        "staff_accounts": len(staff_active),
        "staff_without_mfa": sum(1 for u in staff_active if u.id not in with_mfa),
        "active_api_keys": len(keys),
        "sandbox_api_keys": sum(1 for k in keys if k.environment == "sandbox"),
        "api_keys_expiring_30d": sum(1 for k in keys if k.expires_at is not None and as_utc(k.expires_at) <= expiring),
        "disabled_organizations": db.scalar(select(func.count(Organization.id)).where(Organization.is_active.is_(False))) or 0,
    }


def locked_accounts(db: Session) -> list[dict]:
    from app.core.time import as_utc

    now = utcnow()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "organization_id": str(u.organization_id) if u.organization_id else None,
            "locked_until": as_utc(u.locked_until).isoformat(),
        }
        for u in db.scalars(select(User).where(User.locked_until.is_not(None))).all()
        if as_utc(u.locked_until) > now
    ]


def _user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFound("Utilisateur introuvable", code="USER_NOT_FOUND")
    return user


def unlock(db: Session, principal: Principal, user_id: uuid.UUID) -> None:
    user = _user(db, user_id)
    user.locked_until, user.failed_login_attempts = None, 0
    audit.record(
        db,
        action="security.account_unlocked",
        resource_type="user",
        resource_id=user.id,
        principal=principal,
        organization_id=user.organization_id,
    )
    db.commit()


def revoke_sessions(db: Session, principal: Principal, user_id: uuid.UUID) -> None:
    user = _user(db, user_id)
    user.token_version += 1
    audit.record(
        db,
        action="security.sessions_revoked",
        resource_type="user",
        resource_id=user.id,
        principal=principal,
        organization_id=user.organization_id,
    )
    db.commit()


def events_csv(rows: list[AuditLog]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "created_at",
            "action",
            "actor_type",
            "actor_id",
            "organization_id",
            "resource_type",
            "resource_id",
            "ip_address",
            "request_id",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                _csv_cell(v)
                for v in (
                    r.created_at.isoformat() if r.created_at else "",
                    r.action,
                    r.actor_type.value,
                    r.actor_id,
                    r.organization_id,
                    r.resource_type,
                    r.resource_id,
                    r.ip_address,
                    r.request_id,
                )
            ]
        )
    return buffer.getvalue()


def kyc_report(db: Session, *, organization_id: uuid.UUID | None, start, end, include_sandbox: bool) -> dict:
    from app.core.time import as_utc

    query = select(KycCase)
    if organization_id:
        query = query.where(KycCase.organization_id == organization_id)
    if start:
        query = query.where(KycCase.created_at >= start)
    if end:
        query = query.where(KycCase.created_at < end)
    if not include_sandbox:
        query = query.where(KycCase.is_sandbox.is_(False))
    cases = db.scalars(query.limit(50000)).all()
    by_status: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    by_country: dict[str, int] = {}
    by_day: dict[str, int] = {}
    durations: list[float] = []
    for c in cases:
        by_status[c.status.value] = by_status.get(c.status.value, 0) + 1
        by_risk[c.risk_level.value if c.risk_level else "unknown"] = (
            by_risk.get(c.risk_level.value if c.risk_level else "unknown", 0) + 1
        )
        by_country[c.country_code] = by_country.get(c.country_code, 0) + 1
        day = as_utc(c.created_at).date().isoformat()
        by_day[day] = by_day.get(day, 0) + 1
        if c.completed_at and c.status.value in ("verified", "not_verified"):
            durations.append((as_utc(c.completed_at) - as_utc(c.created_at)).total_seconds() / 3600)
    decided = by_status.get("verified", 0) + by_status.get("not_verified", 0)
    return {
        "total": len(cases),
        "by_status": by_status,
        "by_risk": by_risk,
        "by_country": by_country,
        "by_day": dict(sorted(by_day.items())),
        "verified_rate": round(by_status.get("verified", 0) / decided, 4) if decided else None,
        "avg_resolution_hours": round(sum(durations) / len(durations), 2) if durations else None,
        "pending_review": by_status.get("manual_review", 0),
    }


def organizations_report(db: Session) -> list[dict]:
    rows = []
    for org in db.scalars(select(Organization).order_by(Organization.created_at)).all():
        rows.append(
            {
                "organization_id": str(org.id),
                "name": org.name,
                "is_active": org.is_active,
                "production_enabled": org.production_enabled,
                "modules": org.enabled_modules,
                "users": db.scalar(select(func.count(User.id)).where(User.organization_id == org.id)) or 0,
                "cases": db.scalar(
                    select(func.count(KycCase.id)).where(KycCase.organization_id == org.id, KycCase.is_sandbox.is_(False))
                )
                or 0,
                "active_api_keys": db.scalar(
                    select(func.count(ApiKey.id)).where(ApiKey.organization_id == org.id, ApiKey.is_active.is_(True))
                )
                or 0,
            }
        )
    return rows
