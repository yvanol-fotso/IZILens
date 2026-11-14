import re
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.common.enums import CaseStatus, Decision, DocumentSide, DocumentType, RiskLevel

REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9._:\-]{1,64}$")


class ExtractedField(BaseModel):
    value: str | None
    normalized: str | None
    score: float | None
    method: str | None
    valid: bool


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    side: DocumentSide
    mime_type: str
    size_bytes: int
    width: int
    height: int
    sharpness: float


class CaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference: str | None
    document_type: DocumentType
    status: CaseStatus
    risk_level: RiskLevel | None
    ocr_confidence: float | None
    created_at: datetime
    processed_at: datetime | None


class CaseDetail(CaseSummary):
    flags: list[dict[str, Any]]
    extracted: dict[str, ExtractedField] | None = None
    failure_reason: str | None
    documents: list[DocumentRead]
    decided_by_user_id: uuid.UUID | None
    decided_at: datetime | None
    decision_reason: str | None


class DecisionRequest(BaseModel):
    decision: Decision
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _reason_required_for_rejection(self) -> "DecisionRequest":
        if self.decision == Decision.REJECTED and not (self.reason and self.reason.strip()):
            raise ValueError("Un motif est obligatoire pour un rejet")
        return self
