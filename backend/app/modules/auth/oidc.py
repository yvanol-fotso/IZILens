import logging
from typing import Any, Protocol
from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.core.config import get_settings
from app.core.exceptions import Forbidden, Unauthorized, ValidationFailed
from app.core.time import as_utc, utcnow
from app.modules.audit import service as audit
from app.modules.auth.schemas import TokenPair
from app.modules.auth.service import _organization_usable, issue_tokens
from app.modules.users.models import User, UserIdentity

logger = logging.getLogger("app.oidc")
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"  # noqa: S105


class KeyResolver(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> Any: ...


_resolver: KeyResolver | None = None


def get_key_resolver() -> KeyResolver:
    global _resolver
    if _resolver is None:
        _resolver = PyJWKClient(GOOGLE_JWKS_URI, cache_keys=True, lifespan=3600)
    return _resolver


def set_key_resolver(resolver: KeyResolver | None) -> None:
    """Injecte un résolveur de clés de substitution (tests) ou réinitialise le résolveur par défaut."""
    global _resolver
    _resolver = resolver


def _require_enabled() -> None:
    settings = get_settings()
    if not settings.oidc_enabled or not settings.google_client_id:
        raise Forbidden("La connexion Google n'est pas activée", code="OIDC_DISABLED")


def providers() -> dict[str, dict]:
    settings = get_settings()
    enabled = bool(settings.oidc_enabled and settings.google_client_id)
    return {"google": {"enabled": enabled, "client_id": settings.google_client_id if enabled else None}}


def verify_id_token(id_token: str, nonce: str | None) -> dict[str, Any]:
    """Vérifie signature, émetteur, audience, expiration, e-mail vérifié et nonce d'un jeton d'identité Google."""
    _require_enabled()
    settings = get_settings()
    invalid = Unauthorized("Jeton Google invalide", code="INVALID_ID_TOKEN")
    try:
        key = get_key_resolver().get_signing_key_from_jwt(id_token).key
        claims = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            options={"require": ["exp", "iat", "aud", "iss", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise invalid from exc
    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise invalid
    if not claims.get("email") or claims.get("email_verified") is not True:
        raise Unauthorized("Adresse e-mail Google non vérifiée", code="EMAIL_NOT_VERIFIED")
    if nonce is not None and claims.get("nonce") != nonce:
        raise invalid
    return claims


def login_with_claims(db: Session, claims: dict[str, Any], ip: str | None) -> TokenPair:
    """Connecte un utilisateur déjà invité ; aucun compte n'est créé automatiquement (pas de fuite entre organisations)."""
    subject, email = str(claims["sub"]), str(claims["email"]).lower()
    identity = db.scalar(select(UserIdentity).where(UserIdentity.provider == "google", UserIdentity.subject == subject))
    user = db.get(User, identity.user_id) if identity else db.scalar(select(User).where(User.email == email))
    if user is None:
        raise Forbidden(
            "Aucun compte n'est associé à cette adresse. Demandez une invitation à votre administrateur.",
            code="ACCOUNT_NOT_PROVISIONED",
        )
    if identity is None:
        if db.scalar(select(UserIdentity).where(UserIdentity.user_id == user.id, UserIdentity.provider == "google")):
            raise Forbidden("Ce compte est déjà lié à une autre identité Google", code="IDENTITY_MISMATCH")
        db.add(UserIdentity(user_id=user.id, provider="google", subject=subject, email=email))
    locked = user.locked_until is not None and as_utc(user.locked_until) > utcnow()
    if not user.is_active or locked or not _organization_usable(db, user) or user.role == UserRole.INTEGRATION:
        audit.record(
            db,
            action="auth.oidc_denied",
            resource_type="user",
            resource_id=user.id,
            organization_id=user.organization_id,
            details={"ip": ip},
        )
        db.commit()
        raise Unauthorized("Connexion refusée", code="INVALID_CREDENTIALS")
    user.last_login_at = utcnow()
    user.failed_login_attempts = 0
    audit.record(
        db,
        action="auth.oidc_login_succeeded",
        resource_type="user",
        resource_id=user.id,
        organization_id=user.organization_id,
        details={"ip": ip, "provider": "google"},
    )
    db.commit()
    return issue_tokens(user)


def authorize_url(redirect_uri: str, state: str, nonce: str, code_challenge: str) -> str:
    _require_enabled()
    settings = get_settings()
    if redirect_uri not in settings.oidc_allowed_redirect_uris:
        raise ValidationFailed("redirect_uri non autorisée", code="REDIRECT_URI_NOT_ALLOWED")
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTH_ENDPOINT}?{query}"


def exchange_code(code: str, redirect_uri: str, code_verifier: str, *, client: httpx.Client | None = None) -> str:
    _require_enabled()
    settings = get_settings()
    if redirect_uri not in settings.oidc_allowed_redirect_uris:
        raise ValidationFailed("redirect_uri non autorisée", code="REDIRECT_URI_NOT_ALLOWED")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": settings.google_client_id,
        "code_verifier": code_verifier,
    }
    if settings.google_client_secret:
        data["client_secret"] = settings.google_client_secret
    http = client or httpx.Client(timeout=10.0)
    try:
        response = http.post(GOOGLE_TOKEN_ENDPOINT, data=data)
    except httpx.HTTPError as exc:
        logger.warning("Échec de l'échange de code OIDC")
        raise Unauthorized("Échange du code impossible", code="OIDC_EXCHANGE_FAILED") from exc
    finally:
        if client is None:
            http.close()
    id_token = response.json().get("id_token") if response.status_code == 200 else None
    if not id_token:
        raise Unauthorized("Échange du code refusé", code="OIDC_EXCHANGE_FAILED")
    return id_token
