from __future__ import annotations

from .conftest import auth_headers


def test_origin_validation_allows_trusted_origin(client):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers("http://localhost:3000"),
        json={"email": "secure@example.com", "password": "supersecret", "name": "Secure"},
    )
    assert response.status_code == 200


def test_origin_validation_rejects_untrusted_origin(client):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers("https://evil.example"),
        json={"email": "bad@example.com", "password": "supersecret", "name": "Bad"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "invalid_origin"

