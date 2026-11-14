import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.common.enums import UserRole

ASSIGNABLE_ROLES = {UserRole.ADMIN, UserRole.REVIEWER, UserRole.VIEWER}


def validate_password_strength(value: str) -> str:
    if len(value) < 12 or len(value) > 128:
        raise ValueError("Le mot de passe doit contenir entre 12 et 128 caractères")
    if not (re.search(r"[A-Za-z]", value) and re.search(r"\d", value)):
        raise ValueError("Le mot de passe doit contenir au moins une lettre et un chiffre")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str
    role: UserRole = UserRole.REVIEWER
    organization_id: uuid.UUID | None = None

    _password = field_validator("password")(validate_password_strength)

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
