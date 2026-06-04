from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.errors import AppError, error_payload
from app.core.rate_limit import enforce_rate_limit
from app.core.security import clear_auth_cookies
from app.db.session import get_session
from app.modules.auth.schemas import AuthenticatedUser, LoginInput, RegisterInput
from app.modules.auth.service import (
    build_authenticated_user,
    login_user,
    logout_user,
    register_and_login,
    require_active_user,
    rotate_refresh_token,
)
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    payload: RegisterInput,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    await enforce_rate_limit("register", request, limit=5, window_seconds=3600, identifier=payload.email)
    user = register_and_login(session, payload, request, response)
    return {"data": {"user": AuthenticatedUser.model_validate(user)}}


@router.post("/login")
async def login(
    payload: LoginInput,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    await enforce_rate_limit("login", request, limit=5, window_seconds=60, identifier=payload.email)
    user = login_user(session, payload, request, response)
    return {"data": {"user": AuthenticatedUser.model_validate(user)}}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    logout_user(session, request, response)
    return {"data": {"success": True}, "message": "Logged out"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    await enforce_rate_limit("refresh", request, limit=10, window_seconds=60, identifier="refresh")
    try:
        user = rotate_refresh_token(session, request, response)
    except AppError as exc:
        if exc.status_code == 401:
            error_response = JSONResponse(
                status_code=exc.status_code,
                content=error_payload(exc.code, exc.message, exc.details),
            )
            clear_auth_cookies(error_response)
            return error_response
        raise
    return {"data": {"user": build_authenticated_user(user)}}


@router.get("/me")
def me(current_user: User = Depends(require_active_user)):
    return {"data": {"user": build_authenticated_user(current_user)}}
