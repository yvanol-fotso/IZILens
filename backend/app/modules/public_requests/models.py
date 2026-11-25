import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.core.types import EncryptedJSON, JsonType


class PublicRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Demande publique (contact, devis, démonstration) : champs personnels chiffrés, métadonnées exploitables en clair."""

    __tablename__ = "public_requests"
    __table_args__ = (Index("ix_public_requests_status_created", "status", "created_at"),)

    reference: Mapped[str] = mapped_column(String(24), unique=True)
    kind: Mapped[str] = mapped_column(String(10))
    request_type: Mapped[str] = mapped_column(String(30))
    team: Mapped[str] = mapped_column(String(12))
    locale: Mapped[str] = mapped_column(String(2), default="fr")
    status: Mapped[str] = mapped_column(String(12), default="new")
    country: Mapped[str | None] = mapped_column(String(80))
    sector: Mapped[str | None] = mapped_column(String(60))
    volume: Mapped[str | None] = mapped_column(String(40))
    services: Mapped[list] = mapped_column(JsonType, default=list)
    payload: Mapped[dict] = mapped_column(EncryptedJSON)
    email_hash: Mapped[str] = mapped_column(String(64), index=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    consent_privacy: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_version: Mapped[str | None] = mapped_column(String(20))
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    events: Mapped[list["PublicRequestEvent"]] = relationship(
        back_populates="request", cascade="all, delete-orphan", order_by="PublicRequestEvent.seq"
    )


class PublicRequestEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "public_request_events"

    request_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("public_requests.id", ondelete="CASCADE"), index=True)
    seq: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(30))
    from_status: Mapped[str | None] = mapped_column(String(12))
    to_status: Mapped[str | None] = mapped_column(String(12))
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    note: Mapped[dict | None] = mapped_column(EncryptedJSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped[PublicRequest] = relationship(back_populates="events")
