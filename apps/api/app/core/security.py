from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request, Response

from app.core.config import get_settings
from app.core.errors import AppError

password_hasher = PasswordHasher()


def utcnow() -> datetime:
    return datetime.now(UTC)


def coerce_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    now = utcnow()
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AppError(code="invalid_access_token", message="Authentication required", status_code=401) from exc

    if payload.get("type") != "access":
        raise AppError(code="invalid_access_token", message="Authentication required", status_code=401)
    return payload


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def refresh_token_expiry() -> datetime:
    settings = get_settings()
    return utcnow() + timedelta(days=settings.refresh_token_expire_days)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    settings = get_settings()
    common_kwargs = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": settings.cookie_samesite,
        "domain": settings.cookie_domain or None,
    }
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
        **common_kwargs,
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
        **common_kwargs,
    )
    response.set_cookie(
        key=settings.session_cookie_name,
        value="1",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
        **common_kwargs,
    )


def clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(settings.access_cookie_name, path="/", domain=settings.cookie_domain or None)
    response.delete_cookie(settings.refresh_cookie_name, path="/api/v1/auth", domain=settings.cookie_domain or None)
    response.delete_cookie(settings.session_cookie_name, path="/", domain=settings.cookie_domain or None)


def get_access_cookie(request: Request) -> str:
    settings = get_settings()
    token = request.cookies.get(settings.access_cookie_name)
    if not token:
        raise AppError(code="authentication_required", message="Authentication required", status_code=401)
    return token


def get_refresh_cookie(request: Request) -> str:
    settings = get_settings()
    token = request.cookies.get(settings.refresh_cookie_name)
    if not token:
        raise AppError(code="refresh_token_required", message="Refresh token required", status_code=401)
    return token
