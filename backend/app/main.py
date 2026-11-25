import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import models_registry  # noqa: F401  # enregistre tous les modèles
from app.api.v1.router import api_router
from app.common.constants import API_PREFIX, REQUEST_ID_HEADER
from app.core.config import get_settings
from app.core.database import get_engine
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestContextMiddleware
from app.infrastructure.logging.setup import configure_logging

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.ocr_preload:
        from app.shared.ocr.engine import PaddleOcrEngine
        from app.shared.ocr.engine import get_engine as get_ocr

        engine = get_ocr()
        if isinstance(engine, PaddleOcrEngine):
            threading.Thread(target=engine.load, name="ocr-preload", daemon=True).start()
    logger.info("Application démarrée", extra={"environment": settings.environment})
    yield
    get_engine().dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Plateforme de vérification d'identité (KYC) : dossiers, OCR, revue humaine, audit.",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
        max_age=600,
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=API_PREFIX)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {"name": settings.app_name, "version": settings.app_version}

    @app.get("/health", tags=["Santé"], summary="Liveness : le processus répond")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Santé"], summary="Readiness : la base de données répond")
    def ready() -> JSONResponse:
        try:
            with get_engine().connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            logger.exception("Base de données injoignable")
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready"})

    return app


app = create_app()
