from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.workspaces.models import WorkspaceMember

from .conftest import auth_headers
from .test_auth import register_user


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
