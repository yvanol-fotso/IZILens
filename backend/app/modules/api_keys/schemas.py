import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    expires_in_days: int | None = Field(default=None, ge=1, le=730)
    environment: str | None = Field(
        default=None, pattern=r"^(sandbox|production)$", description="Par défaut : Production si activée, sinon Sandbox"
    )


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    prefix: str
    environment: str
    is_active: bool
    expires_at: datetime | None
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class ApiKeyCreated(ApiKeyRead):
    key: str = Field(description="Affichée une seule fois : conservez-la immédiatement")
