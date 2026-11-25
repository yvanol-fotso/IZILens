import re
import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.common.enums import CaseStatus, CheckStatus, CheckType, Decision, DocumentSide, RiskLevel
from app.shared.validation import fields as fv

REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9._:\-]{1,64}$")


class DeclaredIdentity(BaseModel):
    """Identité déclarée par la personne ou l'entreprise cliente ; distincte des données lues sur le document."""

    surname: str = Field(min_length=2, max_length=80)
    given_names: str = Field(min_length=2, max_length=80)
    date_of_birth: date
    nationality: str | None = Field(default=None, max_length=60)

    @field_validator("surname", "given_names")
    @classmethod
    def _clean(cls, value: str) -> str:
        cleaned = fv.clean_name(value)
        if cleaned is None:
            raise ValueError("Valeur invalide")
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def _plausible(cls, value: date) -> date:
        if value >= date.today() or fv.full_years(value, date.today()) > 120:
            raise ValueError("Date de naissance invalide")
        return value

    def to_storage(self) -> dict[str, Any]:
        return {
            "surname": self.surname,
            "given_names": self.given_names,
            "date_of_birth": self.date_of_birth.isoformat(),
            "nationality": self.nationality,
        }


class FlagRead(BaseModel):
    code: str
    severity: str
    message: str
    field: str | None = None
    related_cases: list[str] | None = None
    similarity: float | None = None


class CheckRead(BaseModel):
    check_type: CheckType
    status: CheckStatus
    is_required: bool
    details: dict[str, Any]
    created_at: datetime


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int
    kind: str
    reason: str | None
    status: str
    started_at: datetime
    completed_at: datetime | None


class AttemptQuota(BaseModel):
    used: int
    max: int


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
    attempt_id: uuid.UUID
    mime_type: str
    size_bytes: int
    width: int
    height: int
    sharpness: float
    is_current: bool = True


class ScopeRead(BaseModel):
    executed_checks: list[str]
    not_run_checks: list[str]
    disclaimer: str


class CaseSummary(BaseModel):
    id: uuid.UUID
    reference: str | None
    country_code: str
    document_type: str
    language: str
    status: CaseStatus
    status_label: str
    status_reason: str | None
    status_message: str | None
    risk_level: RiskLevel | None
    ocr_confidence: float | None
    expires_at: datetime | None
    created_at: datetime
    processed_at: datetime | None
    review_team: str | None
    assigned_to_user_id: uuid.UUID | None


class SessionInfo(BaseModel):
    token: str = Field(description="Affiché une seule fois ; à transmettre à la personne via l'URL hébergée")
    hosted_url: str
    expires_at: datetime | None


class CaseCreated(CaseSummary):
    session: SessionInfo


class CaseDetail(CaseSummary):
    journey_code: str
    failure_kind: str | None
    flags: list[FlagRead]
    declared_identity: dict[str, Any] | None
    extracted: dict[str, ExtractedField] | None
    extracted_data: dict[str, Any] | None = None
    failure_reason: str | None = None
    checks: list[CheckRead]
    attempts: list[AttemptRead]
    attempts_summary: dict[str, AttemptQuota]
    documents: list[DocumentRead]
    scope: ScopeRead
    allowed_actions: list[str]
    decided_by_user_id: uuid.UUID | None
    decided_at: datetime | None
    decision_reason: str | None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seq: int
    event_type: str
    from_status: str | None
    to_status: str | None
    reason: str | None
    actor_type: str
    actor_id: str | None
    details: dict[str, Any]
    created_at: datetime


class DeclaredIdentityRead(BaseModel):
    surname: str | None = None
    given_names: str | None = None
    date_of_birth: str | None = None
    nationality: str | None = None


class DecisionRequest(BaseModel):
    decision: Decision
    reason: str | None = Field(default=None, max_length=500)
    exception: bool = Field(
        default=False, description="Exception formelle (plateforme uniquement) aux contrôles biométriques obligatoires"
    )

    @model_validator(mode="after")
    def _reason_required_for_rejection(self) -> "DecisionRequest":
        if self.decision == Decision.REJECTED and not (self.reason and self.reason.strip()):
            raise ValueError("Un motif est obligatoire pour un rejet")
        return self


class AssignRequest(BaseModel):
    assignee_user_id: uuid.UUID | None = Field(default=None, description="Par défaut : l'appelant")


class ActionRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=300)


class TransitionRequest(BaseModel):
    to_status: CaseStatus
    reason: str = Field(min_length=10, max_length=500)
    exception: bool = False


class GrantAttemptsRequest(BaseModel):
    kind: str = Field(pattern=r"^(recapture|data_correction|technical_retry)$")
    extra: int = Field(ge=1, le=5)
    reason: str = Field(min_length=10, max_length=500)


class ExternalCheckRequest(BaseModel):
    check_type: str = Field(pattern=r"^(face_match|liveness)$")
    status: str = Field(pattern=r"^(passed|failed|inconclusive|error)$")
    details: dict[str, Any] = {}
    engine: str | None = Field(default=None, max_length=40)
    version: str | None = Field(default=None, max_length=20)


class ConsentRequest(BaseModel):
    accepted: bool
    terms_version: str = Field(min_length=1, max_length=20)


class SessionView(BaseModel):
    reference: str | None
    language: str
    country_code: str
    status: CaseStatus
    status_label: str
    status_reason: str | None
    message: str | None
    expires_at: datetime | None
    consent_required: bool
    consent_given: bool
    terms_version: str
    declared_identity_required: bool
    declared_identity: DeclaredIdentityRead | None
    documents_allowed: list[dict[str, Any]]
    instructions: list[str]
    attempts: dict[str, AttemptQuota]
    can_upload: bool
    can_update_identity: bool
    next_action: str


class SessionResult(BaseModel):
    status: CaseStatus
    status_label: str
    message: str | None
    final: bool
    scope: ScopeRead
