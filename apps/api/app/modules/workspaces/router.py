from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.modules.auth.service import require_active_user
from app.modules.users.models import User
from app.modules.workspaces.schemas import (
    MemberRoleUpdateInput,
    WorkspaceCreateInput,
    WorkspaceMemberResponse,
    WorkspaceSummary,
    WorkspaceUpdateInput,
)
from app.modules.workspaces.service import (
    create_workspace,
    list_members,
    list_workspaces_for_user,
    remove_member,
    require_workspace_admin,
    require_workspace_member,
    update_member_role,
    update_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("")
def post_workspace(
    payload: WorkspaceCreateInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    workspace = create_workspace(session, current_user, payload)
    return {"data": {"workspace": WorkspaceSummary.model_validate(workspace)}}


@router.get("")
def get_workspaces(
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    return {"data": {"workspaces": list_workspaces_for_user(session, current_user)}}


@router.get("/{workspace_id}")
def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    workspace, _ = require_workspace_member(session, workspace_id, current_user.id)
    return {"data": {"workspace": WorkspaceSummary.model_validate(workspace)}}


@router.patch("/{workspace_id}")
def patch_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdateInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    workspace, _ = require_workspace_admin(session, workspace_id, current_user.id)
    updated = update_workspace(session, workspace, payload)
    return {"data": {"workspace": WorkspaceSummary.model_validate(updated)}, "message": "Workspace updated"}


@router.get("/{workspace_id}/members")
def get_workspace_members(
    workspace_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    require_workspace_member(session, workspace_id, current_user.id)
    members = [WorkspaceMemberResponse.model_validate(member) for member in list_members(session, workspace_id)]
    return {"data": {"members": members}}


@router.patch("/{workspace_id}/members/{member_id}")
def patch_workspace_member(
    workspace_id: UUID,
    member_id: UUID,
    payload: MemberRoleUpdateInput,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    _, actor_member = require_workspace_admin(session, workspace_id, current_user.id)
    member = update_member_role(session, workspace_id, actor_member, member_id, payload)
    return {"data": {"member": {"id": member.id, "role": member.role}}, "message": "Member role updated"}


@router.delete("/{workspace_id}/members/{member_id}")
def delete_workspace_member(
    workspace_id: UUID,
    member_id: UUID,
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
):
    _, actor_member = require_workspace_admin(session, workspace_id, current_user.id)
    remove_member(session, workspace_id, actor_member, member_id)
    return {"data": {"success": True}, "message": "Member removed"}
