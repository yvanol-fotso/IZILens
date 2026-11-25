import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import UserRole
from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.core.types import EncryptedJSON, JsonType


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("organizations.id", ondelete="RESTRICT"), index=True
    )
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str | None] = mapped_column(String(255))  # None : compte OIDC uniquement
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e], name="user_role")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    token_version: Mapped[int] = mapped_column(Integer, default=0)


class UserIdentity(UUIDPrimaryKeyMixin, Base):
    """Identité fédérée (OpenID Connect) rattachée à un utilisateur existant."""

    __tablename__ = "user_identities"
    __table_args__ = (UniqueConstraint("provider", "subject", name="uq_user_identities_provider_subject"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(20))
    subject: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(254))
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserMfa(UUIDPrimaryKeyMixin, Base):
    """Authentification à deux facteurs TOTP : secret chiffré, codes de secours hachés."""

    __tablename__ = "user_mfa"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    secret: Mapped[dict] = mapped_column(EncryptedJSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    recovery_codes: Mapped[list] = mapped_column(JsonType, default=list)
    enrolled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_step: Mapped[int | None] = mapped_column(Integer)
