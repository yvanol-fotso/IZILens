import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.common.constants import REQUEST_ID_HEADER
from app.core.config import get_settings
from app.core.context import request_id_ctx

logger = logging.getLogger("app.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Identifiant de requête, plafond de taille, en-têtes de sécurité et journal d'accès."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = incoming if 8 <= len(incoming) <= 64 and incoming.isascii() and incoming.isprintable() else uuid.uuid4().hex
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        try:
            declared = request.headers.get("content-length")
            if declared and declared.isdigit() and int(declared) > settings.max_request_mb * 1024 * 1024:
                response: Response = JSONResponse(
                    {"error": {"code": "PAYLOAD_TOO_LARGE", "message": "Requête trop volumineuse", "request_id": request_id}},
                    status_code=413,
                )
            else:
                response = await call_next(request)
            self._harden(response, settings.is_production, request_id)
            logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                },
            )
            return response
        finally:
            request_id_ctx.reset(token)

    @staticmethod
    def _harden(response: Response, production: bool, request_id: str) -> None:
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers.setdefault("Cache-Control", "no-store")
        if production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
