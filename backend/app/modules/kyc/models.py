import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import CaseStatus, DocumentSide, RiskLevel
from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.core.types import EncryptedJSON, JsonType


def _enum(enum_cls: type, name: str, length: int) -> Enum:
    return Enum(enum_cls, native_enum=False, length=length, values_callable=lambda e: [m.value for m in e], name=name)


class KycJourney(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Parcours : contrôles exigés, limites de tentatives, expiration et règles de décision configurables."""

    __tablename__ = "kyc_journeys"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_kyc_journeys_org_code"),)

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    required_checks: Mapped[list] = mapped_column(JsonType, default=list)
    max_attempts: Mapped[dict] = mapped_column(JsonType, default=dict)
    expiry_hours: Mapped[int] = mapped_column(Integer, default=72)
    auto_decision_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    review_team: Mapped[str] = mapped_column(String(10), default="either")
    thresholds: Mapped[dict] = mapped_column(JsonType, default=dict)
    decision_rules: Mapped[dict] = mapped_column(JsonType, default=dict)
    billing: Mapped[dict] = mapped_column(JsonType, default=dict)
    parameters_validated: Mapped[bool] = mapped_column(Boolean, default=False)


class KycDocumentCoverage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Matrice pays × documents : seul un document « supported » est proposé comme vérifiable."""

    __tablename__ = "kyc_document_coverage"
    __table_args__ = (UniqueConstraint("country_code", "document_type", name="uq_kyc_coverage_country_document"),)

    country_code: Mapped[str] = mapped_column(String(2))
    document_type: Mapped[str] = mapped_column(String(32))
    label_fr: Mapped[str] = mapped_column(String(120))
    label_en: Mapped[str] = mapped_column(String(120))
    sides_required: Mapped[list] = mapped_column(JsonType, default=lambda: ["front"])
    status: Mapped[str] = mapped_column(String(12), default="planned")
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)


class KycCase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kyc_cases"
    __table_args__ = (
        UniqueConstraint("organization_id", "reference", name="uq_kyc_cases_org_reference"),
        Index("ix_kyc_cases_org_status_created", "organization_id", "status", "created_at"),
        Index("ix_kyc_cases_org_fingerprint", "organization_id", "identity_fingerprint"),
        Index("ix_kyc_cases_status_expires", "status", "expires_at"),
        Index("ix_kyc_cases_review_queue", "status", "review_team"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"))
    journey_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_journeys.id", ondelete="RESTRICT"))
    reference: Mapped[str | None] = mapped_column(String(64))
    country_code: Mapped[str] = mapped_column(String(2))
    document_type: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(2), default="fr")

    status: Mapped[CaseStatus] = mapped_column(_enum(CaseStatus, "case_status", 16), default=CaseStatus.CREATED)
    status_reason: Mapped[str | None] = mapped_column(String(48))
    failure_kind: Mapped[str | None] = mapped_column(String(16))  # "technical" : incident, jamais un refus d'identité
    risk_level: Mapped[RiskLevel | None] = mapped_column(_enum(RiskLevel, "risk_level", 8))
    ocr_confidence: Mapped[float | None] = mapped_column(Float)
    flags: Mapped[list] = mapped_column(JsonType, default=list)

    declared_identity: Mapped[dict | None] = mapped_column(EncryptedJSON)
    extracted_data: Mapped[dict | None] = mapped_column(EncryptedJSON)
    consent: Mapped[dict | None] = mapped_column(EncryptedJSON)
    identity_fingerprint: Mapped[str | None] = mapped_column(String(64))

    session_token_hash: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt_grants: Mapped[dict] = mapped_column(JsonType, default=dict)

    review_team: Mapped[str | None] = mapped_column(String(10))
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_by: Mapped[str] = mapped_column(String(80))
    is_sandbox: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(Text)

    journey: Mapped[KycJourney] = relationship()
    attempts: Mapped[list["KycAttempt"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="KycAttempt.number"
    )
    documents: Mapped[list["KycDocument"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    checks: Mapped[list["KycCheck"]] = relationship(back_populates="case", cascade="all, delete-orphan", order_by="KycCheck.seq")
    events: Mapped[list["KycEvent"]] = relationship(back_populates="case", cascade="all, delete-orphan", order_by="KycEvent.seq")


class KycAttempt(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "kyc_attempts"
    __table_args__ = (UniqueConstraint("case_id", "number", name="uq_kyc_attempts_case_number"),)

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_cases.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(String(48))
    status: Mapped[str] = mapped_column(String(16), default="processing")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    case: Mapped[KycCase] = relationship(back_populates="attempts")


class KycDocument(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "kyc_documents"
    __table_args__ = (
        UniqueConstraint("attempt_id", "side", name="uq_kyc_documents_attempt_side"),
        Index("ix_kyc_documents_org_sha256", "organization_id", "sha256"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_cases.id", ondelete="CASCADE"), index=True)
    attempt_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_attempts.id", ondelete="CASCADE"))
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"))
    side: Mapped[DocumentSide] = mapped_column(_enum(DocumentSide, "document_side", 8))
    storage_key: Mapped[str] = mapped_column(String(200))
    sha256: Mapped[str] = mapped_column(String(64))
    mime_type: Mapped[str] = mapped_column(String(32))
    size_bytes: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    sharpness: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[KycCase] = relationship(back_populates="documents")


class KycCheck(UUIDPrimaryKeyMixin, Base):
    """Résultat d'un contrôle : documentaire aujourd'hui, biométrique (face_match, liveness) via le module 2."""

    __tablename__ = "kyc_checks"
    __table_args__ = (Index("ix_kyc_checks_case_type", "case_id", "check_type"),)

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_cases.id", ondelete="CASCADE"))
    attempt_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("kyc_attempts.id", ondelete="SET NULL"))
    seq: Mapped[int] = mapped_column(Integer)
    check_type: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(12))
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    details: Mapped[dict] = mapped_column(JsonType, default=dict)
    engine: Mapped[str | None] = mapped_column(String(40))
    version: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[KycCase] = relationship(back_populates="checks")


class KycEvent(UUIDPrimaryKeyMixin, Base):
    """Historique métier du dossier : jamais modifié ni supprimé."""

    __tablename__ = "kyc_events"
    __table_args__ = (Index("ix_kyc_events_case_seq", "case_id", "seq"),)

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_cases.id", ondelete="CASCADE"))
    seq: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(40))
    from_status: Mapped[str | None] = mapped_column(String(16))
    to_status: Mapped[str | None] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(String(48))
    actor_type: Mapped[str] = mapped_column(String(12))
    actor_id: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[KycCase] = relationship(back_populates="events")
