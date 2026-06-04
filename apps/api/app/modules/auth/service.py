from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Request, Response
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    clear_auth_cookies,
    coerce_utc,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    get_access_cookie,
    get_refresh_cookie,
    hash_password,
    hash_secret,
    refresh_token_expiry,
    set_auth_cookies,
    utcnow,
    verify_password,
)
from app.db.session import get_session
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import AuthenticatedUser, LoginInput, RegisterInput
from app.modules.users.models import User


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _issue_tokens(session: Session, user: User, request: Request, response: Response) -> None:
    raw_refresh = generate_refresh_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_secret(raw_refresh),
        expires_at=refresh_token_expiry(),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    session.add(refresh_row)
    session.commit()
    access_token = create_access_token(str(user.id))
    set_auth_cookies(response, access_token=access_token, refresh_token=raw_refresh)


def register_user(session: Session, payload: RegisterInput) -> User:
    email = _normalize_email(payload.email)
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise AppError(code="email_already_registered", message="An account with this email already exists", status_code=409)

    user = User(email=email, name=payload.name.strip(), password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, payload: LoginInput) -> User:
    email = _normalize_email(payload.email)
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(code="invalid_credentials", message="Invalid email or password", status_code=401)
    if not user.is_active:
        raise AppError(code="user_inactive", message="Your account is inactive", status_code=403)
    user.last_login_at = utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def build_authenticated_user(user: User) -> AuthenticatedUser:
    return AuthenticatedUser.model_validate(user)


def login_user(session: Session, payload: LoginInput, request: Request, response: Response) -> User:
    user = authenticate_user(session, payload)
    _issue_tokens(session, user, request, response)
    return user


def register_and_login(session: Session, payload: RegisterInput, request: Request, response: Response) -> User:
    user = register_user(session, payload)
    _issue_tokens(session, user, request, response)
    return user


def revoke_refresh_token(session: Session, raw_refresh_token: str | None) -> None:
    if not raw_refresh_token:
        return
    token_hash = hash_secret(raw_refresh_token)
    refresh_row = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    if not refresh_row or refresh_row.revoked_at is not None:
        return
    refresh_row.revoked_at = utcnow()
    refresh_row.updated_at = utcnow()
    session.add(refresh_row)
    session.commit()


def logout_user(session: Session, request: Request, response: Response) -> None:
    settings = get_settings()
    revoke_refresh_token(session, request.cookies.get(settings.refresh_cookie_name))
    clear_auth_cookies(response)


def rotate_refresh_token(session: Session, request: Request, response: Response) -> User:
    raw_refresh = get_refresh_cookie(request)
    refresh_row = session.exec(select(RefreshToken).where(RefreshToken.token_hash == hash_secret(raw_refresh))).first()
    expires_at = coerce_utc(refresh_row.expires_at) if refresh_row else None
    if not refresh_row or refresh_row.revoked_at is not None or not expires_at or expires_at <= utcnow():
        raise AppError(code="invalid_refresh_token", message="Refresh token is invalid", status_code=401)

    user = session.get(User, refresh_row.user_id)
    if not user or not user.is_active:
        raise AppError(code="authentication_required", message="Authentication required", status_code=401)

    refresh_row.revoked_at = utcnow()
    refresh_row.updated_at = utcnow()
    session.add(refresh_row)
    session.commit()

    _issue_tokens(session, user, request, response)
    return user


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    access_token = get_access_cookie(request)
    payload = decode_access_token(access_token)
    user_id = payload.get("sub")
    user = session.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise AppError(code="authentication_required", message="Authentication required", status_code=401)
    return user


def require_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
