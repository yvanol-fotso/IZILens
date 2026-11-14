import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import CaseStatus
from app.modules.kyc.models import KycCase, KycDocument


def get_case(db: Session, organization_id: uuid.UUID, case_id: uuid.UUID) -> KycCase | None:
    """Toute lecture de dossier est filtrée par organisation : isolation entre clients."""
    return db.scalar(
        select(KycCase)
        .options(selectinload(KycCase.documents))
        .where(KycCase.id == case_id, KycCase.organization_id == organization_id)
    )


def list_cases(
    db: Session,
    organization_id: uuid.UUID,
    *,
    status: CaseStatus | None,
    reference: str | None,
    page: int,
    page_size: int,
) -> tuple[list[KycCase], int]:
    query = select(KycCase).where(KycCase.organization_id == organization_id)
    if status:
        query = query.where(KycCase.status == status)
    if reference:
        query = query.where(KycCase.reference == reference)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(KycCase.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return list(rows), total


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
                KycCase.status != CaseStatus.FAILED,
            )
            .limit(5)
        ).all()
    )
