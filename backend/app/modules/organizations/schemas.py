import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.common.constants import DEFAULT_MODULES, KNOWN_MODULES


def _check_modules(value: list[str]) -> list[str]:
    unknown = set(value) - KNOWN_MODULES
    if unknown:
        raise ValueError(f"Modules inconnus : {', '.join(sorted(unknown))}")
    return sorted(set(value))


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(pattern=r"^[a-z0-9](?:[a-z0-9-]{1,48})[a-z0-9]$")
    enabled_modules: list[str] = DEFAULT_MODULES
    admin_email: EmailStr | None = None
    admin_full_name: str | None = Field(default=None, min_length=2, max_length=120)
    production_enabled: bool = True

    _modules = field_validator("enabled_modules")(_check_modules)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    is_active: bool | None = None
    enabled_modules: list[str] | None = None
    production_enabled: bool | None = None

    @field_validator("enabled_modules")
    @classmethod
    def _modules(cls, value: list[str] | None) -> list[str] | None:
        return None if value is None else _check_modules(value)


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    enabled_modules: list[str]
    production_enabled: bool = True
    created_at: datetime
