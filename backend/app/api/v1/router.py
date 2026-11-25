from fastapi import APIRouter

from app.modules.api_keys.routes import router as api_keys_router
from app.modules.audit.routes import router as audit_router
from app.modules.auth.routes import router as auth_router
from app.modules.backoffice.routes import router as backoffice_router
from app.modules.billing.routes import admin_router as billing_admin_router
from app.modules.billing.routes import router as billing_router
from app.modules.cms.routes import admin_router as cms_admin_router
from app.modules.cms.routes import public_router as cms_public_router
from app.modules.developers.routes import admin_router as developers_admin_router
from app.modules.developers.routes import router as developers_router
from app.modules.kyc.routes import router as kyc_router
from app.modules.kyc.session_routes import router as session_router
from app.modules.organizations.routes import router as organizations_router
from app.modules.public_requests.routes import admin_router as requests_admin_router
from app.modules.public_requests.routes import public_router as requests_public_router
from app.modules.security.routes import router as security_router
from app.modules.users.routes import router as users_router
from app.modules.webhooks.routes import router as webhooks_router

api_router = APIRouter()
for module_router in (
    auth_router,
    organizations_router,
    users_router,
    api_keys_router,
    session_router,
    kyc_router,
    webhooks_router,
    backoffice_router,
    billing_router,
    billing_admin_router,
    cms_public_router,
    cms_admin_router,
    developers_router,
    developers_admin_router,
    requests_public_router,
    requests_admin_router,
    security_router,
    audit_router,
):
    api_router.include_router(module_router)


@api_router.get("/health", tags=["Santé"], summary="Liveness (préfixe API)")
def health() -> dict[str, str]:
    return {"status": "ok"}
