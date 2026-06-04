from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_session
from app.modules.auth.service import require_active_user
from app.modules.invites.schemas import InviteCreateInput, InviteResponse
from app.modules.invites.service import accept_invite, cancel_invite, create_invite, get_invite_by_token, list_invites
from app.modules.users.models import User

router = APIRouter(tags=["invites"])


@router.post("/workspaces/{workspace_id}/invites")
async def post_invite(
    workspace_id: UUID,
    payload: InviteCreateInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    invite, invite_url = await create_invite(session, workspace_id, current_user, payload)
    response = InviteResponse.model_validate({**invite.model_dump(), "invite_url": invite_url})
    return {"data": {"invite": response}}


@router.get("/workspaces/{workspace_id}/invites")
def get_workspace_invites(
    workspace_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    invites = [InviteResponse.model_validate(invite) for invite in list_invites(session, workspace_id, current_user)]
    return {"data": {"invites": invites}}


@router.delete("/workspaces/{workspace_id}/invites/{invite_id}")
def delete_invite(
    workspace_id: UUID,
    invite_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    cancel_invite(session, workspace_id, invite_id, current_user)
    return {"data": {"success": True}, "message": "Invite revoked"}


@router.get("/invites/{token}")
def get_invite(
    token: str,
    session: Session = Depends(get_session),
):
    invite = get_invite_by_token(session, token)
    return {"data": {"invite": InviteResponse.model_validate(invite)}}


@router.post("/invites/{token}/accept")
async def post_accept_invite(
    token: str,
    request: Request,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    await enforce_rate_limit("invite_accept", request, limit=5, window_seconds=3600, identifier=current_user.email)
    invite = accept_invite(session, token, current_user)
    return {"data": {"invite": InviteResponse.model_validate(invite)}, "message": "Invite accepted"}
