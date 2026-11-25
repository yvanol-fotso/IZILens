import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.webhooks import service
from app.modules.webhooks.schemas import DeliveryRead, WebhookCreate, WebhookCreated, WebhookRead

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
admin_only = require_access(UserRole.ADMIN, module="kyc")


@router.post(
    "", response_model=WebhookCreated, status_code=201, summary="Déclarer un point de notification (secret affiché une fois)"
)
def create_webhook(payload: WebhookCreate, principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    endpoint, secret = service.create_endpoint(db, principal, payload)
    return WebhookCreated.model_validate({**WebhookRead.model_validate(endpoint).model_dump(), "secret": secret})


@router.get("", response_model=list[WebhookRead], summary="Lister les points de notification")
def list_webhooks(principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    return service.list_endpoints(db, principal)


@router.delete("/{webhook_id}", response_model=WebhookRead, summary="Désactiver un point de notification")
def deactivate_webhook(webhook_id: uuid.UUID, principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    return service.deactivate_endpoint(db, principal, webhook_id)


@router.get("/{webhook_id}/deliveries", response_model=list[DeliveryRead], summary="Historique des livraisons")
def list_deliveries(webhook_id: uuid.UUID, principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    return service.list_deliveries(db, principal, webhook_id)
