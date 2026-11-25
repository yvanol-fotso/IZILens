import uuid
from dataclasses import dataclass
from typing import Literal

from app.common.enums import ActorType, UserRole


@dataclass(frozen=True)
class Principal:
    """Identité authentifiée de la requête : utilisateur (JWT) ou intégration (clé API)."""

    kind: Literal["user", "api_key"]
    actor_id: uuid.UUID
    organization_id: uuid.UUID | None
    role: UserRole
    enabled_modules: frozenset[str]
    ip: str | None = None
    sandbox: bool = False  # clé Sandbox ou organisation sans accès Production : dossiers non facturés

    @property
    def actor_type(self) -> ActorType:
        return ActorType.USER if self.kind == "user" else ActorType.API_KEY

    @property
    def label(self) -> str:
        return f"{self.kind}:{self.actor_id}"
