from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.audit import service
from app.modules.audit.schemas import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=Page[AuditLogRead], summary="Consulter le journal d'audit")
def list_audit_logs(
    action: str | None = Query(None, max_length=64),
    resource_id: str | None = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    principal: Principal = Depends(require_access(UserRole.SUPER_ADMIN, UserRole.ADMIN, tenant=False)),
    db: Session = Depends(get_db),
):
    scope = None if principal.role == UserRole.SUPER_ADMIN else principal.organization_id
    items, total = service.list_logs(
        db, organization_id=scope, action=action, resource_id=resource_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)
