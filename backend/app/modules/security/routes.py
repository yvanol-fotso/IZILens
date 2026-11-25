import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.permissions import ROLES
from app.core.principal import Principal
from app.modules.audit import service as audit
from app.modules.audit.schemas import AuditLogRead
from app.modules.auth import mfa
from app.modules.security import service

router = APIRouter(prefix="/admin", tags=["Back-office : sécurité et rapports"])
reader = require_access(UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE, tenant=False)
super_only = require_access(UserRole.SUPER_ADMIN, tenant=False)
reports = require_access(UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE, UserRole.BILLING_MANAGER, tenant=False)


@router.get("/roles", summary="Catalogue des rôles et permissions")
def roles(_: Principal = Depends(require_access(UserRole.SUPER_ADMIN, UserRole.PLATFORM_COMPLIANCE, tenant=False))):
    return ROLES


@router.get("/security/overview", summary="Centre de sécurité : indicateurs")
def overview(_: Principal = Depends(reader), db: Session = Depends(get_db)):
    return service.overview(db)


@router.get("/security/locked-accounts", summary="Comptes verrouillés")
def locked(_: Principal = Depends(reader), db: Session = Depends(get_db)):
    return service.locked_accounts(db)


@router.post("/security/users/{user_id}/unlock", status_code=204, summary="Déverrouiller un compte")
def unlock(user_id: uuid.UUID, principal: Principal = Depends(super_only), db: Session = Depends(get_db)):
    service.unlock(db, principal, user_id)
    return Response(status_code=204)


@router.post(
    "/security/users/{user_id}/revoke-sessions", status_code=204, summary="Révoquer toutes les sessions d'un utilisateur"
)
def revoke(user_id: uuid.UUID, principal: Principal = Depends(super_only), db: Session = Depends(get_db)):
    service.revoke_sessions(db, principal, user_id)
    return Response(status_code=204)


@router.post(
    "/security/users/{user_id}/reset-mfa",
    status_code=204,
    summary="Réinitialiser l'authentification à deux facteurs (appareil perdu)",
)
def reset_mfa(user_id: uuid.UUID, principal: Principal = Depends(super_only), db: Session = Depends(get_db)):
    mfa.admin_reset(db, principal, user_id)
    return Response(status_code=204)


@router.get(
    "/security/events", response_model=Page[AuditLogRead], summary="Événements de sécurité (connexions, MFA, verrouillages)"
)
def events(
    action_prefix: str = Query("auth.", max_length=32),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    since: datetime | None = None,
    _: Principal = Depends(reader),
    db: Session = Depends(get_db),
):
    items, total = audit.list_logs(
        db,
        organization_id=None,
        action=None,
        resource_id=None,
        page=page,
        page_size=page_size,
        action_prefix=action_prefix,
        since=since,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/security/events.csv", summary="Export CSV des événements (5 000 lignes maximum)")
def events_csv(
    action_prefix: str = Query("auth.", max_length=32),
    since: datetime | None = None,
    principal: Principal = Depends(reader),
    db: Session = Depends(get_db),
):
    items, _ = audit.list_logs(
        db, organization_id=None, action=None, resource_id=None, page=1, page_size=5000, action_prefix=action_prefix, since=since
    )
    audit.record(db, action="security.events_exported", resource_type="audit", principal=principal)
    db.commit()
    return Response(
        service.events_csv(items),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="security-events.csv"'},
    )


@router.get("/reports/kyc", summary="Rapport KYC : statuts, risques, pays, délais")
def kyc_report(
    organization_id: uuid.UUID | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    include_sandbox: bool = False,
    format: str = Query("json", pattern=r"^(json|csv)$"),
    _: Principal = Depends(reports),
    db: Session = Depends(get_db),
):
    data = service.kyc_report(db, organization_id=organization_id, start=start, end=end, include_sandbox=include_sandbox)
    if format == "csv":
        lines = ["day,cases", *[f"{day},{count}" for day, count in data["by_day"].items()]]
        return Response(
            "\n".join(lines) + "\n",
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="kyc-report.csv"'},
        )
    return data


@router.get("/reports/organizations", summary="Rapport par organisation")
def organizations_report(_: Principal = Depends(reports), db: Session = Depends(get_db)):
    return service.organizations_report(db)
