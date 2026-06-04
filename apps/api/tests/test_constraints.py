from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.security import hash_password, hash_secret, utcnow
from app.modules.billing.models import Plan, Subscription
from app.modules.invites.models import WorkspaceInvite
from app.modules.users.models import User
from app.modules.workspaces.models import Workspace, WorkspaceMember


def create_user(session: Session, email: str, name: str = "User") -> User:
    user = User(email=email, name=name, password_hash=hash_password("supersecret"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_workspace(session: Session, owner: User, name: str = "Acme", slug: str = "acme") -> Workspace:
    workspace = Workspace(name=name, slug=slug, owner_id=owner.id)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


def test_users_email_unique_constraint(session: Session):
    create_user(session, "duplicate@example.com", name="First")
    session.add(User(email="duplicate@example.com", name="Second", password_hash=hash_password("supersecret")))

    with pytest.raises(IntegrityError):
        session.commit()


def test_workspaces_slug_unique_constraint(session: Session):
    owner = create_user(session, "workspace-owner@example.com", name="Owner")
    create_workspace(session, owner, name="Acme", slug="shared-slug")
    session.add(Workspace(name="Beta", slug="shared-slug", owner_id=owner.id))

    with pytest.raises(IntegrityError):
        session.commit()


def test_workspace_members_unique_constraint(session: Session):
    owner = create_user(session, "member-owner@example.com", name="Owner")
    teammate = create_user(session, "member-user@example.com", name="Teammate")
    workspace = create_workspace(session, owner, slug="members")

    session.add(WorkspaceMember(workspace_id=workspace.id, user_id=teammate.id, role="member"))
    session.commit()
    session.add(WorkspaceMember(workspace_id=workspace.id, user_id=teammate.id, role="admin"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_workspace_invites_pending_partial_unique_constraint(session: Session):
    owner = create_user(session, "invite-owner@example.com", name="Owner")
    workspace = create_workspace(session, owner, slug="invite-constraints")

    revoked_invite = WorkspaceInvite(
        workspace_id=workspace.id,
        email="teammate@example.com",
        role="member",
        token_hash=hash_secret("revoked-token"),
        invited_by_user_id=owner.id,
        status="revoked",
        expires_at=utcnow() + timedelta(days=7),
    )
    pending_invite = WorkspaceInvite(
        workspace_id=workspace.id,
        email="teammate@example.com",
        role="member",
        token_hash=hash_secret("pending-token"),
        invited_by_user_id=owner.id,
        status="pending",
        expires_at=utcnow() + timedelta(days=7),
    )
    session.add(revoked_invite)
    session.add(pending_invite)
    session.commit()

    session.add(
        WorkspaceInvite(
            workspace_id=workspace.id,
            email="teammate@example.com",
            role="admin",
            token_hash=hash_secret("duplicate-pending-token"),
            invited_by_user_id=owner.id,
            status="pending",
            expires_at=utcnow() + timedelta(days=7),
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_subscriptions_workspace_unique_constraint(session: Session):
    owner = create_user(session, "subscription-owner@example.com", name="Owner")
    workspace = create_workspace(session, owner, slug="billing")
    free_plan = session.exec(select(Plan).where(Plan.slug == "free")).first()
    pro_plan = session.exec(select(Plan).where(Plan.slug == "pro")).first()
    assert free_plan is not None
    assert pro_plan is not None

    session.add(Subscription(workspace_id=workspace.id, plan_id=free_plan.id, status="active"))
    session.commit()
    session.add(Subscription(workspace_id=workspace.id, plan_id=pro_plan.id, status="active"))

    with pytest.raises(IntegrityError):
        session.commit()
