import uuid

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.common.enums import STAFF_ROLES
from app.core.config import get_settings
from app.core.exceptions import Conflict, NotFound, ValidationFailed
from app.core.numbering import next_value
from app.core.principal import Principal
from app.core.rate_limit import limiter
from app.core.security import keyed_digest
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.notifications.service import queue_email
from app.modules.public_requests.models import PublicRequest, PublicRequestEvent
from app.modules.public_requests.schemas import TEAM_BY_TYPE, ContactRequestIn, RequestDetail, RequestEventRead, RequestSummary
from app.modules.users.models import User

TRANSITIONS = {
    "new": {"in_review", "closed"},
    "in_review": {"contacted", "qualified", "closed"},
    "contacted": {"in_review", "qualified", "closed"},
    "qualified": {"contacted", "closed"},
    "closed": {"in_review"},
}
PRIVACY_VERSION = "2026-11"


def _event(
    db: Session,
    request: PublicRequest,
    event_type: str,
    *,
    actor: uuid.UUID | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    note: str | None = None,
) -> None:
    db.add(
        PublicRequestEvent(
            request=request,
            seq=len(request.events) + 1,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            actor_user_id=actor,
            note={"note": note} if note else None,
            created_at=utcnow(),
        )
    )


def create_request(db: Session, payload: ContactRequestIn, ip: str | None) -> PublicRequest:
    settings = get_settings()
    fields = payload.fields
    email_hash = keyed_digest("email:" + fields.email)
    limiter.check(f"public-ip:{ip}", settings.public_request_limit_per_10min, 600)
    limiter.check(f"public-email:{email_hash}", 5, 3600)
    request_type = "demo" if payload.kind == "demo" else fields.type
    team = TEAM_BY_TYPE.get(request_type, "sales")
    reference = f"IZL-{utcnow().year}-{next_value(db, f'REQ-{utcnow().year}'):06d}"
    contact = fields.model_dump(include={"full_name", "company", "email", "role", "phone", "subject", "message"})
    request = PublicRequest(
        reference=reference,
        kind=payload.kind,
        request_type=request_type,
        team=team,
        locale=payload.locale,
        country=fields.country,
        sector=fields.sector,
        volume=fields.volume,
        services=fields.services,
        payload=contact,
        email_hash=email_hash,
        ip_hash=keyed_digest("ip:" + ip) if ip else None,
        consent_privacy=True,
        consent_marketing=fields.consent_marketing,
        consent_version=PRIVACY_VERSION,
    )
    db.add(request)
    db.flush()
    _event(db, request, "received", to_status="new")
    queue_email(
        db,
        to=fields.email,
        template="request_confirmation",
        locale=payload.locale,
        related_id=request.id,
        params={
            "full_name": fields.full_name,
            "reference": reference,
            "team": "commerciale" if team == "sales" and payload.locale == "fr" else team,
        },
    )
    internal = {"sales": settings.sales_email, "partnerships": settings.partnerships_email}.get(team)
    if internal:
        queue_email(
            db,
            to=internal,
            template="request_internal",
            locale="fr",
            related_id=request.id,
            params={"team": team, "reference": reference, "kind": payload.kind, "type": request_type},
        )
    db.commit()
    return request


def _summary(r: PublicRequest) -> RequestSummary:
    return RequestSummary.model_validate(r)


def get_request(db: Session, request_id: uuid.UUID) -> PublicRequest:
    request = db.get(PublicRequest, request_id)
    if request is None:
        raise NotFound("Demande introuvable", code="REQUEST_NOT_FOUND")
    return request


def detail(request: PublicRequest) -> RequestDetail:
    return RequestDetail(
        **_summary(request).model_dump(),
        contact=request.payload,
        consent_privacy=request.consent_privacy,
        consent_marketing=request.consent_marketing,
        consent_version=request.consent_version,
        events=[
            RequestEventRead(
                seq=e.seq,
                event_type=e.event_type,
                from_status=e.from_status,
                to_status=e.to_status,
                actor_user_id=e.actor_user_id,
                note=(e.note or {}).get("note"),
                created_at=e.created_at,
            )
            for e in request.events
        ],
    )


def list_requests(
    db: Session,
    *,
    status: str | None,
    kind: str | None,
    team: str | None,
    search: str | None,
    assigned_to: uuid.UUID | None,
    page: int,
    page_size: int,
) -> tuple[list[PublicRequest], int]:
    query = select(PublicRequest)
    if status:
        query = query.where(PublicRequest.status == status)
    if kind:
        query = query.where(PublicRequest.kind == kind)
    if team:
        query = query.where(PublicRequest.team == team)
    if assigned_to:
        query = query.where(PublicRequest.assigned_to_user_id == assigned_to)
    if search:
        pattern = f"%{search.strip()[:64]}%"
        query = query.where(or_(PublicRequest.reference.ilike(pattern), cast(PublicRequest.id, String).ilike(pattern)))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(PublicRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return list(rows), total


def change_status(db: Session, principal: Principal, request: PublicRequest, status: str, note: str | None) -> PublicRequest:
    if status == request.status:
        raise Conflict("Le statut est déjà celui demandé", code="INVALID_STATE")
    if status not in TRANSITIONS[request.status]:
        raise Conflict(f"Transition {request.status} → {status} interdite", code="INVALID_TRANSITION")
    _event(db, request, "status_changed", actor=principal.actor_id, from_status=request.status, to_status=status, note=note)
    request.status = status
    request.closed_at = utcnow() if status == "closed" else None
    audit.record(
        db,
        action="public_request.status_changed",
        resource_type="public_request",
        resource_id=request.id,
        principal=principal,
        details={"to": status},
    )
    db.commit()
    return request


def assign(db: Session, principal: Principal, request: PublicRequest, assignee_id: uuid.UUID | None) -> PublicRequest:
    target = assignee_id or principal.actor_id
    user = db.get(User, target)
    if user is None or not user.is_active or user.role not in STAFF_ROLES:
        raise ValidationFailed("Seuls les comptes de la plateforme peuvent traiter une demande", code="ASSIGNEE_INVALID")
    request.assigned_to_user_id = user.id
    _event(db, request, "assigned", actor=principal.actor_id, note=str(user.id))
    audit.record(
        db, action="public_request.assigned", resource_type="public_request", resource_id=request.id, principal=principal
    )
    db.commit()
    return request


def add_note(db: Session, principal: Principal, request: PublicRequest, note: str) -> PublicRequest:
    _event(db, request, "note", actor=principal.actor_id, note=note)
    db.commit()
    return request


def stats(db: Session) -> dict[str, dict[str, int]]:
    rows = db.execute(
        select(PublicRequest.team, PublicRequest.status, func.count(PublicRequest.id)).group_by(
            PublicRequest.team, PublicRequest.status
        )
    ).all()
    result: dict[str, dict[str, int]] = {"by_status": {}, "by_team": {}}
    for team, status, count in rows:
        result["by_status"][status] = result["by_status"].get(status, 0) + count
        result["by_team"][team] = result["by_team"].get(team, 0) + count
    return result
