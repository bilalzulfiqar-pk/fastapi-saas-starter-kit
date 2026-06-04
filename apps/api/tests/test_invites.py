from __future__ import annotations

from fastapi.testclient import TestClient

from .conftest import auth_headers
from .test_auth import register_user
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

