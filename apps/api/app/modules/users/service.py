from __future__ import annotations

from sqlmodel import Session

from app.core.errors import AppError
from app.core.security import hash_password, utcnow, verify_password
from app.modules.users.models import User
from app.modules.users.schemas import ChangePasswordInput, UserUpdateInput


def update_profile(session: Session, user: User, payload: UserUpdateInput) -> User:
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url.strip() or None
    user.updated_at = utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def change_password(session: Session, user: User, payload: ChangePasswordInput) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise AppError(code="invalid_password", message="Current password is incorrect", status_code=400)
    if payload.current_password == payload.new_password:
        raise AppError(code="password_reuse", message="New password must be different", status_code=400)
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = utcnow()
    session.add(user)
    session.commit()

