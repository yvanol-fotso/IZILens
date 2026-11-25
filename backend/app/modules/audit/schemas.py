import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.common.enums import ActorType


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None
    actor_type: ActorType
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str | None
    request_id: str | None
    details: dict[str, Any]
    created_at: datetime
