import logging
import secrets
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.common.enums import (
    LIMITED_ATTEMPT_KINDS,
    PLATFORM_ROLES,
    AttemptKind,
    BillingEventType,
    CaseStatus,
    CheckStatus,
    CheckType,
    Decision,
    DocumentSide,
    UserRole,
)
from app.core.config import get_settings
from app.core.database import session_scope
from app.core.exceptions import Conflict, Forbidden, NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.security import keyed_digest
from app.core.time import as_utc, utcnow
from app.modules.audit import service as audit
from app.modules.billing import service as billing
from app.modules.kyc import journeys, repository, rules
from app.modules.kyc.analysis import CheckResult, analyze_document, compute_risk, declared_match_check, derive_flags
from app.modules.kyc.models import KycAttempt, KycCase, KycCheck, KycDocument, KycEvent
from app.modules.kyc.schemas import REFERENCE_PATTERN, DecisionRequest
from app.modules.kyc.states import EDITABLE_DECLARATION, EXPIRABLE, TERMINAL, UPLOADABLE, can_transition
from app.modules.kyc.visibility import biometric_unsatisfied, latest_checks
from app.modules.webhooks import service as webhooks
from app.shared.ocr.engine import get_engine
from app.shared.storage.local import get_storage
from app.shared.validation.files import NormalizedImage, normalize_image, read_upload

logger = logging.getLogger("app.kyc")
MIN_JUSTIFICATION = 10
SESSION_PREFIX = "izs_"
DECLARED_ONLY = "DECLARED_ONLY"


@dataclass(frozen=True)
class Actor:
    type: str
    id: str | None = None

    @classmethod
    def of(cls, principal: Principal) -> "Actor":
        return cls(principal.actor_type.value, str(principal.actor_id))


SYSTEM = Actor("system")
PERSON = Actor("person")


@dataclass
class CaseParams:
    reference: str | None
    country_code: str
    document_type: str
    language: str
    journey_code: str | None = None
    declared: dict[str, Any] | None = None
    consent: dict[str, Any] | None = None


# ----------------------------------------------------------------------------- historique et transitions


def record_event(
    db: Session,
    case: KycCase,
    event_type: str,
    *,
    actor: Actor,
    from_status: str | None = None,
    to_status: str | None = None,
    reason: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        KycEvent(
            case=case,
            seq=len(case.events) + 1,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            actor_type=actor.type,
            actor_id=actor.id,
            details=details or {},
        )
    )


def transition(
    db: Session, case: KycCase, to: CaseStatus, *, reason: str | None, actor: Actor, details: dict | None = None
) -> None:
    """Applique le diagramme d'états : toute évolution de statut est validée, historisée et notifiée."""
    current = case.status
    if current == to:
        case.status_reason = reason
        return
    if not can_transition(current, to):
        raise Conflict(f"Transition {current.value} → {to.value} interdite", code="INVALID_TRANSITION")
    now = utcnow()
    case.status, case.status_reason = to, reason
    case.failure_kind = "technical" if to == CaseStatus.FAILED else None
    if to in TERMINAL:
        case.completed_at = now
    if to == CaseStatus.MANUAL_REVIEW:
        case.review_team = case.journey.review_team
        case.assigned_to_user_id = case.assigned_at = None
        billing.record(db, case, BillingEventType.MANUAL_REVIEW)
    elif current == CaseStatus.MANUAL_REVIEW:
        case.assigned_to_user_id = case.assigned_at = None
    if to == CaseStatus.FAILED:
        billing.record(db, case, BillingEventType.TECHNICAL_FAILURE)
    record_event(
        db, case, "status_changed", actor=actor, from_status=current.value, to_status=to.value, reason=reason, details=details
    )
    webhooks.enqueue(db, case, "case.status_changed", {"previous_status": current.value})


# ----------------------------------------------------------------------------- tentatives


def _used(case: KycCase, kind: str) -> int:
    return sum(1 for a in case.attempts if a.kind == kind)


def _limit(case: KycCase, kind: str) -> int:
    return case.journey.max_attempts.get(kind, 0) + case.attempt_grants.get(kind, 0)


def can_retry(case: KycCase, kind: str) -> bool:
    return _used(case, kind) < _limit(case, kind)


def _start_attempt(db: Session, case: KycCase, kind: AttemptKind, actor: Actor, reason: str | None = None) -> KycAttempt:
    if kind in LIMITED_ATTEMPT_KINDS and not can_retry(case, kind.value):
        raise Conflict("Nombre maximal de tentatives atteint", code="ATTEMPTS_EXHAUSTED")
    attempt = KycAttempt(case=case, number=len(case.attempts) + 1, kind=kind.value, reason=reason, status="processing")
    db.add(attempt)
    db.flush()
    if kind != AttemptKind.INITIAL:
        billing.record(db, case, BillingEventType.ATTEMPT)
    record_event(db, case, "attempt_started", actor=actor, details={"number": attempt.number, "kind": kind.value})
    return attempt


# ----------------------------------------------------------------------------- création et dépôt


def _validate_reference(db: Session, organization_id: uuid.UUID, reference: str | None) -> None:
    if reference is None:
        return
    if not REFERENCE_PATTERN.match(reference):
        raise ValidationFailed("Référence invalide (1 à 64 caractères alphanumériques, . _ : -)", code="INVALID_REFERENCE")
    if repository.reference_exists(db, organization_id, reference):
        raise Conflict("Cette référence existe déjà", code="REFERENCE_ALREADY_USED")


def normalize_uploads(
    front: UploadFile | None, back: UploadFile | None, required_sides: list[str]
) -> dict[DocumentSide, NormalizedImage]:
    settings = get_settings()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    images: dict[DocumentSide, NormalizedImage] = {}
    for side, upload in ((DocumentSide.FRONT, front), (DocumentSide.BACK, back)):
        if upload is not None:
            images[side] = normalize_image(
                read_upload(upload, max_bytes),
                min_long_side=settings.min_image_long_side,
                min_short_side=settings.min_image_short_side,
            )
    for side in required_sides:
        if DocumentSide(side) not in images:
            raise ValidationFailed(f"Le document « {side} » est requis", code="DOCUMENT_SIDE_REQUIRED")
    return images


def _attach_documents(
    db: Session, case: KycCase, attempt: KycAttempt, images: dict[DocumentSide, NormalizedImage], saved: list[str]
) -> None:
    storage = get_storage()
    for side, image in images.items():
        key = storage.save(organization_id=case.organization_id, case_id=case.id, data=image.data)
        saved.append(key)
        db.add(
            KycDocument(
                case=case,
                attempt_id=attempt.id,
                organization_id=case.organization_id,
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


def _discard_files(keys: list[str]) -> None:
    storage = get_storage()
    for key in keys:
        try:
            storage.delete(key)
        except Exception:  # noqa: BLE001 - nettoyage au mieux, l'erreur d'origine prime
            logger.warning("Suppression de fichier orphelin impossible")


def new_session_token() -> tuple[str, str]:
    token = SESSION_PREFIX + secrets.token_urlsafe(32)
    return token, keyed_digest(token)


def hosted_url(token: str) -> str:
    return f"{get_settings().hosted_journey_base_url.rstrip('/')}/{token}"


def create_case(
    db: Session, principal: Principal, params: CaseParams, front: UploadFile | None, back: UploadFile | None
) -> tuple[KycCase, str, KycAttempt | None]:
    organization_id = principal.organization_id
    actor = Actor.of(principal)
    coverage = journeys.require_supported_document(db, params.country_code, params.document_type)
    journey = journeys.resolve_journey(db, organization_id, params.journey_code)
    _validate_reference(db, organization_id, params.reference)
    images = normalize_uploads(front, back, coverage.sides_required) if front is not None or back is not None else {}

    token, token_hash = new_session_token()
    case = KycCase(
        organization_id=organization_id,
        journey_id=journey.id,
        reference=params.reference,
        country_code=params.country_code,
        document_type=params.document_type,
        language=params.language,
        status=CaseStatus.CREATED,
        flags=[],
        declared_identity=params.declared,
        consent=params.consent,
        session_token_hash=token_hash,
        expires_at=utcnow() + timedelta(hours=journey.expiry_hours),
        created_by=principal.label,
        is_sandbox=principal.sandbox,
    )
    case.journey = journey
    db.add(case)
    db.flush()
    saved: list[str] = []
    attempt = None
    try:
        record_event(db, case, "case_created", actor=actor, details={"journey": journey.code})
        billing.record(db, case, BillingEventType.CASE_CREATED)
        webhooks.enqueue(db, case, "case.created")
        if images:
            attempt = _submit(db, case, actor, images, saved)
        audit.record(
            db,
            action="kyc.case.created",
            resource_type="kyc_case",
            resource_id=case.id,
            principal=principal,
            details={"documents": [s.value for s in images]},
        )
        db.commit()
    except Exception:
        db.rollback()
        _discard_files(saved)
        raise
    db.refresh(case)
    return case, token, attempt


def _submit(
    db: Session, case: KycCase, actor: Actor, images: dict[DocumentSide, NormalizedImage], saved: list[str]
) -> KycAttempt:
    kind = AttemptKind.RECAPTURE if case.documents else AttemptKind.INITIAL
    attempt = _start_attempt(db, case, kind, actor)
    _attach_documents(db, case, attempt, images, saved)
    record_event(
        db, case, "documents_submitted", actor=actor, details={"sides": [s.value for s in images], "attempt": attempt.number}
    )
    transition(db, case, CaseStatus.PROCESSING, reason="PROCESSING", actor=actor)
    return attempt


def refresh_expiry(db: Session, case: KycCase) -> bool:
    """Expiration paresseuse : une demande dépassée n'est ni validée ni refusée, simplement expirée."""
    if case.status in EXPIRABLE and case.expires_at is not None and as_utc(case.expires_at) <= utcnow():
        transition(db, case, CaseStatus.EXPIRED, reason="REQUEST_EXPIRED", actor=SYSTEM)
        db.commit()
        return True
    return False


def submit_documents(db: Session, case: KycCase, actor: Actor, front: UploadFile, back: UploadFile | None) -> KycAttempt:
    if refresh_expiry(db, case):
        raise Conflict("La demande a expiré", code="CASE_EXPIRED")
    if case.status not in UPLOADABLE:
        raise Conflict("Le dépôt de documents n'est pas possible dans ce statut", code="INVALID_STATE")
    coverage = journeys.require_supported_document(db, case.country_code, case.document_type)
    images = normalize_uploads(front, back, coverage.sides_required)
    saved: list[str] = []
    try:
        attempt = _submit(db, case, actor, images, saved)
        db.commit()
    except Exception:
        db.rollback()
        _discard_files(saved)
        raise
    return attempt


def update_declared_identity(db: Session, case: KycCase, actor: Actor, declared: dict[str, Any]) -> KycAttempt | None:
    if refresh_expiry(db, case):
        raise Conflict("La demande a expiré", code="CASE_EXPIRED")
    if case.status not in EDITABLE_DECLARATION:
        raise Conflict("La modification n'est pas possible dans ce statut", code="INVALID_STATE")
    had_declared = case.declared_identity is not None
    processed = any(c.check_type == CheckType.OCR_EXTRACTION.value for c in case.checks)
    case.declared_identity = declared
    record_event(db, case, "declared_identity_updated", actor=actor, details={"correction": had_declared})
    attempt = None
    if not processed:
        if case.status == CaseStatus.CREATED:
            transition(db, case, CaseStatus.IN_PROGRESS, reason="IN_PROGRESS", actor=actor)
    else:
        kind = AttemptKind.DATA_CORRECTION if had_declared else AttemptKind.INITIAL
        attempt = _start_attempt(db, case, kind, actor, reason=DECLARED_ONLY)
        transition(db, case, CaseStatus.PROCESSING, reason="PROCESSING", actor=actor)
    db.commit()
    return attempt


def record_consent(db: Session, case: KycCase, actor: Actor, terms_version: str, ip: str | None) -> None:
    case.consent = {"terms_version": terms_version, "accepted_at": utcnow().isoformat(), "ip": ip}
    record_event(db, case, "consent_recorded", actor=actor, details={"terms_version": terms_version})
    if case.status == CaseStatus.CREATED:
        transition(db, case, CaseStatus.IN_PROGRESS, reason="IN_PROGRESS", actor=actor)
    db.commit()


# ----------------------------------------------------------------------------- traitement


def _add_check(
    db: Session,
    case: KycCase,
    attempt: KycAttempt | None,
    result: CheckResult,
    *,
    engine: str | None = None,
    version: str | None = None,
) -> None:
    db.add(
        KycCheck(
            case=case,
            attempt_id=attempt.id if attempt else None,
            seq=len(case.checks) + 1,
            check_type=result.check_type.value,
            status=result.status.value,
            is_required=result.check_type.value in case.journey.required_checks,
            details=result.details,
            engine=engine,
            version=version,
        )
    )


def apply_evaluation(db: Session, case: KycCase, attempt: KycAttempt | None, actor: Actor) -> None:
    """Recalcule signaux, risque et statut à partir des derniers résultats de chaque contrôle."""
    journey = case.journey
    checks = latest_checks(case)
    fields = (case.extracted_data or {}).get("fields")
    flags = derive_flags(fields, checks, today=utcnow().date(), thresholds=journey.thresholds)
    case.flags, case.risk_level = flags, compute_risk(flags)
    outcome = rules.evaluate(
        checks,
        flags,
        required_checks=journey.required_checks,
        decision_rules=journey.decision_rules,
        auto_decision_enabled=journey.auto_decision_enabled,
        can_retry=lambda kind: can_retry(case, kind),
    )
    if attempt is not None:
        attempt.completed_at = utcnow()
        attempt.status = {CaseStatus.FAILED: "failed", CaseStatus.ACTION_REQUIRED: "action_required"}.get(
            outcome.status, "completed"
        )
    transition(
        db,
        case,
        outcome.status,
        reason=outcome.reason,
        actor=actor,
        details={"triggers": outcome.triggers} if outcome.triggers else None,
    )


def _duplicate_checks(db: Session, case: KycCase, attempt: KycAttempt, fingerprint: str | None) -> list[CheckResult]:
    hashes = [d.sha256 for d in case.documents if d.attempt_id == attempt.id]
    same_image = repository.cases_with_same_image(db, case.organization_id, case.id, hashes) if hashes else []
    results = [
        CheckResult(
            CheckType.DUPLICATE_IMAGE,
            CheckStatus.INCONCLUSIVE if same_image else CheckStatus.PASSED,
            {"related_cases": [str(i) for i in same_image]} if same_image else {},
        )
    ]
    same_identity = repository.cases_with_same_identity(db, case.organization_id, case.id, fingerprint) if fingerprint else []
    results.append(
        CheckResult(
            CheckType.DUPLICATE_IDENTITY,
            CheckStatus.INCONCLUSIVE if same_identity else CheckStatus.PASSED,
            {"related_cases": [str(i) for i in same_identity]} if same_identity else {},
        )
    )
    return results


def _latest_documents(case: KycCase) -> dict[DocumentSide, KycDocument]:
    number = {a.id: a.number for a in case.attempts}
    latest: dict[DocumentSide, KycDocument] = {}
    for document in case.documents:
        current = latest.get(document.side)
        if current is None or number.get(document.attempt_id, 0) > number.get(current.attempt_id, 0):
            latest[document.side] = document
    return latest


def _execute(db: Session, case: KycCase, attempt: KycAttempt) -> None:
    settings = get_settings()
    journey = case.journey
    if attempt.reason == DECLARED_ONLY:
        fields = (case.extracted_data or {}).get("fields", {})
        _add_check(db, case, attempt, declared_match_check(case.declared_identity, fields, journey.thresholds))
    else:
        front = _latest_documents(case)[DocumentSide.FRONT]
        lines = get_engine().read(get_storage().load(front.storage_key))
        analysis = analyze_document(
            lines,
            sharpness=front.sharpness,
            today=utcnow().date(),
            thresholds=journey.thresholds,
            min_line_score=settings.ocr_min_line_score,
            declared=case.declared_identity,
        )
        case.extracted_data = {"engine": "paddleocr", "fields": analysis.fields}
        case.ocr_confidence, case.identity_fingerprint = analysis.confidence, analysis.identity_fingerprint
        for result in [*analysis.checks, *_duplicate_checks(db, case, attempt, analysis.identity_fingerprint)]:
            _add_check(db, case, attempt, result, engine="paddleocr" if result.check_type == CheckType.OCR_EXTRACTION else None)
    case.processed_at = utcnow()
    apply_evaluation(db, case, attempt, SYSTEM)


def run_pipeline(case_id: uuid.UUID, attempt_id: uuid.UUID) -> None:
    """Traitement hors requête : un incident technique devient FAILED, jamais un refus d'identité (R-08)."""
    with session_scope() as db:
        case = repository.get_case(db, case_id, None)
        attempt = db.get(KycAttempt, attempt_id)
        if case is None or attempt is None or case.status != CaseStatus.PROCESSING:
            return
        try:
            _execute(db, case, attempt)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Échec du traitement", extra={"case_id": str(case_id)})
            case = repository.get_case(db, case_id, None)
            attempt = db.get(KycAttempt, attempt_id)
            _add_check(db, case, attempt, CheckResult(CheckType.OCR_EXTRACTION, CheckStatus.ERROR, {"reason": "TECHNICAL_ERROR"}))
            attempt.status, attempt.completed_at = "failed", utcnow()
            transition(db, case, CaseStatus.FAILED, reason="TECHNICAL_ERROR", actor=SYSTEM)
            audit.record(
                db,
                action="kyc.case.failed",
                resource_type="kyc_case",
                resource_id=case_id,
                organization_id=case.organization_id,
                details={"reason": "TECHNICAL_ERROR"},
            )
            db.commit()
    webhooks.dispatch_pending()


def reprocess_case(db: Session, case: KycCase, actor: Actor) -> KycAttempt:
    if case.status != CaseStatus.FAILED:
        raise Conflict("Seul un dossier en incident technique peut être retraité", code="INVALID_STATE")
    attempt = _start_attempt(db, case, AttemptKind.TECHNICAL_RETRY, actor, reason="REPROCESS")
    transition(db, case, CaseStatus.PROCESSING, reason="PROCESSING", actor=actor)
    db.commit()
    return attempt


def record_external_check(
    db: Session,
    case: KycCase,
    actor: Actor,
    check_type: CheckType,
    status: CheckStatus,
    details: dict,
    engine: str | None,
    version: str | None,
) -> None:
    """Point d'entrée du module biométrique : enregistre un résultat puis réévalue le dossier sans toucher au reste."""
    if case.status not in (CaseStatus.IN_PROGRESS, CaseStatus.PROCESSING, CaseStatus.MANUAL_REVIEW):
        raise Conflict("Ce dossier n'accepte pas de nouveau résultat de contrôle", code="INVALID_STATE")
    _add_check(db, case, None, CheckResult(check_type, status, details), engine=engine, version=version)
    billing.record(db, case, BillingEventType.EXTRA_CHECK)
    record_event(db, case, "check_recorded", actor=actor, details={"check_type": check_type.value, "status": status.value})
    if case.status == CaseStatus.MANUAL_REVIEW:
        fields = (case.extracted_data or {}).get("fields")
        case.flags = derive_flags(fields, latest_checks(case), today=utcnow().date(), thresholds=case.journey.thresholds)
        case.risk_level = compute_risk(case.flags)
    else:
        apply_evaluation(db, case, None, actor)
    db.commit()


# ----------------------------------------------------------------------------- revue humaine


def _review_authority(case: KycCase, principal: Principal) -> None:
    team = case.review_team or "either"
    if principal.role in PLATFORM_ROLES:
        allowed = team in ("platform", "either") or principal.role == UserRole.SUPER_ADMIN
    else:
        allowed = team in ("client", "either")
    if not allowed:
        raise Forbidden("Ce dossier relève d'une autre équipe de revue", code="REVIEW_TEAM_MISMATCH")


def assign_case(db: Session, principal: Principal, case: KycCase, assignee_id: uuid.UUID | None) -> KycCase:
    from app.modules.users.models import User

    if case.status != CaseStatus.MANUAL_REVIEW:
        raise Conflict("Le dossier n'est pas en revue", code="INVALID_STATE")
    _review_authority(case, principal)
    target = assignee_id or principal.actor_id
    user = db.get(User, target) if principal.kind == "user" or assignee_id else None
    if user is None or not user.is_active:
        raise ValidationFailed("Analyste introuvable ou inactif", code="ASSIGNEE_INVALID")
    team = case.review_team or "either"
    is_platform = user.role in PLATFORM_ROLES
    same_org = user.organization_id == case.organization_id and user.role in (UserRole.ADMIN, UserRole.REVIEWER)
    if not ((is_platform and team in ("platform", "either")) or (same_org and team in ("client", "either"))):
        raise ValidationFailed("Cet utilisateur ne peut pas examiner ce dossier", code="ASSIGNEE_NOT_ALLOWED")
    if target != principal.actor_id and principal.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.PLATFORM_COMPLIANCE,
    ):
        raise Forbidden("Seul un administrateur peut assigner à un tiers", code="INSUFFICIENT_ROLE")
    case.assigned_to_user_id, case.assigned_at = user.id, utcnow()
    record_event(db, case, "assigned", actor=Actor.of(principal), details={"assignee": str(user.id)})
    audit.record(
        db,
        action="kyc.case.assigned",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
        details={"assignee": str(user.id)},
    )
    db.commit()
    return case


def decide(db: Session, principal: Principal, case: KycCase, payload: DecisionRequest) -> KycCase:
    if case.status != CaseStatus.MANUAL_REVIEW:
        raise Conflict("Le dossier n'est pas en attente de revue", code="INVALID_STATE")
    _review_authority(case, principal)
    if (
        case.assigned_to_user_id
        and case.assigned_to_user_id != principal.actor_id
        and principal.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ):
        raise Forbidden("Ce dossier est assigné à un autre analyste", code="ASSIGNED_TO_ANOTHER")
    reason = payload.reason.strip() if payload.reason else None
    approving = payload.decision == Decision.APPROVED
    if approving and case.risk_level and case.risk_level.value == "high" and (not reason or len(reason) < MIN_JUSTIFICATION):
        raise ValidationFailed(
            "Approuver un dossier à risque élevé exige une justification", code="REASON_REQUIRED_FOR_HIGH_RISK"
        )
    missing = biometric_unsatisfied(case) if approving else []
    if missing:
        formal = payload.exception and principal.role in PLATFORM_ROLES and reason and len(reason) >= MIN_JUSTIFICATION
        if not formal:
            raise ValidationFailed(
                "Un contrôle biométrique obligatoire n'est pas satisfait", code="REQUIRED_CHECKS_NOT_SATISFIED"
            )
        record_event(db, case, "exception_granted", actor=Actor.of(principal), details={"checks": missing})
        audit.record(
            db,
            action="kyc.case.exception_granted",
            resource_type="kyc_case",
            resource_id=case.id,
            principal=principal,
            organization_id=case.organization_id,
            details={"checks": missing},
        )
    case.decided_by_user_id = principal.actor_id if principal.kind == "user" else None
    case.decided_at, case.decision_reason = utcnow(), reason
    to = CaseStatus.VERIFIED if approving else CaseStatus.NOT_VERIFIED
    transition(db, case, to, reason="VERIFIED_MANUAL" if approving else "REJECTED_MANUAL", actor=Actor.of(principal))
    audit.record(
        db,
        action=f"kyc.case.{to.value}",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
        details={"risk_level": case.risk_level.value if case.risk_level else None},
    )
    db.commit()
    return case


def request_action(db: Session, principal: Principal, case: KycCase, reason: str) -> KycCase:
    if case.status != CaseStatus.MANUAL_REVIEW:
        raise Conflict("Le dossier n'est pas en revue", code="INVALID_STATE")
    _review_authority(case, principal)
    transition(
        db, case, CaseStatus.ACTION_REQUIRED, reason="COMPLEMENT_REQUESTED", actor=Actor.of(principal), details={"note": reason}
    )
    audit.record(
        db,
        action="kyc.case.complement_requested",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
    )
    db.commit()
    return case


# ----------------------------------------------------------------------------- back-office


def admin_transition(db: Session, principal: Principal, case: KycCase, to: CaseStatus, reason: str, exception: bool) -> KycCase:
    """Changement de statut encadré : validé par le diagramme d'états, motivé et audité ; jamais un contournement silencieux."""
    if principal.role != UserRole.SUPER_ADMIN:
        raise Forbidden("Réservé au super administrateur", code="INSUFFICIENT_ROLE")
    if to == CaseStatus.VERIFIED:
        missing = biometric_unsatisfied(case)
        if missing and not exception:
            raise ValidationFailed(
                "Un contrôle biométrique obligatoire n'est pas satisfait", code="REQUIRED_CHECKS_NOT_SATISFIED"
            )
        if missing:
            record_event(db, case, "exception_granted", actor=Actor.of(principal), details={"checks": missing})
    if to in (CaseStatus.VERIFIED, CaseStatus.NOT_VERIFIED):
        case.decided_by_user_id, case.decided_at, case.decision_reason = principal.actor_id, utcnow(), reason
    transition(db, case, to, reason="ADMIN_TRANSITION", actor=Actor.of(principal), details={"note": reason})
    audit.record(
        db,
        action="kyc.case.admin_transition",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
        details={"to": to.value, "exception": exception},
    )
    db.commit()
    return case


def grant_attempts(db: Session, principal: Principal, case: KycCase, kind: str, extra: int, reason: str) -> KycCase:
    if case.status in TERMINAL:
        raise Conflict("Dossier terminé", code="INVALID_STATE")
    grants = dict(case.attempt_grants or {})
    grants[kind] = grants.get(kind, 0) + extra
    case.attempt_grants = grants
    record_event(db, case, "attempts_granted", actor=Actor.of(principal), details={"kind": kind, "extra": extra, "note": reason})
    if case.status == CaseStatus.MANUAL_REVIEW and case.status_reason == "ATTEMPTS_EXHAUSTED":
        transition(db, case, CaseStatus.ACTION_REQUIRED, reason="COMPLEMENT_REQUESTED", actor=Actor.of(principal))
    audit.record(
        db,
        action="kyc.case.attempts_granted",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
        details={"kind": kind, "extra": extra},
    )
    db.commit()
    return case


def expire_due_cases(db: Session) -> int:
    count = 0
    for case in repository.due_for_expiry(db, utcnow()):
        transition(db, case, CaseStatus.EXPIRED, reason="REQUEST_EXPIRED", actor=SYSTEM)
        count += 1
    db.commit()
    return count


def rotate_session(db: Session, principal: Principal, case: KycCase) -> tuple[str, str]:
    if case.status in TERMINAL:
        raise Conflict("Dossier terminé", code="INVALID_STATE")
    token, token_hash = new_session_token()
    case.session_token_hash = token_hash
    audit.record(
        db,
        action="kyc.session.rotated",
        resource_type="kyc_case",
        resource_id=case.id,
        principal=principal,
        organization_id=case.organization_id,
    )
    db.commit()
    return token, hosted_url(token)


def read_document(db: Session, principal: Principal, case: KycCase, document_id: uuid.UUID) -> tuple[bytes, str]:
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
        organization_id=case.organization_id,
        details={"case_id": str(case.id)},
    )
    db.commit()
    return content, document.mime_type


def scoped_case(db: Session, principal: Principal, case_id: uuid.UUID) -> KycCase:
    case = repository.get_case(db, case_id, None if principal.role in PLATFORM_ROLES else principal.organization_id)
    if case is None:
        raise NotFound("Dossier introuvable", code="CASE_NOT_FOUND")
    return case


def case_from_session(db: Session, token: str) -> KycCase:
    from app.core.exceptions import Unauthorized

    case = repository.get_case_by_session(db, keyed_digest(token))
    if case is None:
        raise Unauthorized("Session invalide", code="INVALID_SESSION")
    refresh_expiry(db, case)
    return case
