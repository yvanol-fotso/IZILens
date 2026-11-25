import uuid
from datetime import timedelta

import jwt
import pytest

from app.common.enums import UserRole
from app.core import security
from app.core.config import get_settings
from app.core.exceptions import Unauthorized
from app.core.time import utcnow


def test_password_roundtrip_and_unknown_user_is_constant_path():
    hashed = security.hash_password("Sup3rSecretPass99")
    assert security.verify_password("Sup3rSecretPass99", hashed)
    assert not security.verify_password("wrong-password-1", hashed)
    assert not security.verify_password("anything", None)


def test_access_token_roundtrip():
    user_id, org_id = uuid.uuid4(), uuid.uuid4()
    token, expires = security.create_token(user_id=user_id, organization_id=org_id, role=UserRole.ADMIN, token_type="access")
    claims = security.decode_token(token, "access")
    assert (claims["sub"], claims["org"], claims["role"]) == (str(user_id), str(org_id), "admin") and expires > 0


def test_refresh_token_cannot_be_used_as_access():
    token, _ = security.create_token(user_id=uuid.uuid4(), organization_id=None, role=UserRole.ADMIN, token_type="refresh")
    with pytest.raises(Unauthorized):
        security.decode_token(token, "access")


def test_tampered_and_expired_tokens_rejected():
    token, _ = security.create_token(user_id=uuid.uuid4(), organization_id=None, role=UserRole.ADMIN, token_type="access")
    with pytest.raises(Unauthorized):
        security.decode_token(token[:-3] + "abc", "access")
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "x", "typ": "access", "iat": utcnow() - timedelta(hours=2), "exp": utcnow() - timedelta(hours=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(Unauthorized):
        security.decode_token(expired, "access")


def test_token_signed_with_other_secret_rejected():
    forged = jwt.encode(
        {"sub": "x", "typ": "access", "iat": utcnow(), "exp": utcnow() + timedelta(hours=1)}, "x" * 40, algorithm="HS256"
    )
    with pytest.raises(Unauthorized):
        security.decode_token(forged, "access")


def test_api_key_format_and_digest():
    full, prefix, digest = security.generate_api_key()
    assert security.parse_api_key_prefix(full) == prefix
    assert security.digests_match(security.keyed_digest(full), digest)
    assert full not in digest
    assert security.parse_api_key_prefix("not-a-key") is None
    assert security.parse_api_key_prefix("izl_test_short_x") is None
