import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

KINDS = ("contact", "demo")
REQUEST_TYPES = ("sales", "demo", "partnership", "integration", "institutional", "quote", "developer", "other")
SERVICES = ("kyc", "kyb", "liveness", "monitoring", "api", "other")
STATUSES = ("new", "in_review", "contacted", "qualified", "closed")
TEAM_BY_TYPE = {
    "sales": "sales",
    "demo": "sales",
    "quote": "sales",
    "other": "sales",
    "partnership": "partnerships",
    "integration": "partnerships",
    "institutional": "partnerships",
    "developer": "partnerships",
}


class ContactFields(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    company: str = Field(min_length=1, max_length=120)
    email: EmailStr
    country: str = Field(min_length=2, max_length=80)
    role: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    type: str = Field(default="sales", max_length=30)
    subject: str | None = Field(default=None, max_length=200)
    sector: str | None = Field(default=None, max_length=60)
    volume: str | None = Field(default=None, max_length=40)
    services: list[str] = []
    message: str = Field(min_length=1, max_length=4000)
    consent_privacy: bool
    consent_marketing: bool = False

    @field_validator("type")
    @classmethod
    def _type(cls, value: str) -> str:
        return value if value in REQUEST_TYPES else "other"

    @field_validator("services")
    @classmethod
    def _services(cls, value: list[str]) -> list[str]:
        return sorted({s for s in value if s in SERVICES})

    @field_validator("full_name", "company", "country", "role", "subject", "sector", "message", "phone", "volume", mode="before")
    @classmethod
    def _strip(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def _lower(cls, value: str) -> str:
        return value.lower()


class ContactRequestIn(BaseModel):
    kind: str = Field(default="contact")
    locale: str = Field(default="fr")
    fields: ContactFields

    @model_validator(mode="after")
    def _check(self) -> "ContactRequestIn":
        if self.kind not in KINDS:
            raise ValueError("Type de demande inconnu")
        if self.locale not in ("fr", "en"):
            self.locale = "fr"
        if not self.fields.consent_privacy:
            raise ValueError("Le consentement à la politique de confidentialité est requis")
        return self


class ContactRequestOut(BaseModel):
    reference: str


class StatusChange(BaseModel):
    status: str = Field(pattern=r"^(new|in_review|contacted|qualified|closed)$")
    note: str | None = Field(default=None, max_length=1000)


class AssignIn(BaseModel):
    assignee_user_id: uuid.UUID | None = None


class NoteIn(BaseModel):
    note: str = Field(min_length=2, max_length=1000)


class RequestSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference: str
    kind: str
    request_type: str
    team: str
    locale: str
    status: str
    country: str | None
    sector: str | None
    volume: str | None
    services: list[str]
    assigned_to_user_id: uuid.UUID | None
    created_at: datetime
    closed_at: datetime | None


class RequestEventRead(BaseModel):
    seq: int
    event_type: str
    from_status: str | None
    to_status: str | None
    actor_user_id: uuid.UUID | None
    note: str | None
    created_at: datetime


class RequestDetail(RequestSummary):
    contact: dict[str, Any]
    consent_privacy: bool
    consent_marketing: bool
    consent_version: str | None
    events: list[RequestEventRead]
