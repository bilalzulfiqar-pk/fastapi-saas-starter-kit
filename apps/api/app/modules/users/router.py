from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.auth.service import require_active_user
from app.modules.users.models import User
from app.modules.users.schemas import ChangePasswordInput, UserUpdateInput
from app.modules.users.service import change_password, update_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_profile(current_user: User = Depends(require_active_user)):
    return {"data": {"user": AuthenticatedUser.model_validate(current_user)}}


@router.patch("/me")
def patch_profile(
    payload: UserUpdateInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    user = update_profile(session, current_user, payload)
    return {"data": {"user": AuthenticatedUser.model_validate(user)}, "message": "Profile updated"}


@router.post("/me/change-password")
def post_change_password(
    payload: ChangePasswordInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    change_password(session, current_user, payload)
    return {"data": {"success": True}, "message": "Password updated"}

