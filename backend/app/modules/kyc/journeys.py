import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.constants import PRIORITY_COUNTRIES
from app.core.exceptions import Conflict, Forbidden, NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.kyc import defaults
from app.modules.kyc.journey_schemas import CoverageUpdate, CoverageUpsert, JourneyCreate, JourneyUpdate
from app.modules.kyc.models import KycDocumentCoverage, KycJourney


def ensure_platform_defaults(db: Session, *, validate_coverage: bool = False) -> KycJourney:
    """Crée le parcours plateforme et la matrice de couverture initiale si absents (idempotent)."""
    journey = db.scalar(
        select(KycJourney).where(KycJourney.organization_id.is_(None), KycJourney.code == defaults.DEFAULT_JOURNEY["code"])
    )
    if journey is None:
        journey = KycJourney(organization_id=None, **defaults.DEFAULT_JOURNEY)
        db.add(journey)
    for entry in defaults.DEFAULT_COVERAGE:
        row = db.scalar(
            select(KycDocumentCoverage).where(
                KycDocumentCoverage.country_code == entry["country_code"],
                KycDocumentCoverage.document_type == entry["document_type"],
            )
        )
        if row is None:
            row = KycDocumentCoverage(**entry)
            db.add(row)
        if validate_coverage and row.status != "supported":
            row.status = "supported"
            row.validated_at = utcnow()
    db.flush()
    return journey


def platform_journey(db: Session) -> KycJourney:
    journey = db.scalar(
        select(KycJourney).where(
            KycJourney.organization_id.is_(None), KycJourney.is_default.is_(True), KycJourney.is_active.is_(True)
        )
    )
    if journey is None:
        raise NotFound("Aucun parcours plateforme configuré", code="JOURNEY_NOT_CONFIGURED")
    return journey


def resolve_journey(db: Session, organization_id: uuid.UUID, code: str | None) -> KycJourney:
    """Ordre : code demandé (parcours de l'organisation puis plateforme), parcours par défaut de l'organisation, parcours plateforme."""
    base = select(KycJourney).where(KycJourney.is_active.is_(True))
    if code:
        journey = db.scalar(base.where(KycJourney.organization_id == organization_id, KycJourney.code == code)) or db.scalar(
            base.where(KycJourney.organization_id.is_(None), KycJourney.code == code)
        )
        if journey is None:
            raise ValidationFailed("Parcours inconnu", code="JOURNEY_NOT_FOUND")
        return journey
    return db.scalar(
        base.where(KycJourney.organization_id == organization_id, KycJourney.is_default.is_(True))
    ) or platform_journey(db)


def list_journeys(db: Session, organization_id: uuid.UUID | None) -> list[KycJourney]:
    query = select(KycJourney).order_by(KycJourney.organization_id.is_(None).desc(), KycJourney.code)
    if organization_id is not None:
        query = query.where((KycJourney.organization_id == organization_id) | (KycJourney.organization_id.is_(None)))
    return list(db.scalars(query).all())


def _merge(base: dict, patch: dict) -> dict:
    return {**base, **{k: v for k, v in patch.items() if v is not None}}


def _check_not_weaker_than_platform(db: Session, required_checks: list[str]) -> None:
    mandatory = set(platform_journey(db).required_checks)
    if not mandatory <= set(required_checks):
        raise ValidationFailed(
            "Un parcours client ne peut pas retirer un contrôle obligatoire de la plateforme", code="MANDATORY_CHECK_REMOVED"
        )


def create_journey(db: Session, principal: Principal, payload: JourneyCreate, organization_id: uuid.UUID | None) -> KycJourney:
    config = {**defaults.DEFAULT_JOURNEY}
    for key in (
        "required_checks",
        "max_attempts",
        "expiry_hours",
        "auto_decision_enabled",
        "review_team",
        "thresholds",
        "decision_rules",
        "billing",
    ):
        value = getattr(payload, key)
        if value is not None:
            config[key] = value.value if key == "review_team" else value
    config.update(code=payload.code, name=payload.name, is_default=payload.is_default, parameters_validated=False)
    for key in ("max_attempts", "thresholds", "decision_rules", "billing"):
        config[key] = {**defaults.DEFAULT_JOURNEY[key], **(getattr(payload, key) or {})}
    if organization_id is not None:
        _check_not_weaker_than_platform(db, config["required_checks"])
    exists = db.scalar(
        select(KycJourney.id).where(
            KycJourney.organization_id == organization_id if organization_id else KycJourney.organization_id.is_(None),
            KycJourney.code == payload.code,
        )
    )
    if exists:
        raise Conflict("Ce code de parcours existe déjà", code="JOURNEY_CODE_ALREADY_USED")
    if payload.is_default:
        _clear_default(db, organization_id)
    journey = KycJourney(organization_id=organization_id, **config)
    db.add(journey)
    db.flush()
    audit.record(
        db,
        action="kyc.journey.created",
        resource_type="kyc_journey",
        resource_id=journey.id,
        principal=principal,
        organization_id=organization_id,
    )
    db.commit()
    return journey


def _clear_default(db: Session, organization_id: uuid.UUID | None) -> None:
    query = select(KycJourney).where(KycJourney.is_default.is_(True))
    query = (
        query.where(KycJourney.organization_id == organization_id)
        if organization_id
        else query.where(KycJourney.organization_id.is_(None))
    )
    for row in db.scalars(query).all():
        row.is_default = False


def update_journey(
    db: Session, principal: Principal, journey_id: uuid.UUID, payload: JourneyUpdate, *, scope: uuid.UUID | None, platform: bool
) -> KycJourney:
    journey = db.get(KycJourney, journey_id)
    if journey is None or (not platform and journey.organization_id != scope):
        raise NotFound("Parcours introuvable", code="JOURNEY_NOT_FOUND")
    if journey.organization_id is None and not platform:
        raise Forbidden("Le parcours plateforme n'est pas modifiable ici", code="FORBIDDEN")
    changes = payload.model_dump(exclude_unset=True)
    if not platform and "parameters_validated" in changes:
        raise Forbidden("Seule la plateforme valide les paramètres", code="FORBIDDEN")
    if journey.organization_id is not None and "required_checks" in changes and changes["required_checks"] is not None:
        _check_not_weaker_than_platform(db, changes["required_checks"])
    if changes.get("is_default"):
        _clear_default(db, journey.organization_id)
    for key, value in changes.items():
        if value is None:
            continue
        if key in ("max_attempts", "thresholds", "decision_rules", "billing"):
            value = _merge(getattr(journey, key), value)
        if key == "review_team":
            value = value.value if hasattr(value, "value") else value
        setattr(journey, key, value)
    if changes and set(changes) != {"parameters_validated"} and "parameters_validated" not in changes:
        journey.parameters_validated = False
    audit.record(
        db,
        action="kyc.journey.updated",
        resource_type="kyc_journey",
        resource_id=journey.id,
        principal=principal,
        organization_id=journey.organization_id,
        details={"fields": sorted(changes)},
    )
    db.commit()
    return journey


def supported_documents(db: Session, country_code: str | None = None) -> list[KycDocumentCoverage]:
    query = (
        select(KycDocumentCoverage)
        .where(KycDocumentCoverage.status == "supported")
        .order_by(KycDocumentCoverage.country_code, KycDocumentCoverage.document_type)
    )
    if country_code:
        query = query.where(KycDocumentCoverage.country_code == country_code.upper())
    return list(db.scalars(query).all())


def coverage_gaps(db: Session) -> list[str]:
    covered = {row.country_code for row in supported_documents(db)}
    return sorted(PRIORITY_COUNTRIES - covered)


def require_supported_document(db: Session, country_code: str, document_type: str) -> KycDocumentCoverage:
    row = db.scalar(
        select(KycDocumentCoverage).where(
            KycDocumentCoverage.country_code == country_code, KycDocumentCoverage.document_type == document_type
        )
    )
    if row is None or row.status != "supported":
        raise ValidationFailed("Ce document n'est pas pris en charge pour ce pays", code="DOCUMENT_NOT_SUPPORTED")
    return row


def list_coverage(db: Session) -> list[KycDocumentCoverage]:
    return list(
        db.scalars(
            select(KycDocumentCoverage).order_by(KycDocumentCoverage.country_code, KycDocumentCoverage.document_type)
        ).all()
    )


def upsert_coverage(db: Session, principal: Principal, payload: CoverageUpsert) -> KycDocumentCoverage:
    row = db.scalar(
        select(KycDocumentCoverage).where(
            KycDocumentCoverage.country_code == payload.country_code, KycDocumentCoverage.document_type == payload.document_type
        )
    )
    if row is not None:
        raise Conflict("Ce document existe déjà pour ce pays", code="COVERAGE_ALREADY_EXISTS")
    row = KycDocumentCoverage(**payload.model_dump())
    if payload.status == "supported":
        row.validated_at, row.validated_by_user_id = utcnow(), principal.actor_id
    db.add(row)
    db.flush()
    audit.record(db, action="kyc.coverage.created", resource_type="kyc_coverage", resource_id=row.id, principal=principal)
    db.commit()
    return row


def update_coverage(db: Session, principal: Principal, coverage_id: uuid.UUID, payload: CoverageUpdate) -> KycDocumentCoverage:
    row = db.get(KycDocumentCoverage, coverage_id)
    if row is None:
        raise NotFound("Couverture introuvable", code="COVERAGE_NOT_FOUND")
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        if value is not None:
            setattr(row, key, value)
    if changes.get("status") == "supported":
        row.validated_at, row.validated_by_user_id = utcnow(), principal.actor_id
    audit.record(
        db,
        action="kyc.coverage.updated",
        resource_type="kyc_coverage",
        resource_id=row.id,
        principal=principal,
        details={"fields": sorted(changes)},
    )
    db.commit()
    return row


def resolve_country(db: Session, country_code: str | None, document_type: str) -> str:
    """Le pays doit être connu (R-01) : fourni, ou déduit du type de document lorsqu'il n'existe que dans un pays supporté."""
    if country_code:
        return country_code.upper()
    countries = {row.country_code for row in supported_documents(db) if row.document_type == document_type}
    if len(countries) == 1:
        return countries.pop()
    raise ValidationFailed("Le pays de délivrance est requis", code="COUNTRY_REQUIRED")
