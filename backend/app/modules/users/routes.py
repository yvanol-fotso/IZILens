import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.schemas import Page
from app.core.database import get_db
from app.core.dependencies import get_principal, require_access
from app.core.principal import Principal
from app.modules.users import service
from app.modules.users.schemas import ProfileUpdate, UserCreate, UserRead, UserStatusUpdate, UserUpdate

router = APIRouter(prefix="/users", tags=["Utilisateurs"])
manage_users = require_access(UserRole.SUPER_ADMIN, UserRole.ADMIN, tenant=False)


@router.post("", response_model=UserRead, status_code=201, summary="Créer un utilisateur")
def create_user(payload: UserCreate, principal: Principal = Depends(manage_users), db: Session = Depends(get_db)):
    return service.create_user(db, principal, payload)


@router.get("", response_model=Page[UserRead], summary="Lister les utilisateurs")
def list_users(
    organization_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    principal: Principal = Depends(manage_users),
    db: Session = Depends(get_db),
):
    items, total = service.list_users(db, principal, organization_id, page, page_size)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.patch("/me", response_model=UserRead, summary="Modifier son profil")
def update_me(payload: ProfileUpdate, principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    return service.update_profile(db, principal, payload.full_name)


@router.patch("/{user_id}", response_model=UserRead, summary="Modifier nom, rôle, statut ou rattachement d'un utilisateur")
def update_user(
    user_id: uuid.UUID, payload: UserUpdate, principal: Principal = Depends(manage_users), db: Session = Depends(get_db)
):
    return service.update_user(db, principal, user_id, payload)


@router.patch("/{user_id}/status", response_model=UserRead, summary="Activer ou désactiver un utilisateur")
def update_status(
    user_id: uuid.UUID, payload: UserStatusUpdate, principal: Principal = Depends(manage_users), db: Session = Depends(get_db)
):
    return service.set_user_active(db, principal, user_id, payload.is_active)
