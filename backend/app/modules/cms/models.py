import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.core.types import JsonType


class CmsEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Contenu éditorial administrable : article de blog, guide ou question de FAQ, par langue."""

    __tablename__ = "cms_entries"
    __table_args__ = (
        UniqueConstraint("kind", "locale", "slug", name="uq_cms_entries_kind_locale_slug"),
        Index("ix_cms_entries_public", "kind", "locale", "status", "published_at"),
    )

    kind: Mapped[str] = mapped_column(String(8))
    locale: Mapped[str] = mapped_column(String(2))
    slug: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(String(400))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(60))
    tags: Mapped[list] = mapped_column(JsonType, default=list)
    status: Mapped[str] = mapped_column(String(10), default="draft")
    position: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    author_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
