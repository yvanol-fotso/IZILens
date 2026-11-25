"""Importe tous les modèles pour qu'Alembic et SQLAlchemy voient l'ensemble du schéma."""

from app.core.database import Base
from app.modules.api_keys.models import ApiKey
from app.modules.audit.models import AuditLog
from app.modules.billing.models import BillingEvent, BillingPlan, CreditNote, DocumentCounter, Invoice, Subscription
from app.modules.cms.models import CmsEntry
from app.modules.developers.models import DeveloperAccessRequest
from app.modules.kyc.models import KycAttempt, KycCase, KycCheck, KycDocument, KycDocumentCoverage, KycEvent, KycJourney
from app.modules.notifications.models import EmailOutbox
from app.modules.organizations.models import Organization
from app.modules.public_requests.models import PublicRequest, PublicRequestEvent
from app.modules.users.models import User, UserIdentity, UserMfa
from app.modules.webhooks.models import WebhookDelivery, WebhookEndpoint

__all__ = [
    "ApiKey",
    "AuditLog",
    "Base",
    "BillingEvent",
    "BillingPlan",
    "CmsEntry",
    "CreditNote",
    "DeveloperAccessRequest",
    "DocumentCounter",
    "EmailOutbox",
    "Invoice",
    "KycAttempt",
    "KycCase",
    "KycCheck",
    "KycDocument",
    "KycDocumentCoverage",
    "KycEvent",
    "KycJourney",
    "Organization",
    "PublicRequest",
    "PublicRequestEvent",
    "Subscription",
    "User",
    "UserIdentity",
    "UserMfa",
    "WebhookDelivery",
    "WebhookEndpoint",
]
