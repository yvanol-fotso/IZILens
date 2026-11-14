import uuid
from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.constants import API_PREFIX
from app.common.enums import UserRole
from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import Forbidden, Unauthorized
from app.core.principal import Principal
from app.core.rate_limit import limiter
from app.core.security import decode_token
from app.core.time import as_utc, utcnow
from app.modules.api_keys.service import authenticate_api_key
from app.modules.organizations.models import Organization
from app.modules.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/auth/token", auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _principal_from_token(db: Session, token: str, ip: str | None) -> Principal:
    claims = decode_token(token, "access")
    user = db.get(User, uuid.UUID(claims["sub"]))
    unauthorized = Unauthorized("Session invalide", code="INVALID_TOKEN")
    if user is None or not user.is_active:
        raise unauthorized
    if user.locked_until is not None and as_utc(user.locked_until) > utcnow():
        raise unauthorized
    modules: frozenset[str] = frozenset()
    if user.organization_id is not None:
        organization = db.get(Organization, user.organization_id)
        if organization is None or not organization.is_active:
            raise Forbidden("Organisation désactivée", code="ORGANIZATION_DISABLED")
        modules = frozenset(organization.enabled_modules)
    return Principal(
        kind="user",
        actor_id=user.id,
        organization_id=user.organization_id,
        role=user.role,
        enabled_modules=modules,
        ip=ip,
    )


def get_principal(
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
    raw_api_key: str | None = Depends(api_key_scheme),
) -> Principal:
    ip = client_ip(request)
    if raw_api_key:
        return authenticate_api_key(db, raw_api_key, ip)
    if token:
        return _principal_from_token(db, token, ip)
    raise Unauthorized("Authentification requise", code="AUTHENTICATION_REQUIRED", headers={"WWW-Authenticate": "Bearer"})


def require_access(*roles: UserRole, module: str | None = None, tenant: bool = True) -> Callable[..., Principal]:
    """Dépendance d'autorisation : rôle, appartenance à une organisation et module souscrit."""

    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in roles:
            raise Forbidden("Droits insuffisants", code="INSUFFICIENT_ROLE")
        if tenant and principal.organization_id is None:
            raise Forbidden("Une organisation est requise", code="ORGANIZATION_REQUIRED")
        if module and module not in principal.enabled_modules:
            raise Forbidden(f"Le module '{module}' n'est pas activé pour votre organisation", code="MODULE_NOT_ENABLED")
        return principal

    return dependency


def rate_limited(scope: str, limit_attr: str) -> Callable[..., None]:
    """Limite par adresse IP pour les routes publiques (ex. connexion)."""

    def dependency(request: Request) -> None:
        limiter.check(f"{scope}:{client_ip(request)}", getattr(get_settings(), limit_attr), 60)

    return dependency
