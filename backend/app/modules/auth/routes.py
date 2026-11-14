from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import client_ip, get_principal, rate_limited
from app.core.exceptions import NotFound
from app.core.principal import Principal
from app.modules.auth import service
from app.modules.auth.schemas import ChangePasswordRequest, LoginRequest, RefreshRequest, TokenPair
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentification"])
login_limit = Depends(rate_limited("login", "rate_limit_login_per_minute"))


@router.post("/login", response_model=TokenPair, dependencies=[login_limit], summary="Connexion (JSON)")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return service.authenticate(db, payload.email, payload.password, client_ip(request))


@router.post(
    "/token",
    response_model=TokenPair,
    dependencies=[login_limit],
    summary="Connexion (formulaire OAuth2, bouton Authorize de Swagger)",
)
def token(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return service.authenticate(db, form.username, form.password, client_ip(request))


@router.post("/refresh", response_model=TokenPair, dependencies=[login_limit], summary="Renouveler les jetons")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return service.refresh_tokens(db, payload.refresh_token)


@router.get("/me", response_model=UserRead, summary="Profil de l'utilisateur connecté")
def me(principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    user = db.get(User, principal.actor_id) if principal.kind == "user" else None
    if user is None:
        raise NotFound("Aucun profil utilisateur pour cette identité", code="USER_NOT_FOUND")
    return user


@router.post("/change-password", status_code=204, summary="Changer son mot de passe")
def change_password(payload: ChangePasswordRequest, principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    service.change_password(db, principal, payload.current_password, payload.new_password)
    return Response(status_code=204)
