from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import hash_secret
from app.modules.auth.models import RefreshToken

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


def test_duplicate_registration_returns_conflict(client: TestClient):
    first = register_user(client, email="duplicate@example.com")
    assert first.status_code == 200

    second = register_user(client, email="duplicate@example.com")

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "email_already_registered"


def test_login_rate_limit_returns_429(client: TestClient):
    register_user(client, email="limited@example.com")

    for _ in range(5):
        failed_login = login_user(client, email="limited@example.com", password="wrong-password")
        assert failed_login.status_code == 401
        assert failed_login.json()["error"]["code"] == "invalid_credentials"

    blocked_login = login_user(client, email="limited@example.com", password="wrong-password")

    assert blocked_login.status_code == 429
    assert blocked_login.json()["error"]["code"] == "rate_limited"


def test_refresh_rotation_rejects_replay_of_old_token(client: TestClient):
    settings = get_settings()
    register_user(client, email="rotate@example.com")
    original_refresh_token = client.cookies.get(settings.refresh_cookie_name)
    assert original_refresh_token is not None

    refreshed = client.post("/api/v1/auth/refresh", headers=auth_headers())
    assert refreshed.status_code == 200

    rotated_refresh_token = client.cookies.get(settings.refresh_cookie_name)
    assert rotated_refresh_token is not None
    assert rotated_refresh_token != original_refresh_token

    client.cookies.set(
        settings.refresh_cookie_name,
        original_refresh_token,
        domain="testserver.local",
        path="/api/v1/auth",
    )
    replay = client.post("/api/v1/auth/refresh", headers=auth_headers())

    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "invalid_refresh_token"


def test_logout_revokes_refresh_token_and_old_password_stops_working(client: TestClient, session: Session):
    settings = get_settings()
    register_user(client, email="password@example.com")
    refresh_token = client.cookies.get(settings.refresh_cookie_name)
    assert refresh_token is not None

    change_password = client.post(
        "/api/v1/users/me/change-password",
        headers=auth_headers(),
        json={"current_password": "supersecret", "new_password": "newersecret"},
    )
    assert change_password.status_code == 200

    logout = client.post("/api/v1/auth/logout", headers=auth_headers())
    assert logout.status_code == 200

    refresh_row = session.exec(select(RefreshToken).where(RefreshToken.token_hash == hash_secret(refresh_token))).first()
    assert refresh_row is not None
    assert refresh_row.revoked_at is not None

    replay_client = client
    replay_client.cookies.set(
        settings.refresh_cookie_name,
        refresh_token,
        domain="testserver.local",
        path="/api/v1/auth",
    )
    replay_response = replay_client.post("/api/v1/auth/refresh", headers=auth_headers())
    assert replay_response.status_code == 401
    assert replay_response.json()["error"]["code"] == "invalid_refresh_token"

    old_login = login_user(client, email="password@example.com", password="supersecret")
    assert old_login.status_code == 401
    assert old_login.json()["error"]["code"] == "invalid_credentials"

    new_login = login_user(client, email="password@example.com", password="newersecret")
    assert new_login.status_code == 200


def test_change_password_rejects_password_reuse(client: TestClient):
    register_user(client, email="reuse@example.com")

    response = client.post(
        "/api/v1/users/me/change-password",
        headers=auth_headers(),
        json={"current_password": "supersecret", "new_password": "supersecret"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "password_reuse"


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
