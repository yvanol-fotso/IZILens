import logging
import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import CaseStatus, Decision, DocumentSide, FlagSeverity, RiskLevel
from app.core.config import get_settings
from app.core.database import session_scope
from app.core.exceptions import Conflict, NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.kyc import repository
from app.modules.kyc.analysis import add_flag, analyze_front, compute_risk
from app.modules.kyc.models import KycCase, KycDocument
from app.modules.kyc.schemas import REFERENCE_PATTERN, CaseDetail, DecisionRequest, ExtractedField
from app.shared.ocr.engine import get_engine
from app.shared.storage.local import get_storage
from app.shared.validation.files import NormalizedImage, normalize_image, read_upload

logger = logging.getLogger("app.kyc")
HIGH_RISK_APPROVAL_MIN_REASON = 10


def _require_case(db: Session, principal: Principal, case_id: uuid.UUID) -> KycCase:
    case = repository.get_case(db, principal.organization_id, case_id)  # type: ignore[arg-type]
    if case is None:
        raise NotFound("Dossier introuvable", code="CASE_NOT_FOUND")
    return case


def create_case(
    db: Session, principal: Principal, *, front: UploadFile, back: UploadFile | None, reference: str | None
) -> KycCase:
    settings = get_settings()
    organization_id = principal.organization_id
    if reference is not None:
        if not REFERENCE_PATTERN.match(reference):
            raise ValidationFailed("Référence invalide (1 à 64 caractères alphanumériques, . _ : -)", code="INVALID_REFERENCE")
        if repository.reference_exists(db, organization_id, reference):  # type: ignore[arg-type]
            raise Conflict("Cette référence existe déjà", code="REFERENCE_ALREADY_USED")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    images: dict[DocumentSide, NormalizedImage] = {}
    for side, upload in ((DocumentSide.FRONT, front), (DocumentSide.BACK, back)):
        if upload is not None:
            images[side] = normalize_image(
                read_upload(upload, max_bytes),
                min_long_side=settings.min_image_long_side,
                min_short_side=settings.min_image_short_side,
            )

    case_id = uuid.uuid4()
    storage = get_storage()
    saved_keys: list[str] = []
    try:
        case = KycCase(
            id=case_id,
            organization_id=organization_id,
            reference=reference,
            status=CaseStatus.PROCESSING,
            flags=[],
            created_by=principal.label,
        )
        db.add(case)
        for side, image in images.items():
            key = storage.save(organization_id=organization_id, case_id=case_id, data=image.data)  # type: ignore[arg-type]
            saved_keys.append(key)
            db.add(
                KycDocument(
                    case_id=case_id,
                    organization_id=organization_id,
                    side=side,
                    storage_key=key,
                    sha256=image.sha256,
                    mime_type=image.mime_type,
                    size_bytes=len(image.data),
                    width=image.width,
                    height=image.height,
                    sharpness=image.sharpness,
                )
            )
        audit.record(
            db,
            action="kyc.case.created",
            resource_type="kyc_case",
            resource_id=case_id,
            principal=principal,
            details={"sides": [s.value for s in images]},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _discard_files(saved_keys)
        raise Conflict("Cette référence existe déjà", code="REFERENCE_ALREADY_USED") from exc
    except Exception:
        db.rollback()
        _discard_files(saved_keys)
        raise
    db.refresh(case)
    return case


def _discard_files(keys: list[str]) -> None:
    storage = get_storage()
    for key in keys:
        try:
            storage.delete(key)
        except Exception:  # noqa: BLE001 - nettoyage au mieux, l'erreur d'origine prime
            logger.warning("Suppression de fichier orphelin impossible")


def process_case(case_id: uuid.UUID) -> None:
    """Pipeline OCR exécuté hors requête : lecture, validation, détection de doublons, mise à jour du dossier."""
    settings = get_settings()
    with session_scope() as db:
        case = db.get(KycCase, case_id)
        if case is None or case.status != CaseStatus.PROCESSING:
            return
        try:
            documents = {d.side: d for d in db.scalars(select(KycDocument).where(KycDocument.case_id == case_id))}
            front = documents[DocumentSide.FRONT]
            lines = get_engine().read(get_storage().load(front.storage_key))
            result = analyze_front(
                lines,
                sharpness=front.sharpness,
                today=utcnow().date(),
                review_threshold=settings.ocr_review_threshold,
                min_line_score=settings.ocr_min_line_score,
            )
            same_image = repository.cases_with_same_image(
                db, case.organization_id, case_id, [d.sha256 for d in documents.values()]
            )
            if same_image:
                add_flag(
                    result.flags,
                    "DUPLICATE_DOCUMENT_IMAGE",
                    FlagSeverity.HIGH,
                    "Cette image a déjà été soumise dans un autre dossier",
                    related_cases=[str(i) for i in same_image],
                )
            if result.identity_fingerprint:
                same_identity = repository.cases_with_same_identity(
                    db, case.organization_id, case_id, result.identity_fingerprint
                )
                if same_identity:
                    add_flag(
                        result.flags,
                        "POSSIBLE_DUPLICATE_IDENTITY",
                        FlagSeverity.MEDIUM,
                        "Une identité identique existe déjà dans un autre dossier",
                        related_cases=[str(i) for i in same_identity],
                    )
            case.extracted_data = {"engine": "paddleocr", "fields": result.fields}
            case.flags = result.flags
            case.risk_level = compute_risk(result.flags)
            case.ocr_confidence = result.confidence
            case.identity_fingerprint = result.identity_fingerprint
            case.status = CaseStatus.PENDING_REVIEW
            case.failure_reason = None
            case.processed_at = utcnow()
            audit.record(
                db,
                action="kyc.case.processed",
                resource_type="kyc_case",
                resource_id=case_id,
                organization_id=case.organization_id,
                details={"risk_level": case.risk_level.value, "flags": sorted({f["code"] for f in result.flags})},
            )
        except Exception:
            db.rollback()
            logger.exception("Échec du traitement OCR", extra={"case_id": str(case_id)})
            case = db.get(KycCase, case_id)
            case.status = CaseStatus.FAILED
            case.failure_reason = "OCR_ERROR"
            case.processed_at = utcnow()
            audit.record(
                db,
                action="kyc.case.failed",
                resource_type="kyc_case",
                resource_id=case_id,
                organization_id=case.organization_id,
                details={"reason": "OCR_ERROR"},
            )
        db.commit()


def reprocess_case(db: Session, principal: Principal, case_id: uuid.UUID) -> KycCase:
    case = _require_case(db, principal, case_id)
    if case.status != CaseStatus.FAILED:
        raise Conflict("Seul un dossier en échec peut être retraité", code="INVALID_STATE")
    case.status = CaseStatus.PROCESSING
    case.failure_reason = None
    audit.record(db, action="kyc.case.reprocess_requested", resource_type="kyc_case", resource_id=case.id, principal=principal)
    db.commit()
    return case


def decide(db: Session, principal: Principal, case_id: uuid.UUID, payload: DecisionRequest) -> KycCase:
    case = _require_case(db, principal, case_id)
    if case.status != CaseStatus.PENDING_REVIEW:
        raise Conflict("Le dossier n'est pas en attente de revue", code="INVALID_STATE")
    reason = payload.reason.strip() if payload.reason else None
    high_risk_approval = payload.decision == Decision.APPROVED and case.risk_level == RiskLevel.HIGH
    if high_risk_approval and (not reason or len(reason) < HIGH_RISK_APPROVAL_MIN_REASON):
        raise ValidationFailed(
            "Approuver un dossier à risque élevé exige une justification", code="REASON_REQUIRED_FOR_HIGH_RISK"
        )
    case.status = CaseStatus.APPROVED if payload.decision == Decision.APPROVED else CaseStatus.REJECTED
    case.decided_by_user_id = principal.actor_id if principal.kind == "user" else None
    case.decided_at = utcnow()
    case.decision_reason = reason
    audit.record(
        db,
        action=f"kyc.case.{case.status.value}",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        details={"risk_level": case.risk_level.value if case.risk_level else None},
    )
    db.commit()
    return case


def get_case(db: Session, principal: Principal, case_id: uuid.UUID) -> KycCase:
    return _require_case(db, principal, case_id)


def read_document(db: Session, principal: Principal, case_id: uuid.UUID, document_id: uuid.UUID) -> tuple[bytes, str]:
    case = _require_case(db, principal, case_id)
    document = next((d for d in case.documents if d.id == document_id), None)
    if document is None:
        raise NotFound("Document introuvable", code="DOCUMENT_NOT_FOUND")
    content = get_storage().load(document.storage_key)
    audit.record(
        db,
        action="kyc.document.viewed",
        resource_type="kyc_document",
        resource_id=document.id,
        principal=principal,
        details={"case_id": str(case.id)},
    )
    db.commit()
    return content, document.mime_type


def to_detail(case: KycCase) -> CaseDetail:
    extracted = None
    if case.extracted_data:
        extracted = {name: ExtractedField(**data) for name, data in case.extracted_data["fields"].items()}
    base = {c: getattr(case, c) for c in CaseDetail.model_fields if hasattr(case, c) and c not in ("extracted", "documents")}
    return CaseDetail(**base, extracted=extracted, documents=list(case.documents))
