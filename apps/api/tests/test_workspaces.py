from __future__ import annotations

from fastapi.testclient import TestClient

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
