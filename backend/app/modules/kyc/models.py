import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
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

from app.common.enums import CaseStatus, DocumentSide, DocumentType, RiskLevel
from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.core.types import EncryptedJSON, JsonType


def _enum(enum_cls: type, name: str, length: int) -> Enum:
    return Enum(enum_cls, native_enum=False, length=length, values_callable=lambda e: [m.value for m in e], name=name)


class KycCase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kyc_cases"
    __table_args__ = (
        UniqueConstraint("organization_id", "reference", name="uq_kyc_cases_org_reference"),
        Index("ix_kyc_cases_org_status_created", "organization_id", "status", "created_at"),
        Index("ix_kyc_cases_org_fingerprint", "organization_id", "identity_fingerprint"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"))
    reference: Mapped[str | None] = mapped_column(String(64))
    document_type: Mapped[DocumentType] = mapped_column(_enum(DocumentType, "document_type", 16), default=DocumentType.CNI_CM)
    status: Mapped[CaseStatus] = mapped_column(_enum(CaseStatus, "case_status", 16), default=CaseStatus.PROCESSING)
    risk_level: Mapped[RiskLevel | None] = mapped_column(_enum(RiskLevel, "risk_level", 8))
    ocr_confidence: Mapped[float | None] = mapped_column(Float)
    extracted_data: Mapped[dict | None] = mapped_column(EncryptedJSON)
    flags: Mapped[list] = mapped_column(JsonType, default=list)
    identity_fingerprint: Mapped[str | None] = mapped_column(String(64))
    failure_reason: Mapped[str | None] = mapped_column(String(64))
    created_by: Mapped[str] = mapped_column(String(80))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(Text)

    documents: Mapped[list["KycDocument"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class KycDocument(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "kyc_documents"
    __table_args__ = (
        UniqueConstraint("case_id", "side", name="uq_kyc_documents_case_side"),
        Index("ix_kyc_documents_org_sha256", "organization_id", "sha256"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("kyc_cases.id", ondelete="CASCADE"), index=True)
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
