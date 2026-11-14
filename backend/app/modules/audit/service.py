import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.enums import ActorType
from app.core.context import request_id_ctx
from app.core.principal import Principal
from app.modules.audit.models import AuditLog


def record(
    db: Session,
    *,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | str | None = None,
    principal: Principal | None = None,
    organization_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Ajoute une ligne d'audit dans la transaction courante ; ne doit jamais contenir de donnée personnelle."""
    request_id = request_id_ctx.get()
    db.add(
        AuditLog(
            organization_id=organization_id or (principal.organization_id if principal else None),
            actor_type=principal.actor_type if principal else ActorType.SYSTEM,
            actor_id=str(principal.actor_id) if principal else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=principal.ip if principal else None,
            request_id=None if request_id == "-" else request_id,
            details=details or {},
        )
    )


def list_logs(
    db: Session,
    *,
    organization_id: uuid.UUID | None,
    action: str | None,
    resource_id: str | None,
    page: int,
    page_size: int,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    if organization_id:
        query = query.where(AuditLog.organization_id == organization_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return list(rows), total
