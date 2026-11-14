import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.users import service
from app.modules.users.schemas import UserCreate, UserRead, UserStatusUpdate

router = APIRouter(prefix="/users", tags=["Utilisateurs"])
manage_users = require_access(UserRole.SUPER_ADMIN, UserRole.ADMIN, tenant=False)


@router.post("", response_model=UserRead, status_code=201, summary="Créer un utilisateur")
def create_user(payload: UserCreate, principal: Principal = Depends(manage_users), db: Session = Depends(get_db)):
    return service.create_user(db, principal, payload)


@router.get("", response_model=Page[UserRead], summary="Lister les utilisateurs")
def list_users(
    organization_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    principal: Principal = Depends(manage_users),
    db: Session = Depends(get_db),
):
    items, total = service.list_users(db, principal, organization_id, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{user_id}/status", response_model=UserRead, summary="Activer ou désactiver un utilisateur")
def update_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    principal: Principal = Depends(manage_users),
    db: Session = Depends(get_db),
):
    return service.set_user_active(db, principal, user_id, payload.is_active)
