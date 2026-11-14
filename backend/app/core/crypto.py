from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.core.config import get_settings


class DecryptionError(Exception):
    pass


class DataCipher:
    """Chiffrement symétrique avec rotation de clés (la première clé chiffre, toutes déchiffrent)."""

    def __init__(self, keys: list[str]) -> None:
        self._fernet = MultiFernet([Fernet(key.encode()) for key in keys])

    def encrypt(self, data: bytes) -> bytes:
        return self._fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        try:
            return self._fernet.decrypt(token)
        except InvalidToken as exc:
            raise DecryptionError("Donnée illisible avec les clés configurées") from exc


@lru_cache
def get_cipher() -> DataCipher:
    return DataCipher(get_settings().encryption_keys)
