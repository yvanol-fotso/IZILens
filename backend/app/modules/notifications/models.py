import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UUIDPrimaryKeyMixin
from app.core.types import EncryptedJSON


class EmailOutbox(UUIDPrimaryKeyMixin, Base):
    """File d'envoi d'e-mails : écrite dans la transaction métier, envoyée ensuite (jamais perdue ni envoyée à tort)."""

    __tablename__ = "email_outbox"
    __table_args__ = (Index("ix_email_outbox_due", "status", "created_at"),)

    template: Mapped[str] = mapped_column(String(40))
    locale: Mapped[str] = mapped_column(String(2), default="fr")
    message: Mapped[dict] = mapped_column(EncryptedJSON)  # destinataire, sujet et corps : données personnelles
    status: Mapped[str] = mapped_column(String(10), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(String(200))
    related_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
