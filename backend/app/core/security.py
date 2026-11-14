import hashlib
import hmac
import secrets
import uuid
from datetime import timedelta
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.common.enums import UserRole
from app.core.config import get_settings
from app.core.exceptions import Unauthorized
from app.core.time import utcnow

TokenType = Literal["access", "refresh"]
API_KEY_PREFIX = "izl"

_hasher = PasswordHasher()
_DUMMY_HASH = _hasher.hash("dummy-password-for-constant-time")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Vérifie en temps constant, même si l'utilisateur n'existe pas."""
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


def create_token(
    *, user_id: uuid.UUID, organization_id: uuid.UUID | None, role: UserRole, token_type: TokenType
) -> tuple[str, int]:
    settings = get_settings()
    lifetime = (
        timedelta(minutes=settings.access_token_minutes)
        if token_type == "access"
        else timedelta(days=settings.refresh_token_days)
    )
    now = utcnow()
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "org": str(organization_id) if organization_id else None,
        "role": role.value,
        "typ": token_type,
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + lifetime,
    }
    token = jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(lifetime.total_seconds())


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat", "typ"]},
        )
    except jwt.PyJWTError as exc:
        raise Unauthorized("Jeton invalide ou expiré", code="INVALID_TOKEN") from exc
    if claims.get("typ") != expected_type:
        raise Unauthorized("Type de jeton incorrect", code="INVALID_TOKEN")
    return claims


def keyed_digest(value: str) -> str:
    """HMAC-SHA256 avec poivre serveur : empreintes non réversibles par dictionnaire."""
    pepper = get_settings().api_key_pepper.encode()
    return hmac.new(pepper, value.encode(), hashlib.sha256).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """Retourne (clé complète, préfixe public, empreinte stockée) ; la clé n'est jamais conservée."""
    env = "live" if get_settings().is_production else "test"
    prefix = secrets.token_hex(4)
    full_key = f"{API_KEY_PREFIX}_{env}_{prefix}_{secrets.token_urlsafe(32)}"
    return full_key, prefix, keyed_digest(full_key)


def parse_api_key_prefix(raw_key: str) -> str | None:
    parts = raw_key.split("_", 3)
    if len(parts) != 4 or parts[0] != API_KEY_PREFIX or len(parts[2]) != 8:
        return None
    return parts[2]


def digests_match(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)
