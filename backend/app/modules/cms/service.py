import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import Conflict, NotFound
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.cms.models import CmsEntry
from app.modules.cms.schemas import EntryCreate, EntryUpdate


def create(db: Session, principal: Principal, payload: EntryCreate) -> CmsEntry:
    entry = CmsEntry(**payload.model_dump(), author_user_id=principal.actor_id)
    db.add(entry)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Ce contenu existe déjà dans cette langue", code="SLUG_ALREADY_USED") from exc
    audit.record(
        db,
        action="cms.created",
        resource_type="cms_entry",
        resource_id=entry.id,
        principal=principal,
        details={"kind": entry.kind},
    )
    db.commit()
    return entry


def get(db: Session, entry_id: uuid.UUID) -> CmsEntry:
    entry = db.get(CmsEntry, entry_id)
    if entry is None:
        raise NotFound("Contenu introuvable", code="CONTENT_NOT_FOUND")
    return entry


def update(db: Session, principal: Principal, entry: CmsEntry, payload: EntryUpdate) -> CmsEntry:
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in changes.items():
        setattr(entry, key, value)
    audit.record(
        db,
        action="cms.updated",
        resource_type="cms_entry",
        resource_id=entry.id,
        principal=principal,
        details={"fields": sorted(changes)},
    )
    db.commit()
    return entry


def set_status(db: Session, principal: Principal, entry: CmsEntry, status: str) -> CmsEntry:
    entry.status = status
    if status == "published" and entry.published_at is None:
        entry.published_at = utcnow()
    audit.record(db, action=f"cms.{status}", resource_type="cms_entry", resource_id=entry.id, principal=principal)
    db.commit()
    return entry


def delete(db: Session, principal: Principal, entry: CmsEntry) -> None:
    audit.record(
        db,
        action="cms.deleted",
        resource_type="cms_entry",
        resource_id=entry.id,
        principal=principal,
        details={"kind": entry.kind},
    )
    db.delete(entry)
    db.commit()


def _query(
    *,
    kind: str | None,
    locale: str | None,
    category: str | None,
    search: str | None,
    tag: str | None,
    published_only: bool,
    status: str | None = None,
):
    query = select(CmsEntry)
    if published_only:
        query = query.where(CmsEntry.status == "published")
    elif status:
        query = query.where(CmsEntry.status == status)
    if kind:
        query = query.where(CmsEntry.kind == kind)
    if locale:
        query = query.where(CmsEntry.locale == locale)
    if category:
        query = query.where(CmsEntry.category == category)
    if tag:
        pass  # filtre par étiquette appliqué après lecture (portable SQLite et PostgreSQL)
    if search:
        pattern = f"%{search.strip()[:64]}%"
        query = query.where(or_(CmsEntry.title.ilike(pattern), CmsEntry.summary.ilike(pattern), CmsEntry.body.ilike(pattern)))
    return query


def list_entries(db: Session, *, page: int, page_size: int, **filters) -> tuple[list[CmsEntry], int]:
    query = _query(**filters)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    order = (
        (CmsEntry.position.asc(), CmsEntry.title.asc())
        if filters.get("kind") == "faq"
        else (CmsEntry.published_at.desc().nulls_last(), CmsEntry.created_at.desc())
    )
    rows = db.scalars(query.order_by(*order).offset((page - 1) * page_size).limit(page_size)).all()
    tag = filters.get("tag")
    if tag:
        rows = [r for r in rows if tag.lower() in (r.tags or [])]
    return list(rows), total


def get_public(db: Session, kind: str, slug: str, locale: str) -> CmsEntry:
    entry = db.scalar(
        select(CmsEntry).where(
            CmsEntry.kind == kind, CmsEntry.slug == slug, CmsEntry.locale == locale, CmsEntry.status == "published"
        )
    )
    if entry is None:
        raise NotFound("Contenu introuvable", code="CONTENT_NOT_FOUND")
    return entry
