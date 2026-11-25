import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.core.database import get_db
from app.core.dependencies import require_access
from app.core.principal import Principal
from app.modules.api_keys import service
from app.modules.api_keys.schemas import ApiKeyCreate, ApiKeyCreated, ApiKeyRead

router = APIRouter(prefix="/api-keys", tags=["Clés API"])
admin_only = require_access(UserRole.ADMIN)


@router.post("", response_model=ApiKeyCreated, status_code=201, summary="Générer une clé API (affichée une seule fois)")
def create_api_key(payload: ApiKeyCreate, principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    api_key, raw_key = service.create_api_key(db, principal, payload)
    return ApiKeyCreated.model_validate({**ApiKeyRead.model_validate(api_key).model_dump(), "key": raw_key})


@router.get("", response_model=list[ApiKeyRead], summary="Lister les clés de l'organisation")
def list_api_keys(principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    return service.list_api_keys(db, principal)


@router.delete("/{key_id}", response_model=ApiKeyRead, summary="Révoquer une clé API")
def revoke_api_key(key_id: uuid.UUID, principal: Principal = Depends(admin_only), db: Session = Depends(get_db)):
    return service.revoke_api_key(db, principal, key_id)
