from __future__ import annotations

import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.csrf import OriginValidationMiddleware
from app.core.errors import AppError, error_payload
from app.core.logging import configure_logging
from app.db.session import engine

settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.trusted_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    app.add_middleware(OriginValidationMiddleware)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = perf_counter()
        response = await call_next(request)
        duration_ms = (perf_counter() - start) * 1000
        logger.info("%s %s -> %s %.2fms", request.method, request.url.path, response.status_code, duration_ms)
        return response

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message, exc.details))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload("validation_error", "Validation failed", {"issues": exc.errors()}),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error: %s", exc)
        return JSONResponse(status_code=500, content=error_payload("internal_server_error", "Something went wrong"))

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readiness")
    async def readiness() -> dict[str, str]:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return {"status": "ready"}

    app.include_router(api_router)
    return app


app = create_application()
