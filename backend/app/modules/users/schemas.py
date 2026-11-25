import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.common.enums import STAFF_ROLES, UserRole

TENANT_ROLES = {UserRole.ADMIN, UserRole.REVIEWER, UserRole.VIEWER, UserRole.INTEGRATION}
STAFF_ASSIGNABLE = STAFF_ROLES - {UserRole.SUPER_ADMIN}
ASSIGNABLE_ROLES = TENANT_ROLES | STAFF_ASSIGNABLE


def validate_password_strength(value: str) -> str:
    if len(value) < 12 or len(value) > 128:
        raise ValueError("Le mot de passe doit contenir entre 12 et 128 caractères")
    if not (re.search(r"[A-Za-z]", value) and re.search(r"\d", value)):
        raise ValueError("Le mot de passe doit contenir au moins une lettre et un chiffre")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str | None = Field(default=None, description="Omis : compte réservé à la connexion Google (OIDC)")
    role: UserRole = UserRole.REVIEWER
    organization_id: uuid.UUID | None = None

    @field_validator("password")
    @classmethod
    def _password(cls, value: str | None) -> str | None:
        return None if value is None else validate_password_strength(value)

    @field_validator("role")
    @classmethod
    def _role_assignable(cls, value: UserRole) -> UserRole:
        if value not in ASSIGNABLE_ROLES:
            raise ValueError("Rôle non attribuable")
        return value

    @field_validator("email")
    @classmethod
    def _lower(cls, value: str) -> str:
        return value.lower()


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    role: UserRole | None = None
    is_active: bool | None = None
    organization_id: uuid.UUID | None = Field(
        default=None, description="Super administrateur uniquement : rattacher un compte à une organisation"
    )

    @field_validator("role")
    @classmethod
    def _role_assignable(cls, value: UserRole | None) -> UserRole | None:
        if value is not None and value not in ASSIGNABLE_ROLES:
            raise ValueError("Rôle non attribuable")
        return value


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
