from fastapi import APIRouter

from app.api.v1.endpoints import router as health_router
from app.modules.kyc.routes import router as kyc_router
from app.modules.kyb.routes import router as kyb_router
from app.modules.biometrics.liveness.routes import router as liveness_router
from app.modules.biometrics.face_match.routes import router as face_match_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(kyc_router, prefix="/kyc", tags=["kyc"])
api_router.include_router(kyb_router, prefix="/kyb", tags=["kyb"])
api_router.include_router(liveness_router, prefix="/biometrics/liveness", tags=["liveness"])
api_router.include_router(face_match_router, prefix="/biometrics/face-match", tags=["face-match"])
