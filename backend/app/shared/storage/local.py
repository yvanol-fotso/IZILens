import os
import uuid
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.core.crypto import DataCipher, DecryptionError, get_cipher
from app.shared.storage.base import StorageBackend, StorageError


class LocalEncryptedStorage:
    """Stockage disque chiffré au repos ; remplaçable par un stockage objet via StorageBackend."""

    def __init__(self, root: Path, cipher: DataCipher) -> None:
        self._root = root.resolve()
        self._cipher = cipher
        self._root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if self._root not in path.parents:
            raise StorageError("Clé de stockage invalide")
        return path

    def save(self, *, organization_id: uuid.UUID, case_id: uuid.UUID, data: bytes) -> str:
        key = f"{organization_id}/{case_id}/{uuid.uuid4().hex}.bin"
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(self._cipher.encrypt(data))
        os.replace(temporary, path)  # écriture atomique : jamais de fichier partiel
        return key

    def load(self, key: str) -> bytes:
        path = self._resolve(key)
        try:
            return self._cipher.decrypt(path.read_bytes())
        except FileNotFoundError as exc:
            raise StorageError("Fichier introuvable") from exc
        except DecryptionError as exc:
            raise StorageError("Fichier illisible") from exc

    def delete(self, key: str) -> None:
        self._resolve(key).unlink(missing_ok=True)


@lru_cache
def get_storage() -> StorageBackend:
    return LocalEncryptedStorage(get_settings().storage_dir, get_cipher())
