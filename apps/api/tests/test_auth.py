from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import get_settings

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


def test_register_sets_session_marker_cookie(client: TestClient):
    response = register_user(client, email="session@example.com")

    assert response.status_code == 200
    assert response.cookies.get(get_settings().session_cookie_name) == "1"


def test_invalid_refresh_clears_auth_cookies(client: TestClient):
    settings = get_settings()
    client.cookies.set(settings.access_cookie_name, "stale-access", domain="testserver.local", path="/")
    client.cookies.set(settings.refresh_cookie_name, "stale-refresh", domain="testserver.local", path="/api/v1/auth")
    client.cookies.set(settings.session_cookie_name, "1", domain="testserver.local", path="/")

    response = client.post("/api/v1/auth/refresh", headers=auth_headers())

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"
    set_cookie_headers = response.headers.get_list("set-cookie")
    assert any(header.startswith(f"{settings.access_cookie_name}=") and "Path=/" in header for header in set_cookie_headers)
    assert any(
        header.startswith(f"{settings.refresh_cookie_name}=") and "Path=/api/v1/auth" in header
        for header in set_cookie_headers
    )
    assert any(header.startswith(f"{settings.session_cookie_name}=") and "Path=/" in header for header in set_cookie_headers)
    assert client.cookies.get(settings.access_cookie_name) is None
    assert client.cookies.get(settings.refresh_cookie_name) is None
    assert client.cookies.get(settings.session_cookie_name) is None
