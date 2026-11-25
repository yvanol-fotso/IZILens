import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

KINDS = ("blog", "guide", "faq")
_FORBIDDEN = re.compile(r"<\s*(script|iframe|object|embed)|javascript:|on\w+\s*=", re.IGNORECASE)


def _safe(value: str | None) -> str | None:
    if value is not None and _FORBIDDEN.search(value):
        raise ValueError("Contenu non autorisé (balises actives)")
    return value


class EntryBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    summary: str | None = Field(default=None, max_length=400)
    body: str = Field(min_length=1, max_length=60000)
    category: str | None = Field(default=None, max_length=60)
    tags: list[str] = Field(default=[], max_length=12)
    position: int = Field(default=0, ge=0, le=10000)

    _body = field_validator("body", "summary", "title")(_safe)

    @field_validator("tags")
    @classmethod
    def _tags(cls, value: list[str]) -> list[str]:
        return sorted({t.strip().lower()[:30] for t in value if t.strip()})


class EntryCreate(EntryBase):
    kind: str = Field(pattern=r"^(blog|guide|faq)$")
    locale: str = Field(pattern=r"^(fr|en)$")
    slug: str = Field(pattern=r"^[a-z0-9](?:[a-z0-9-]{0,110}[a-z0-9])?$")


class EntryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    summary: str | None = Field(default=None, max_length=400)
    body: str | None = Field(default=None, min_length=1, max_length=60000)
    category: str | None = Field(default=None, max_length=60)
    tags: list[str] | None = None
    position: int | None = Field(default=None, ge=0, le=10000)

    _body = field_validator("body", "summary", "title")(_safe)


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: str
    locale: str
    slug: str
    title: str
    summary: str | None
    body: str
    category: str | None
    tags: list[str]
    status: str
    position: int
    published_at: datetime | None
    updated_at: datetime


class EntryListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: str
    locale: str
    slug: str
    title: str
    summary: str | None
    category: str | None
    tags: list[str]
    status: str
    position: int
    published_at: datetime | None
