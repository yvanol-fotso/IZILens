from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import client_ip, get_principal, rate_limited
from app.core.exceptions import NotFound
from app.core.principal import Principal
from app.modules.auth import mfa, oidc, service
from app.modules.auth.schemas import (
    AuthorizeUrlResponse,
    ChangePasswordRequest,
    GoogleCodeRequest,
    GoogleIdTokenRequest,
    LoginRequest,
    MfaCodeRequest,
    MfaDisableRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentification"])
login_limit = Depends(rate_limited("login", "rate_limit_login_per_minute"))


@router.post("/login", response_model=TokenPair, dependencies=[login_limit], summary="Connexion (JSON)")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return service.authenticate(db, payload.email, payload.password, client_ip(request), payload.mfa_code)


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


@router.get("/oidc/providers", summary="Fournisseurs de connexion fédérée disponibles")
def oidc_providers():
    return oidc.providers()


@router.get("/oidc/google/authorize", response_model=AuthorizeUrlResponse, summary="URL de connexion Google (flux code + PKCE)")
def google_authorize(
    redirect_uri: str = Query(..., max_length=500),
    state: str = Query(..., min_length=8, max_length=128),
    nonce: str = Query(..., min_length=8, max_length=128),
    code_challenge: str = Query(..., min_length=43, max_length=128),
):
    return AuthorizeUrlResponse(authorization_url=oidc.authorize_url(redirect_uri, state, nonce, code_challenge))


@router.post(
    "/oidc/google/token",
    response_model=TokenPair,
    dependencies=[login_limit],
    summary="Connexion avec un jeton d'identité Google (bouton Google)",
)
def google_id_token(payload: GoogleIdTokenRequest, request: Request, db: Session = Depends(get_db)):
    claims = oidc.verify_id_token(payload.id_token, payload.nonce)
    return oidc.login_with_claims(db, claims, client_ip(request))


@router.post(
    "/oidc/google/callback",
    response_model=TokenPair,
    dependencies=[login_limit],
    summary="Connexion Google : échange du code d'autorisation",
)
def google_callback(payload: GoogleCodeRequest, request: Request, db: Session = Depends(get_db)):
    id_token = oidc.exchange_code(payload.code, payload.redirect_uri, payload.code_verifier)
    claims = oidc.verify_id_token(id_token, payload.nonce)
    return oidc.login_with_claims(db, claims, client_ip(request))


@router.post(
    "/register",
    status_code=202,
    dependencies=[login_limit],
    summary="Créer un compte (sans accès tant qu'une demande n'est pas approuvée)",
)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    service.register(db, full_name=payload.full_name, email=payload.email, password=payload.password, ip=client_ip(request))
    return {"status": "registered"}


@router.post("/logout", status_code=204, summary="Fermer la session")
def logout(principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    service.logout(db, principal)
    return Response(status_code=204)


@router.post(
    "/oauth/google",
    response_model=TokenPair,
    dependencies=[login_limit],
    summary="Connexion Google (jeton d'identité obtenu par le dashboard)",
)
def oauth_google(payload: GoogleIdTokenRequest, request: Request, db: Session = Depends(get_db)):
    claims = oidc.verify_id_token(payload.id_token, payload.nonce)
    return oidc.login_with_claims(db, claims, client_ip(request))


@router.get("/mfa/status", summary="État de l'authentification à deux facteurs")
def mfa_status(principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    return mfa.status(db, principal)


@router.post("/mfa/enroll", summary="Démarrer l'activation TOTP (secret et URI pour QR code)")
def mfa_enroll(principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    return mfa.enroll(db, principal)


@router.post("/mfa/verify", summary="Confirmer l'activation avec un code ; renvoie les codes de secours (une seule fois)")
def mfa_verify(payload: MfaCodeRequest, principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    return mfa.activate(db, principal, payload.code)


@router.post("/mfa/recovery-codes", summary="Régénérer les codes de secours")
def mfa_recovery(payload: MfaCodeRequest, principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    return mfa.regenerate_recovery_codes(db, principal, payload.code)


@router.post("/mfa/disable", status_code=204, summary="Désactiver l'authentification à deux facteurs")
def mfa_disable(payload: MfaDisableRequest, principal: Principal = Depends(get_principal), db: Session = Depends(get_db)):
    mfa.disable(db, principal, payload.password, payload.code)
    return Response(status_code=204)
