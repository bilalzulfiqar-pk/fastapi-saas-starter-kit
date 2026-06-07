from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.workspaces.models import WorkspaceMember

from .conftest import auth_headers
from .test_auth import login_user, register_user


def create_workspace(client: TestClient, name: str = "Acme Labs"):
    return client.post("/api/v1/workspaces", headers=auth_headers(), json={"name": name})


def test_workspace_creation_creates_owner_membership_and_subscription(client: TestClient):
    register_user(client)

    workspace = create_workspace(client)
    assert workspace.status_code == 200
    workspace_id = workspace.json()["data"]["workspace"]["id"]

    workspaces = client.get("/api/v1/workspaces")
    assert workspaces.status_code == 200
    assert workspaces.json()["data"]["workspaces"][0]["role"] == "owner"

    members = client.get(f"/api/v1/workspaces/{workspace_id}/members")
    assert members.status_code == 200
    assert members.json()["data"]["members"][0]["role"] == "owner"

    subscription = client.get(f"/api/v1/workspaces/{workspace_id}/subscription")
    assert subscription.status_code == 200
    assert subscription.json()["data"]["subscription"]["status"] == "active"


def test_owner_can_update_member_role_and_remove_member(client: TestClient, session: Session):
    register_user(client)
    workspace = create_workspace(client)
    workspace_id = UUID(workspace.json()["data"]["workspace"]["id"])

    teammate = User(email="teammate@example.com", name="Teammate", password_hash=hash_password("supersecret"))
    session.add(teammate)
    session.commit()
    session.refresh(teammate)

    membership = WorkspaceMember(workspace_id=workspace_id, user_id=teammate.id, role="member")
    session.add(membership)
    session.commit()
    session.refresh(membership)

    promote = client.patch(
        f"/api/v1/workspaces/{workspace_id}/members/{membership.id}",
        headers=auth_headers(),
        json={"role": "admin"},
    )
    assert promote.status_code == 200
    assert promote.json()["data"]["member"]["role"] == "admin"

    remove = client.delete(f"/api/v1/workspaces/{workspace_id}/members/{membership.id}", headers=auth_headers())
    assert remove.status_code == 200

    members = client.get(f"/api/v1/workspaces/{workspace_id}/members")
    assert members.status_code == 200
    assert len(members.json()["data"]["members"]) == 1


def test_member_can_leave_own_workspace(client: TestClient, session: Session):
    register_user(client, email="workspace-owner@example.com")
    workspace = create_workspace(client, name="Leave Workspace")
    workspace_id = UUID(workspace.json()["data"]["workspace"]["id"])

    teammate = User(email="self-leave@example.com", name="Self Leave", password_hash=hash_password("supersecret"))
    session.add(teammate)
    session.commit()
    session.refresh(teammate)

    membership = WorkspaceMember(workspace_id=workspace_id, user_id=teammate.id, role="member")
    session.add(membership)
    session.commit()
    session.refresh(membership)

    logout = client.post("/api/v1/auth/logout", headers=auth_headers())
    assert logout.status_code == 200

    login = login_user(client, email="self-leave@example.com")
    assert login.status_code == 200

    leave = client.delete(f"/api/v1/workspaces/{workspace_id}/members/{membership.id}", headers=auth_headers())
    assert leave.status_code == 200
    assert leave.json()["message"] == "Left workspace"

    workspaces = client.get("/api/v1/workspaces")
    assert workspaces.status_code == 200
    assert workspaces.json()["data"]["workspaces"] == []


def test_last_owner_cannot_be_demoted_or_removed(client: TestClient):
    register_user(client)
    workspace = create_workspace(client)
    workspace_id = workspace.json()["data"]["workspace"]["id"]

    members = client.get(f"/api/v1/workspaces/{workspace_id}/members")
    owner_member_id = members.json()["data"]["members"][0]["id"]

    demote = client.patch(
        f"/api/v1/workspaces/{workspace_id}/members/{owner_member_id}",
        headers=auth_headers(),
        json={"role": "member"},
    )
    assert demote.status_code == 400
    assert demote.json()["error"]["code"] == "last_owner_required"

    remove = client.delete(f"/api/v1/workspaces/{workspace_id}/members/{owner_member_id}", headers=auth_headers())
    assert remove.status_code == 400
    assert remove.json()["error"]["code"] == "last_owner_required"


def test_admin_cannot_grant_revoke_or_remove_owner_roles(client: TestClient, session: Session):
    register_user(client, email="phase3-owner@example.com")
    workspace = create_workspace(client)
    workspace_id = UUID(workspace.json()["data"]["workspace"]["id"])

    admin_user = User(email="admin@example.com", name="Admin", password_hash=hash_password("supersecret"))
    co_owner_user = User(email="owner2@example.com", name="Co Owner", password_hash=hash_password("supersecret"))
    session.add(admin_user)
    session.add(co_owner_user)
    session.commit()
    session.refresh(admin_user)
    session.refresh(co_owner_user)

    admin_membership = WorkspaceMember(workspace_id=workspace_id, user_id=admin_user.id, role="admin")
    co_owner_membership = WorkspaceMember(workspace_id=workspace_id, user_id=co_owner_user.id, role="owner")
    session.add(admin_membership)
    session.add(co_owner_membership)
    session.commit()
    session.refresh(admin_membership)
    session.refresh(co_owner_membership)

    logout = client.post("/api/v1/auth/logout", headers=auth_headers())
    assert logout.status_code == 200

    login = login_user(client, email="admin@example.com")
    assert login.status_code == 200

    grant_owner = client.patch(
        f"/api/v1/workspaces/{workspace_id}/members/{admin_membership.id}",
        headers=auth_headers(),
        json={"role": "owner"},
    )
    assert grant_owner.status_code == 403
    assert grant_owner.json()["error"]["code"] == "owner_role_forbidden"

    revoke_owner = client.patch(
        f"/api/v1/workspaces/{workspace_id}/members/{co_owner_membership.id}",
        headers=auth_headers(),
        json={"role": "admin"},
    )
    assert revoke_owner.status_code == 403
    assert revoke_owner.json()["error"]["code"] == "owner_role_forbidden"

    remove_owner = client.delete(
        f"/api/v1/workspaces/{workspace_id}/members/{co_owner_membership.id}",
        headers=auth_headers(),
    )
    assert remove_owner.status_code == 403
    assert remove_owner.json()["error"]["code"] == "owner_role_forbidden"
