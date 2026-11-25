import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccessRequestCreate(BaseModel):
    environment: str = Field(default="sandbox", pattern=r"^(sandbox|production)$")
    company_name: str = Field(min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    use_case: str = Field(min_length=10, max_length=2000)
    expected_volume: str | None = Field(default=None, max_length=40)


class AccessRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference: str
    environment: str
    company_name: str
    country: str | None
    use_case: str
    expected_volume: str | None
    status: str
    decision_note: str | None
    organization_id: uuid.UUID | None
    created_at: datetime
    decided_at: datetime | None


class AccessDecision(BaseModel):
    decision: str = Field(pattern=r"^(approved|rejected)$")
    note: str | None = Field(default=None, max_length=500)
    organization_slug: str | None = Field(default=None, pattern=r"^[a-z0-9](?:[a-z0-9-]{1,48})[a-z0-9]$")


class DeveloperOverview(BaseModel):
    has_organization: bool
    organization: str | None
    sandbox: bool
    production: bool
    pending_request: AccessRequestRead | None
    api_keys: dict[str, int]
    webhooks: int
    base_url_hint: str
