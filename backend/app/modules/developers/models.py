import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, UUIDPrimaryKeyMixin


class DeveloperAccessRequest(UUIDPrimaryKeyMixin, Base):
    """Demande d'accès au portail développeur : ouverture de l'organisation Sandbox ou passage en Production."""

    __tablename__ = "developer_access_requests"

    reference: Mapped[str] = mapped_column(String(24), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="SET NULL"))
    environment: Mapped[str] = mapped_column(String(10))
    company_name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str | None] = mapped_column(String(80))
    use_case: Mapped[str] = mapped_column(Text)
    expected_volume: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(10), default="pending")
    decision_note: Mapped[str | None] = mapped_column(String(500))
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
