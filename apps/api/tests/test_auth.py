from __future__ import annotations

from fastapi.testclient import TestClient

from .conftest import auth_headers


def register_user(client: TestClient, email: str = "owner@example.com", password: str = "supersecret", name: str = "Owner"):
    return client.post(
        "/api/v1/auth/register",
        headers=auth_headers(),
        json={"email": email, "password": password, "name": name},
    )


def login_user(client: TestClient, email: str = "owner@example.com", password: str = "supersecret"):
    return client.post(
        "/api/v1/auth/login",
        headers=auth_headers(),
        json={"email": email, "password": password},
    )


def test_register_login_me_logout_refresh(client: TestClient):
    register = register_user(client)
    assert register.status_code == 200
    assert register.json()["data"]["user"]["email"] == "owner@example.com"

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["data"]["user"]["name"] == "Owner"

    logout = client.post("/api/v1/auth/logout", headers=auth_headers())
    assert logout.status_code == 200

    after_logout = client.get("/api/v1/auth/me")
    assert after_logout.status_code == 401

    login = login_user(client)
    assert login.status_code == 200

    refresh = client.post("/api/v1/auth/refresh", headers=auth_headers())
    assert refresh.status_code == 200

