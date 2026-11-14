"""Importe tous les modèles pour qu'Alembic et SQLAlchemy voient l'ensemble du schéma."""

from app.core.database import Base
from app.modules.api_keys.models import ApiKey
from app.modules.audit.models import AuditLog
from app.modules.kyc.models import KycCase, KycDocument
from app.modules.organizations.models import Organization
from app.modules.users.models import User

__all__ = ["ApiKey", "AuditLog", "Base", "KycCase", "KycDocument", "Organization", "User"]
