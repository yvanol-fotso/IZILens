from fastapi import APIRouter

from app.modules.api_keys.routes import router as api_keys_router
from app.modules.audit.routes import router as audit_router
from app.modules.auth.routes import router as auth_router
from app.modules.kyc.routes import router as kyc_router
from app.modules.organizations.routes import router as organizations_router
from app.modules.users.routes import router as users_router

api_router = APIRouter()
for module_router in (
    auth_router,
    organizations_router,
    users_router,
    api_keys_router,
    kyc_router,
    audit_router,
):
    api_router.include_router(module_router)
