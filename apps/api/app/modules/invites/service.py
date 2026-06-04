from __future__ import annotations

import secrets
from datetime import timedelta
from uuid import UUID

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.email.base import EmailProvider
from app.core.email.console import ConsoleEmailProvider
from app.core.email.schemas import EmailMessage
from app.core.errors import AppError
from app.core.security import coerce_utc, hash_secret, utcnow
from app.modules.invites.models import WorkspaceInvite
from app.modules.invites.schemas import InviteCreateInput
from app.modules.users.models import User
from app.modules.workspaces.models import WorkspaceMember
from app.modules.workspaces.service import require_workspace_admin, require_workspace_member

email_provider: EmailProvider = ConsoleEmailProvider()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _invite_url(raw_token: str) -> str:
    return f"{get_settings().app_url}/login?invite={raw_token}"


def _ensure_owner_invite_management_allowed(actor_role: str, invite_role: str) -> None:
    if invite_role == "owner" and actor_role != "owner":
        raise AppError(
            code="owner_role_forbidden",
            message="Only workspace owners can grant, revoke, or invite owner roles",
            status_code=403,
        )


async def create_invite(session: Session, workspace_id: UUID, actor: User, payload: InviteCreateInput) -> tuple[WorkspaceInvite, str]:
    workspace, actor_member = require_workspace_admin(session, workspace_id, actor.id)
    _ensure_owner_invite_management_allowed(actor_member.role, payload.role)
    email = _normalize_email(payload.email)

    existing_pending = session.exec(
        select(WorkspaceInvite).where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.email == email,
            WorkspaceInvite.status == "pending",
        )
    ).first()
    if existing_pending:
        raise AppError(code="invite_already_exists", message="A pending invite already exists for this email", status_code=409)

    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        existing_member = session.exec(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == existing_user.id,
            )
        ).first()
        if existing_member:
            raise AppError(code="member_already_exists", message="This user is already a workspace member", status_code=409)

    raw_token = secrets.token_urlsafe(32)
    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        email=email,
        role=payload.role,
        token_hash=hash_secret(raw_token),
        invited_by_user_id=actor.id,
        expires_at=utcnow() + timedelta(days=7),
    )
    session.add(invite)
    session.commit()
    session.refresh(invite)

    invite_url = _invite_url(raw_token)
    await email_provider.send(
        EmailMessage(
            to=email,
            subject=f"You were invited to join {workspace.name}",
            text_body=f"Join {workspace.name} using this invite link: {invite_url}",
        )
    )
    return invite, invite_url


def list_invites(session: Session, workspace_id: UUID, actor: User) -> list[WorkspaceInvite]:
    require_workspace_admin(session, workspace_id, actor.id)
    return session.exec(
        select(WorkspaceInvite).where(WorkspaceInvite.workspace_id == workspace_id).order_by(WorkspaceInvite.created_at.desc())
    ).all()


def get_invite_by_token(session: Session, raw_token: str) -> WorkspaceInvite:
    invite = session.exec(select(WorkspaceInvite).where(WorkspaceInvite.token_hash == hash_secret(raw_token))).first()
    if not invite or invite.status != "pending":
        raise AppError(code="invite_not_found", message="Invite not found", status_code=404)
    expires_at = coerce_utc(invite.expires_at)
    if expires_at and expires_at <= utcnow():
        invite.status = "expired"
        invite.updated_at = utcnow()
        session.add(invite)
        session.commit()
        raise AppError(code="invite_expired", message="Invite has expired", status_code=410)
    return invite


def cancel_invite(session: Session, workspace_id: UUID, invite_id: UUID, actor: User) -> None:
    _, actor_member = require_workspace_admin(session, workspace_id, actor.id)
    invite = session.get(WorkspaceInvite, invite_id)
    if not invite or invite.workspace_id != workspace_id:
        raise AppError(code="invite_not_found", message="Invite not found", status_code=404)
    if invite.status != "pending":
        raise AppError(code="invite_not_pending", message="Only pending invites can be revoked", status_code=409)
    _ensure_owner_invite_management_allowed(actor_member.role, invite.role)
    invite.status = "revoked"
    invite.updated_at = utcnow()
    session.add(invite)
    session.commit()


def accept_invite(session: Session, raw_token: str, user: User) -> WorkspaceInvite:
    invite = get_invite_by_token(session, raw_token)
    if invite.email != _normalize_email(user.email):
        raise AppError(code="invite_email_mismatch", message="Invite email does not match your account", status_code=403)

    existing_member = session.exec(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invite.workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    ).first()
    if existing_member:
        raise AppError(code="member_already_exists", message="You already belong to this workspace", status_code=409)

    member = WorkspaceMember(workspace_id=invite.workspace_id, user_id=user.id, role=invite.role)
    invite.status = "accepted"
    invite.accepted_at = utcnow()
    invite.updated_at = utcnow()
    session.add(member)
    session.add(invite)
    session.commit()
    session.refresh(invite)
    return invite
