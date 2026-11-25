import uuid
from typing import Protocol


class StorageError(Exception):
    pass


class StorageBackend(Protocol):
    def save(self, *, organization_id: uuid.UUID, case_id: uuid.UUID, data: bytes) -> str: ...

    def load(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...
