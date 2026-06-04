from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.errors import AppError
from app.core.security import utcnow
from app.modules.billing.models import Plan, Subscription
from app.modules.users.models import User
from app.modules.workspaces.models import Workspace, WorkspaceMember
from app.modules.workspaces.schemas import MemberRoleUpdateInput, WorkspaceCreateInput, WorkspaceUpdateInput

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
ALLOWED_ROLES = {"owner", "admin", "member"}


def _slugify(value: str) -> str:
    slug = SLUG_PATTERN.sub("-", value.strip().lower()).strip("-")
    return slug or "workspace"


def _ensure_unique_slug(session: Session, base_slug: str, ignore_workspace_id: UUID | None = None) -> str:
    slug = _slugify(base_slug)
    candidate = slug
    counter = 2
    while True:
        statement = select(Workspace).where(Workspace.slug == candidate)
        match = session.exec(statement).first()
        if not match or match.id == ignore_workspace_id:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


def _workspace_member(session: Session, workspace_id: UUID, user_id: UUID) -> WorkspaceMember | None:
    return session.exec(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    ).first()


def require_workspace_member(session: Session, workspace_id: UUID, user_id: UUID) -> tuple[Workspace, WorkspaceMember]:
    workspace = session.get(Workspace, workspace_id)
    if not workspace:
        raise AppError(code="workspace_not_found", message="Workspace not found", status_code=404)
    member = _workspace_member(session, workspace_id, user_id)
    if not member:
        raise AppError(code="workspace_forbidden", message="You do not have access to this workspace", status_code=403)
    return workspace, member


def require_workspace_admin(session: Session, workspace_id: UUID, user_id: UUID) -> tuple[Workspace, WorkspaceMember]:
    workspace, member = require_workspace_member(session, workspace_id, user_id)
    if member.role not in {"owner", "admin"}:
        raise AppError(code="workspace_forbidden", message="You do not have permission for this action", status_code=403)
    return workspace, member


def create_workspace(session: Session, user: User, payload: WorkspaceCreateInput) -> Workspace:
    slug = _ensure_unique_slug(session, payload.slug or payload.name)
    workspace = Workspace(name=payload.name.strip(), slug=slug, owner_id=user.id)
    session.add(workspace)
    session.flush()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    session.add(member)

    free_plan = session.exec(select(Plan).where(Plan.slug == "free")).first()
    if not free_plan:
        raise AppError(code="billing_seed_missing", message="Default billing plan is missing", status_code=500)
    subscription = Subscription(workspace_id=workspace.id, plan_id=free_plan.id, status="active")
    session.add(subscription)

    session.commit()
    session.refresh(workspace)
    return workspace


def list_workspaces_for_user(session: Session, user: User) -> list[dict[str, Any]]:
    memberships = session.exec(select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)).all()
    items: list[dict[str, Any]] = []
    for membership in memberships:
        workspace = session.get(Workspace, membership.workspace_id)
        if workspace:
            items.append(
                {
                    "id": workspace.id,
                    "name": workspace.name,
                    "slug": workspace.slug,
                    "owner_id": workspace.owner_id,
                    "logo_url": workspace.logo_url,
                    "created_at": workspace.created_at,
                    "updated_at": workspace.updated_at,
                    "role": membership.role,
                }
            )
    return items


def update_workspace(session: Session, workspace: Workspace, payload: WorkspaceUpdateInput) -> Workspace:
    if payload.name is not None:
        workspace.name = payload.name.strip()
    if payload.logo_url is not None:
        workspace.logo_url = payload.logo_url.strip() or None
    workspace.updated_at = utcnow()
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


def list_members(session: Session, workspace_id: UUID) -> list[dict[str, Any]]:
    members = session.exec(select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)).all()
    items: list[dict[str, Any]] = []
    for member in members:
        user = session.get(User, member.user_id)
        if user:
            items.append(
                {
                    "id": member.id,
                    "user_id": member.user_id,
                    "workspace_id": member.workspace_id,
                    "role": member.role,
                    "joined_at": member.joined_at,
                    "email": user.email,
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                }
            )
    return items


def _owner_count(session: Session, workspace_id: UUID) -> int:
    owners = session.exec(
        select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.role == "owner")
    ).all()
    return len(owners)


def update_member_role(
    session: Session,
    workspace_id: UUID,
    member_id: UUID,
    payload: MemberRoleUpdateInput,
) -> WorkspaceMember:
    if payload.role not in ALLOWED_ROLES:
        raise AppError(code="invalid_role", message="Role is invalid", status_code=400)

    member = session.get(WorkspaceMember, member_id)
    if not member or member.workspace_id != workspace_id:
        raise AppError(code="member_not_found", message="Member not found", status_code=404)

    if member.role == "owner" and payload.role != "owner" and _owner_count(session, workspace_id) <= 1:
        raise AppError(code="last_owner_required", message="A workspace must always have at least one owner", status_code=400)

    member.role = payload.role
    member.updated_at = utcnow()
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def remove_member(session: Session, workspace_id: UUID, member_id: UUID) -> None:
    member = session.get(WorkspaceMember, member_id)
    if not member or member.workspace_id != workspace_id:
        raise AppError(code="member_not_found", message="Member not found", status_code=404)
    if member.role == "owner" and _owner_count(session, workspace_id) <= 1:
        raise AppError(code="last_owner_required", message="A workspace must always have at least one owner", status_code=400)
    session.delete(member)
    session.commit()

