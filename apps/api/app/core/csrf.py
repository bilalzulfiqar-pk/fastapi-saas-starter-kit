from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.errors import error_payload

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PATHS = {"/health", "/readiness"}


class OriginValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method.upper() in SAFE_METHODS or request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        origin = request.headers.get("origin")
        settings = get_settings()
        if origin is None or origin not in settings.trusted_origins:
            return JSONResponse(
                status_code=403,
                content=error_payload("invalid_origin", "Request origin is not allowed"),
            )

        return await call_next(request)

