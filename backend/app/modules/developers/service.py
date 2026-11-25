import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.constants import DEFAULT_MODULES
from app.common.enums import UserRole
from app.core.config import get_settings
from app.core.exceptions import Conflict, NotFound, ValidationFailed
from app.core.numbering import next_value
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.api_keys.models import ApiKey
from app.modules.audit import service as audit
from app.modules.developers.models import DeveloperAccessRequest
from app.modules.developers.schemas import AccessDecision, AccessRequestCreate, AccessRequestRead, DeveloperOverview
from app.modules.notifications.service import queue_email
from app.modules.organizations.models import Organization
from app.modules.users.models import User
from app.modules.webhooks.models import WebhookEndpoint


def create_request(db: Session, principal: Principal, payload: AccessRequestCreate) -> DeveloperAccessRequest:
    user = db.get(User, principal.actor_id)
    organization = db.get(Organization, user.organization_id) if user.organization_id else None
    if payload.environment == "sandbox" and organization is not None:
        raise Conflict("Votre compte est déjà rattaché à une organisation", code="ALREADY_HAS_ORGANIZATION")
    if payload.environment == "production":
        if organization is None or user.role != UserRole.ADMIN:
            raise Conflict(
                "Seul l'administrateur d'une organisation demande l'accès Production", code="ORGANIZATION_ADMIN_REQUIRED"
            )
        if organization.production_enabled:
            raise Conflict("L'accès Production est déjà activé", code="ALREADY_PRODUCTION")
    pending = db.scalar(
        select(DeveloperAccessRequest.id).where(
            DeveloperAccessRequest.user_id == user.id, DeveloperAccessRequest.status == "pending"
        )
    )
    if pending:
        raise Conflict("Une demande est déjà en cours d'examen", code="REQUEST_ALREADY_PENDING")
    request = DeveloperAccessRequest(
        reference=f"DEV-{utcnow().year}-{next_value(db, f'DEV-{utcnow().year}'):06d}",
        user_id=user.id,
        organization_id=organization.id if organization else None,
        **payload.model_dump(),
    )
    db.add(request)
    db.flush()
    audit.record(
        db,
        action="developer.access_requested",
        resource_type="developer_request",
        resource_id=request.id,
        principal=principal,
        organization_id=request.organization_id,
        details={"environment": payload.environment},
    )
    db.commit()
    return request


def my_requests(db: Session, principal: Principal) -> list[DeveloperAccessRequest]:
    return list(
        db.scalars(
            select(DeveloperAccessRequest)
            .where(DeveloperAccessRequest.user_id == principal.actor_id)
            .order_by(DeveloperAccessRequest.created_at.desc())
        ).all()
    )


def list_requests(db: Session, status: str | None, page: int, page_size: int) -> tuple[list[DeveloperAccessRequest], int]:
    query = select(DeveloperAccessRequest)
    if status:
        query = query.where(DeveloperAccessRequest.status == status)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(
        query.order_by(DeveloperAccessRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(rows), total


def _slug_for(db: Session, wanted: str | None, company: str) -> str:
    base = wanted or (re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")[:40] or "organisation")
    base = base if len(base) >= 3 else f"{base}-org"
    slug, counter = base, 1
    while db.scalar(select(Organization.id).where(Organization.slug == slug)):
        counter += 1
        slug = f"{base[:44]}-{counter}"
    return slug


def decide(db: Session, principal: Principal, request_id: uuid.UUID, payload: AccessDecision) -> DeveloperAccessRequest:
    request = db.get(DeveloperAccessRequest, request_id)
    if request is None:
        raise NotFound("Demande introuvable", code="REQUEST_NOT_FOUND")
    if request.status != "pending":
        raise Conflict("Cette demande a déjà été traitée", code="INVALID_STATE")
    user = db.get(User, request.user_id)
    if payload.decision == "rejected" and not (payload.note and payload.note.strip()):
        raise ValidationFailed("Un motif est requis pour un refus", code="NOTE_REQUIRED")
    if payload.decision == "approved":
        if request.environment == "sandbox":
            organization = Organization(
                name=request.company_name,
                slug=_slug_for(db, payload.organization_slug, request.company_name),
                enabled_modules=list(DEFAULT_MODULES),
                production_enabled=False,
            )
            db.add(organization)
            db.flush()
            user.organization_id, user.role = organization.id, UserRole.ADMIN
            user.token_version += 1
            request.organization_id = organization.id
        else:
            organization = db.get(Organization, request.organization_id)
            organization.production_enabled = True
    request.status = payload.decision
    request.decision_note, request.decided_by_user_id, request.decided_at = payload.note, principal.actor_id, utcnow()
    queue_email(
        db,
        to=user.email,
        template="access_decision",
        locale="fr",
        related_id=request.id,
        params={
            "full_name": user.full_name,
            "reference": request.reference,
            "decision": "approuvée" if payload.decision == "approved" else "refusée",
            "note": payload.note or "",
        },
    )
    audit.record(
        db,
        action=f"developer.access_{payload.decision}",
        resource_type="developer_request",
        resource_id=request.id,
        principal=principal,
        organization_id=request.organization_id,
        details={"environment": request.environment},
    )
    db.commit()
    return request


def overview(db: Session, principal: Principal) -> DeveloperOverview:
    user = db.get(User, principal.actor_id)
    organization = db.get(Organization, user.organization_id) if user.organization_id else None
    pending = db.scalar(
        select(DeveloperAccessRequest).where(
            DeveloperAccessRequest.user_id == user.id, DeveloperAccessRequest.status == "pending"
        )
    )
    keys = {"sandbox": 0, "production": 0}
    webhooks = 0
    if organization:
        for env, count in db.execute(
            select(ApiKey.environment, func.count(ApiKey.id))
            .where(ApiKey.organization_id == organization.id, ApiKey.is_active.is_(True))
            .group_by(ApiKey.environment)
        ).all():
            keys[env] = count
        webhooks = (
            db.scalar(
                select(func.count(WebhookEndpoint.id)).where(
                    WebhookEndpoint.organization_id == organization.id, WebhookEndpoint.is_active.is_(True)
                )
            )
            or 0
        )
    return DeveloperOverview(
        has_organization=organization is not None,
        organization=organization.name if organization else None,
        sandbox=organization is not None,
        production=bool(organization and organization.production_enabled),
        pending_request=AccessRequestRead.model_validate(pending) if pending else None,
        api_keys=keys,
        webhooks=webhooks,
        base_url_hint=f"{get_settings().frontend_url.rstrip('/')}/api/v1",
    )
