import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.common.constants import CURRENCIES
from app.common.enums import BillingEventType

MONEY = Field(ge=Decimal("0"), le=Decimal("1000000000"), decimal_places=2)


class UsageLine(BaseModel):
    organization_id: uuid.UUID
    event_type: str
    billable: bool
    events: int
    units: int


class CurrencyPrices(BaseModel):
    monthly_fee: Decimal = MONEY
    unit_prices: dict[str, Decimal] = {}

    @field_validator("monthly_fee", mode="before")
    @classmethod
    def _default_fee(cls, value):
        return Decimal("0") if value is None else value

    @field_validator("unit_prices")
    @classmethod
    def _unit(cls, value: dict[str, Decimal]) -> dict[str, Decimal]:
        known = {e.value for e in BillingEventType}
        if set(value) - known or any(v < 0 or v.as_tuple().exponent < -2 for v in value.values()):
            raise ValueError("Prix unitaires invalides (types connus, montants positifs à 2 décimales)")
        return value


class PlanCreate(BaseModel):
    code: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{1,38}[a-z0-9]$")
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=400)
    prices: dict[str, CurrencyPrices]

    @field_validator("prices")
    @classmethod
    def _currencies(cls, value: dict[str, CurrencyPrices]) -> dict[str, CurrencyPrices]:
        if not value or set(value) - CURRENCIES:
            raise ValueError(f"Devises autorisées : {', '.join(sorted(CURRENCIES))}")
        return value


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=400)
    is_active: bool | None = None
    prices: dict[str, CurrencyPrices] | None = None

    @field_validator("prices")
    @classmethod
    def _currencies(cls, value):
        if value is not None and (not value or set(value) - CURRENCIES):
            raise ValueError(f"Devises autorisées : {', '.join(sorted(CURRENCIES))}")
        return value


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    prices: dict
    created_at: datetime


class SubscriptionCreate(BaseModel):
    organization_id: uuid.UUID
    plan_id: uuid.UUID
    currency: str
    tax_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"), decimal_places=2)
    started_at: date | None = None

    @field_validator("currency")
    @classmethod
    def _currency(cls, value: str) -> str:
        if value not in CURRENCIES:
            raise ValueError("Devise non autorisée")
        return value


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    plan_id: uuid.UUID
    currency: str
    status: str
    tax_rate: Decimal
    started_at: date
    ended_at: date | None


class InvoiceGenerate(BaseModel):
    organization_id: uuid.UUID
    period_start: date
    period_end: date

    @model_validator(mode="after")
    def _period(self) -> "InvoiceGenerate":
        if self.period_end < self.period_start or (self.period_end - self.period_start).days > 366:
            raise ValueError("Période invalide (fin après début, 366 jours maximum)")
        return self


class CreditNoteCreate(BaseModel):
    amount: Decimal = Field(gt=Decimal("0"), le=Decimal("1000000000"), decimal_places=2)
    reason: str = Field(min_length=5, max_length=300)


class CreditNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str
    invoice_id: uuid.UUID
    currency: str
    amount: Decimal
    reason: str
    issued_at: datetime


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str | None
    organization_id: uuid.UUID
    period_start: date
    period_end: date
    currency: str
    status: str
    lines: list[dict]
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    issued_at: datetime | None
    due_at: date | None
    paid_at: datetime | None
    voided_at: datetime | None
    credit_notes: list[CreditNoteRead] = []
    credited_total: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")


class Consumption(BaseModel):
    currency: str | None
    period_start: date
    period_end: date
    lines: list[dict]
    estimated_total: Decimal | None
