import uuid
from collections.abc import Sequence

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import CaseStatus
from app.modules.kyc.models import KycCase, KycDocument

_LOAD = (
    selectinload(KycCase.documents),
    selectinload(KycCase.attempts),
    selectinload(KycCase.checks),
    selectinload(KycCase.journey),
)


def get_case(db: Session, case_id: uuid.UUID, organization_id: uuid.UUID | None) -> KycCase | None:
    """Une organisation ne lit que ses dossiers ; organization_id=None est réservé au back-office."""
    query = select(KycCase).options(*_LOAD).where(KycCase.id == case_id)
    if organization_id is not None:
        query = query.where(KycCase.organization_id == organization_id)
    return db.scalar(query)


def get_case_by_session(db: Session, token_hash: str) -> KycCase | None:
    return db.scalar(select(KycCase).options(*_LOAD).where(KycCase.session_token_hash == token_hash))


def _filtered(
    organization_id: uuid.UUID | None,
    *,
    status: CaseStatus | None = None,
    reference: str | None = None,
    country_code: str | None = None,
    risk_level: str | None = None,
    search: str | None = None,
    review_teams: Sequence[str] | None = None,
    assigned_to: uuid.UUID | None = None,
    unassigned: bool = False,
):
    query = select(KycCase)
    if organization_id is not None:
        query = query.where(KycCase.organization_id == organization_id)
    if status:
        query = query.where(KycCase.status == status)
    if reference:
        query = query.where(KycCase.reference == reference)
    if country_code:
        query = query.where(KycCase.country_code == country_code.upper())
    if risk_level:
        query = query.where(KycCase.risk_level == risk_level)
    if search:
        pattern = f"%{search.strip().replace('%', '').replace('_', ' ')[:64]}%"
        query = query.where(or_(KycCase.reference.ilike(pattern), cast(KycCase.id, String).ilike(pattern)))
    if review_teams:
        query = query.where(KycCase.review_team.in_(review_teams))
    if assigned_to:
        query = query.where(KycCase.assigned_to_user_id == assigned_to)
    if unassigned:
        query = query.where(KycCase.assigned_to_user_id.is_(None))
    return query


def list_cases(
    db: Session, organization_id: uuid.UUID | None, *, page: int, page_size: int, oldest_first: bool = False, **filters
) -> tuple[list[KycCase], int]:
    query = _filtered(organization_id, **filters)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    order = KycCase.created_at.asc() if oldest_first else KycCase.created_at.desc()
    rows = db.scalars(query.order_by(order).offset((page - 1) * page_size).limit(page_size)).all()
    return list(rows), total


def status_counts(db: Session, organization_id: uuid.UUID | None) -> dict[str, int]:
    query = select(KycCase.status, func.count(KycCase.id)).group_by(KycCase.status)
    if organization_id is not None:
        query = query.where(KycCase.organization_id == organization_id)
    return {status.value: count for status, count in db.execute(query).all()}


def reference_exists(db: Session, organization_id: uuid.UUID, reference: str) -> bool:
    return (
        db.scalar(select(KycCase.id).where(KycCase.organization_id == organization_id, KycCase.reference == reference))
        is not None
    )


def cases_with_same_image(db: Session, organization_id: uuid.UUID, case_id: uuid.UUID, hashes: list[str]) -> list[uuid.UUID]:
    return list(
        db.scalars(
            select(KycDocument.case_id)
            .where(KycDocument.organization_id == organization_id, KycDocument.sha256.in_(hashes), KycDocument.case_id != case_id)
            .distinct()
            .limit(5)
        ).all()
    )


def cases_with_same_identity(db: Session, organization_id: uuid.UUID, case_id: uuid.UUID, fingerprint: str) -> list[uuid.UUID]:
    return list(
        db.scalars(
            select(KycCase.id)
            .where(
                KycCase.organization_id == organization_id,
                KycCase.identity_fingerprint == fingerprint,
                KycCase.id != case_id,
                KycCase.status.notin_([CaseStatus.FAILED, CaseStatus.EXPIRED]),
            )
            .limit(5)
        ).all()
    )


def due_for_expiry(db: Session, now, limit: int = 500) -> list[KycCase]:
    from app.modules.kyc.states import EXPIRABLE

    return list(
        db.scalars(
            select(KycCase)
            .options(selectinload(KycCase.journey))
            .where(KycCase.status.in_(list(EXPIRABLE)), KycCase.expires_at.is_not(None), KycCase.expires_at <= now)
            .limit(limit)
        ).all()
    )
