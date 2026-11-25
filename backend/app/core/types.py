import json
from typing import Any

from sqlalchemy import JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator

from app.core.crypto import get_cipher

JsonType = JSON().with_variant(JSONB(), "postgresql")


class EncryptedJSON(TypeDecorator):
    """JSON chiffré au repos : réservé aux colonnes contenant des données personnelles."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        if value is None:
            return None
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        return get_cipher().encrypt(payload).decode()

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return json.loads(get_cipher().decrypt(value.encode()))
