import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

WEBHOOK_EVENTS = ("case.created", "case.status_changed")


class WebhookCreate(BaseModel):
    url: str = Field(min_length=8, max_length=500)
    description: str | None = Field(default=None, max_length=120)
    events: list[str] = ["*"]

    @field_validator("events")
    @classmethod
    def _known(cls, value: list[str]) -> list[str]:
        unknown = set(value) - {"*", *WEBHOOK_EVENTS}
        if unknown or not value:
            raise ValueError("Événements inconnus ou liste vide")
        return sorted(set(value))


class WebhookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    description: str | None
    events: list[str]
    is_active: bool
    created_at: datetime


class WebhookCreated(WebhookRead):
    secret: str = Field(description="Affiché une seule fois : sert à vérifier la signature X-IZILens-Signature")


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    case_id: uuid.UUID | None
    status: str
    attempts: int
    last_status_code: int | None
    last_error: str | None
    next_attempt_at: datetime
    delivered_at: datetime | None
    created_at: datetime
    payload: dict[str, Any]
