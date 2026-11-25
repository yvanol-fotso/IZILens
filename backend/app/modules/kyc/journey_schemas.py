import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.common.enums import ReviewTeam
from app.modules.kyc import defaults


class JourneyConfig(BaseModel):
    required_checks: list[str] | None = None
    max_attempts: dict[str, int] | None = None
    expiry_hours: int | None = Field(default=None, ge=1, le=24 * 90)
    auto_decision_enabled: bool | None = None
    review_team: ReviewTeam | None = None
    thresholds: dict[str, float] | None = None
    decision_rules: dict[str, str] | None = None
    billing: dict[str, bool] | None = None

    @field_validator("required_checks")
    @classmethod
    def _checks(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        unknown = set(value) - set(defaults.CHECK_TYPES_REQUIRABLE)
        if unknown:
            raise ValueError(f"Contrôles inconnus : {', '.join(sorted(unknown))}")
        return sorted(set(value), key=defaults.CHECK_TYPES_REQUIRABLE.index)

    @field_validator("max_attempts")
    @classmethod
    def _attempts(cls, value: dict[str, int] | None) -> dict[str, int] | None:
        if value is None:
            return None
        if set(value) - set(defaults.ATTEMPT_KINDS_LIMITED) or any(not 0 <= v <= 10 for v in value.values()):
            raise ValueError("Limites de tentatives invalides (0 à 10, types connus uniquement)")
        return value

    @field_validator("thresholds")
    @classmethod
    def _thresholds(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        if value is None:
            return None
        if set(value) - set(defaults.THRESHOLD_KEYS) or any(not 0.0 <= v <= 1.0 for v in value.values()):
            raise ValueError("Seuils invalides (clés connues, valeurs entre 0 et 1)")
        return value

    @field_validator("decision_rules")
    @classmethod
    def _rules(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return None
        if set(value) - set(defaults.DECISION_RULE_KEYS) or any(v not in defaults.DECISION_RULE_VALUES for v in value.values()):
            raise ValueError("Règles de décision invalides")
        return value

    @field_validator("billing")
    @classmethod
    def _billing(cls, value: dict[str, bool] | None) -> dict[str, bool] | None:
        if value is not None and set(value) - set(defaults.BILLING_KEYS):
            raise ValueError("Clés de facturation inconnues")
        return value


class JourneyCreate(JourneyConfig):
    code: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{1,38}[a-z0-9]$")
    name: str = Field(min_length=2, max_length=120)
    is_default: bool = False


class JourneyUpdate(JourneyConfig):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    is_active: bool | None = None
    is_default: bool | None = None
    parameters_validated: bool | None = None


class JourneyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None
    code: str
    name: str
    is_active: bool
    is_default: bool
    required_checks: list[str]
    max_attempts: dict[str, int]
    expiry_hours: int
    auto_decision_enabled: bool
    review_team: str
    thresholds: dict[str, float]
    decision_rules: dict[str, str]
    billing: dict[str, bool]
    parameters_validated: bool
    created_at: datetime


class CoverageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    country_code: str
    document_type: str
    label_fr: str
    label_en: str
    sides_required: list[str]
    status: str
    validated_at: datetime | None
    notes: str | None


class CoverageUpsert(BaseModel):
    country_code: str = Field(pattern=r"^[A-Z]{2}$")
    document_type: str = Field(pattern=r"^[a-z0-9_]{2,32}$")
    label_fr: str = Field(min_length=2, max_length=120)
    label_en: str = Field(min_length=2, max_length=120)
    sides_required: list[str] = ["front"]
    status: str = Field(default="planned", pattern=r"^(planned|testing|supported|disabled)$")
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("sides_required")
    @classmethod
    def _sides(cls, value: list[str]) -> list[str]:
        if not value or "front" not in value or set(value) - {"front", "back"}:
            raise ValueError("Faces invalides : 'front' est obligatoire, 'back' optionnel")
        return sorted(set(value), reverse=True)


class CoverageUpdate(BaseModel):
    label_fr: str | None = Field(default=None, min_length=2, max_length=120)
    label_en: str | None = Field(default=None, min_length=2, max_length=120)
    sides_required: list[str] | None = None
    status: str | None = Field(default=None, pattern=r"^(planned|testing|supported|disabled)$")
    notes: str | None = Field(default=None, max_length=500)


class CoverageOverview(BaseModel):
    supported: list[CoverageRead]
    gaps: list[str]
