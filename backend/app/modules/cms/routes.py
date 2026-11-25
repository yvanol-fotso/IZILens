import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.cms import service
from app.modules.cms.schemas import EntryCreate, EntryListItem, EntryRead, EntryUpdate

public_router = APIRouter(prefix="/public/content", tags=["Public : contenus"])
admin_router = APIRouter(prefix="/admin/cms", tags=["Back-office : contenus éditoriaux"])
editor = require_access(UserRole.SUPER_ADMIN, UserRole.CONTENT_EDITOR, tenant=False)
KIND = Query(None, pattern=r"^(blog|guide|faq)$")
LOCALE = Query(None, pattern=r"^(fr|en)$")


@public_router.get("", response_model=Page[EntryListItem], summary="Contenus publiés (blog, guides, FAQ) avec recherche")
def public_list(
    response: Response,
    kind: str | None = KIND,
    locale: str | None = LOCALE,
    category: str | None = Query(None, max_length=60),
    search: str | None = Query(None, max_length=64),
    tag: str | None = Query(None, max_length=30),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "public, max-age=60"
    items, total = service.list_entries(
        db,
        kind=kind,
        locale=locale,
        category=category,
        search=search,
        tag=tag,
        published_only=True,
        page=page,
        page_size=page_size,
    )
    return Page(items=[EntryListItem.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@public_router.get("/{kind}/{slug}", response_model=EntryRead, summary="Lire un contenu publié")
def public_get(
    response: Response, kind: str, slug: str, locale: str = Query("fr", pattern=r"^(fr|en)$"), db: Session = Depends(get_db)
):
    response.headers["Cache-Control"] = "public, max-age=60"
    return service.get_public(db, kind, slug, locale)


@admin_router.get("", response_model=Page[EntryListItem], summary="Tous les contenus, brouillons compris")
def admin_list(
    kind: str | None = KIND,
    locale: str | None = LOCALE,
    status: str | None = Query(None, pattern=r"^(draft|published|archived)$"),
    category: str | None = None,
    search: str | None = Query(None, max_length=64),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    _: Principal = Depends(editor),
    db: Session = Depends(get_db),
):
    items, total = service.list_entries(
        db,
        kind=kind,
        locale=locale,
        category=category,
        search=search,
        tag=None,
        published_only=False,
        status=status,
        page=page,
        page_size=page_size,
    )
    return Page(items=[EntryListItem.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@admin_router.post("", response_model=EntryRead, status_code=201, summary="Créer un contenu (brouillon)")
def admin_create(payload: EntryCreate, principal: Principal = Depends(editor), db: Session = Depends(get_db)):
    return service.create(db, principal, payload)


@admin_router.get("/{entry_id}", response_model=EntryRead, summary="Lire un contenu")
def admin_get(entry_id: uuid.UUID, _: Principal = Depends(editor), db: Session = Depends(get_db)):
    return service.get(db, entry_id)


@admin_router.patch("/{entry_id}", response_model=EntryRead, summary="Modifier un contenu")
def admin_update(
    entry_id: uuid.UUID, payload: EntryUpdate, principal: Principal = Depends(editor), db: Session = Depends(get_db)
):
    return service.update(db, principal, service.get(db, entry_id), payload)


@admin_router.post("/{entry_id}/publish", response_model=EntryRead, summary="Publier")
def admin_publish(entry_id: uuid.UUID, principal: Principal = Depends(editor), db: Session = Depends(get_db)):
    return service.set_status(db, principal, service.get(db, entry_id), "published")


@admin_router.post("/{entry_id}/unpublish", response_model=EntryRead, summary="Repasser en brouillon")
def admin_unpublish(entry_id: uuid.UUID, principal: Principal = Depends(editor), db: Session = Depends(get_db)):
    return service.set_status(db, principal, service.get(db, entry_id), "draft")


@admin_router.post("/{entry_id}/archive", response_model=EntryRead, summary="Archiver")
def admin_archive(entry_id: uuid.UUID, principal: Principal = Depends(editor), db: Session = Depends(get_db)):
    return service.set_status(db, principal, service.get(db, entry_id), "archived")


@admin_router.delete("/{entry_id}", status_code=204, summary="Supprimer définitivement")
def admin_delete(entry_id: uuid.UUID, principal: Principal = Depends(editor), db: Session = Depends(get_db)):
    service.delete(db, principal, service.get(db, entry_id))
    return Response(status_code=204)
