from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.modules.users.models import User
from app.modules.workspaces.models import WorkspaceMember

from .conftest import auth_headers
from .test_auth import login_user, register_user
from .test_workspaces import create_workspace


def test_invite_creation_and_acceptance_flow(client: TestClient):
    register_user(client, email="owner@example.com", name="Owner")
    workspace = create_workspace(client)
    workspace_id = workspace.json()["data"]["workspace"]["id"]

    invite_response = client.post(
        f"/api/v1/workspaces/{workspace_id}/invites",
        headers=auth_headers(),
        json={"email": "member@example.com", "role": "member"},
    )
    assert invite_response.status_code == 200
    invite_url = invite_response.json()["data"]["invite"]["invite_url"]
    token = invite_url.split("invite=")[1]

    client.post("/api/v1/auth/logout", headers=auth_headers())
    register_user(client, email="member@example.com", name="Member")

    invite_preview = client.get(f"/api/v1/invites/{token}")
    assert invite_preview.status_code == 200

    accept = client.post(f"/api/v1/invites/{token}/accept", headers=auth_headers())
    assert accept.status_code == 200

    members = client.get(f"/api/v1/workspaces/{workspace_id}/members")
    assert members.status_code == 200
    assert len(members.json()["data"]["members"]) == 2


def test_invite_revocation_updates_status(client: TestClient):
    register_user(client, email="invite-owner@example.com", name="Owner")
    workspace = create_workspace(client, name="Invite Revocation")
    workspace_id = workspace.json()["data"]["workspace"]["id"]

    invite_response = client.post(
        f"/api/v1/workspaces/{workspace_id}/invites",
        headers=auth_headers(),
        json={"email": "revoke-me@example.com", "role": "member"},
    )
    assert invite_response.status_code == 200
    invite_id = invite_response.json()["data"]["invite"]["id"]

    revoke = client.delete(f"/api/v1/workspaces/{workspace_id}/invites/{invite_id}", headers=auth_headers())
    assert revoke.status_code == 200

    invites = client.get(f"/api/v1/workspaces/{workspace_id}/invites")
    assert invites.status_code == 200
    assert invites.json()["data"]["invites"][0]["status"] == "revoked"


def test_admin_cannot_create_or_revoke_owner_invites(client: TestClient, session: Session):
    register_user(client, email="invite-phase4-owner@example.com", name="Owner")
    workspace = create_workspace(client, name="Owner Invite Rules")
    workspace_id = UUID(workspace.json()["data"]["workspace"]["id"])

    admin_user = User(email="invite-admin@example.com", name="Invite Admin", password_hash=hash_password("supersecret"))
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    admin_membership = WorkspaceMember(workspace_id=workspace_id, user_id=admin_user.id, role="admin")
    session.add(admin_membership)
    session.commit()

    owner_invite = client.post(
        f"/api/v1/workspaces/{workspace_id}/invites",
        headers=auth_headers(),
        json={"email": "owner-invite@example.com", "role": "owner"},
    )
    assert owner_invite.status_code == 200
    owner_invite_id = owner_invite.json()["data"]["invite"]["id"]

    logout = client.post("/api/v1/auth/logout", headers=auth_headers())
    assert logout.status_code == 200

    login = login_user(client, email="invite-admin@example.com")
    assert login.status_code == 200

    create_owner_invite = client.post(
        f"/api/v1/workspaces/{workspace_id}/invites",
        headers=auth_headers(),
        json={"email": "blocked-owner-invite@example.com", "role": "owner"},
    )
    assert create_owner_invite.status_code == 403
    assert create_owner_invite.json()["error"]["code"] == "owner_role_forbidden"

    revoke_owner_invite = client.delete(
        f"/api/v1/workspaces/{workspace_id}/invites/{owner_invite_id}",
        headers=auth_headers(),
    )
    assert revoke_owner_invite.status_code == 403
    assert revoke_owner_invite.json()["error"]["code"] == "owner_role_forbidden"
