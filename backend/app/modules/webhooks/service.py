import hashlib
import hmac
import ipaddress
import json
import logging
import secrets
import socket
import uuid
from datetime import timedelta
from urllib.parse import urlsplit

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import DeliveryStatus
from app.core.config import get_settings
from app.core.database import session_scope
from app.core.exceptions import NotFound, ValidationFailed
from app.core.principal import Principal
from app.core.time import utcnow
from app.modules.audit import service as audit
from app.modules.kyc.models import KycCase
from app.modules.webhooks.models import WebhookDelivery, WebhookEndpoint
from app.modules.webhooks.schemas import WebhookCreate

logger = logging.getLogger("app.webhooks")
SIGNATURE_HEADER = "X-IZILens-Signature"
_BACKOFF_SECONDS = 30


def _resolve(host: str) -> list[str]:
    return [info[4][0] for info in socket.getaddrinfo(host, None)]


def validate_target_url(url: str) -> None:
    """Refuse les cibles internes (SSRF) : seules des adresses publiques en HTTPS sont acceptées."""
    allow_http = get_settings().webhook_allow_http
    parts = urlsplit(url)
    if parts.scheme not in (("https", "http") if allow_http else ("https",)) or not parts.hostname:
        raise ValidationFailed("L'URL doit être en HTTPS", code="INVALID_WEBHOOK_URL")
    if parts.username or parts.password:
        raise ValidationFailed("Identifiants dans l'URL interdits", code="INVALID_WEBHOOK_URL")
    try:
        addresses = _resolve(parts.hostname)
    except OSError as exc:
        raise ValidationFailed("Nom d'hôte introuvable", code="INVALID_WEBHOOK_URL") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not allow_http and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast):
            raise ValidationFailed("Adresse de destination non autorisée", code="INVALID_WEBHOOK_URL")


def create_endpoint(db: Session, principal: Principal, payload: WebhookCreate) -> tuple[WebhookEndpoint, str]:
    validate_target_url(payload.url)
    secret = "whsec_" + secrets.token_urlsafe(32)
    endpoint = WebhookEndpoint(
        organization_id=principal.organization_id,
        url=payload.url,
        description=payload.description,
        secret={"secret": secret},
        events=payload.events,
    )
    db.add(endpoint)
    db.flush()
    audit.record(db, action="webhook.created", resource_type="webhook", resource_id=endpoint.id, principal=principal)
    db.commit()
    return endpoint, secret


def list_endpoints(db: Session, principal: Principal) -> list[WebhookEndpoint]:
    return list(db.scalars(select(WebhookEndpoint).where(WebhookEndpoint.organization_id == principal.organization_id)).all())


def _own_endpoint(db: Session, principal: Principal, endpoint_id: uuid.UUID) -> WebhookEndpoint:
    endpoint = db.get(WebhookEndpoint, endpoint_id)
    if endpoint is None or endpoint.organization_id != principal.organization_id:
        raise NotFound("Webhook introuvable", code="WEBHOOK_NOT_FOUND")
    return endpoint


def deactivate_endpoint(db: Session, principal: Principal, endpoint_id: uuid.UUID) -> WebhookEndpoint:
    endpoint = _own_endpoint(db, principal, endpoint_id)
    endpoint.is_active = False
    audit.record(db, action="webhook.deactivated", resource_type="webhook", resource_id=endpoint.id, principal=principal)
    db.commit()
    return endpoint


def list_deliveries(db: Session, principal: Principal, endpoint_id: uuid.UUID, limit: int = 50) -> list[WebhookDelivery]:
    endpoint = _own_endpoint(db, principal, endpoint_id)
    return list(
        db.scalars(
            select(WebhookDelivery)
            .where(WebhookDelivery.endpoint_id == endpoint.id)
            .order_by(WebhookDelivery.created_at.desc())
            .limit(limit)
        ).all()
    )


def enqueue(db: Session, case: KycCase, event_type: str, extra: dict | None = None) -> None:
    """Prépare les livraisons dans la transaction du changement : aucun événement perdu ni fantôme."""
    endpoints = db.scalars(
        select(WebhookEndpoint).where(
            WebhookEndpoint.organization_id == case.organization_id, WebhookEndpoint.is_active.is_(True)
        )
    ).all()
    for endpoint in endpoints:
        if "*" not in endpoint.events and event_type not in endpoint.events:
            continue
        payload = {
            "event": event_type,
            "case_id": str(case.id),
            "reference": case.reference,
            "status": case.status.value,
            "status_reason": case.status_reason,
            "occurred_at": utcnow().isoformat(),
            **(extra or {}),
        }
        db.add(
            WebhookDelivery(
                endpoint_id=endpoint.id,
                organization_id=case.organization_id,
                case_id=case.id,
                event_type=event_type,
                payload=payload,
            )
        )


def sign(secret: str, timestamp: int, body: bytes) -> str:
    digest = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def dispatch_pending(*, client: httpx.Client | None = None, limit: int = 50) -> dict[str, int]:
    """Envoie les livraisons dues ; appelé après chaque changement et par la tâche de maintenance."""
    settings = get_settings()
    sent = failed = 0
    own_client = client is None
    http = client or httpx.Client(timeout=settings.webhook_timeout_seconds, follow_redirects=False)
    try:
        with session_scope() as db:
            due = db.scalars(
                select(WebhookDelivery)
                .where(WebhookDelivery.status == DeliveryStatus.PENDING.value, WebhookDelivery.next_attempt_at <= utcnow())
                .order_by(WebhookDelivery.created_at)
                .limit(limit)
            ).all()
            for delivery in due:
                endpoint = db.get(WebhookEndpoint, delivery.endpoint_id)
                delivery.attempts += 1
                try:
                    if endpoint is None or not endpoint.is_active:
                        raise RuntimeError("endpoint inactif")
                    validate_target_url(endpoint.url)
                    body = json.dumps(delivery.payload, separators=(",", ":"), ensure_ascii=False).encode()
                    timestamp = int(utcnow().timestamp())
                    response = http.post(
                        endpoint.url,
                        content=body,
                        headers={
                            "Content-Type": "application/json",
                            SIGNATURE_HEADER: sign(endpoint.secret["secret"], timestamp, body),
                            "User-Agent": "IZILens-Webhooks/1",
                        },
                    )
                    delivery.last_status_code = response.status_code
                    if 200 <= response.status_code < 300:
                        delivery.status = DeliveryStatus.DELIVERED.value
                        delivery.delivered_at = utcnow()
                        delivery.last_error = None
                        sent += 1
                        continue
                    delivery.last_error = f"HTTP {response.status_code}"
                except Exception as exc:  # noqa: BLE001
                    delivery.last_error = type(exc).__name__[:100]
                    logger.warning(
                        "Échec de livraison webhook", extra={"delivery_id": str(delivery.id), "error": delivery.last_error}
                    )
                if delivery.attempts >= settings.webhook_max_attempts:
                    delivery.status = DeliveryStatus.FAILED.value
                    failed += 1
                else:
                    delivery.next_attempt_at = utcnow() + timedelta(seconds=_BACKOFF_SECONDS * 2 ** (delivery.attempts - 1))
            db.commit()
    finally:
        if own_client:
            http.close()
    return {"delivered": sent, "failed": failed}


def retry_delivery(db: Session, delivery_id: uuid.UUID) -> WebhookDelivery:
    delivery = db.get(WebhookDelivery, delivery_id)
    if delivery is None:
        raise NotFound("Livraison introuvable", code="DELIVERY_NOT_FOUND")
    delivery.status = DeliveryStatus.PENDING.value
    delivery.next_attempt_at = utcnow()
    db.commit()
    return delivery
