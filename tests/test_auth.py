from fastapi.testclient import TestClient

from tests.helpers import DEFAULT_PASSWORD, auth_headers, login_user, register_user


def test_successful_registration(client: TestClient) -> None:
    registration = register_user(client)

    assert registration["verification_token"]
    assert registration["user"]["email"]
    assert registration["user"]["username"]
    assert registration["user"]["is_verified"] is False
    assert "password_hash" not in registration["user"]


def test_duplicate_email_registration_returns_409(client: TestClient) -> None:
    registration = register_user(client)
    response = client.post(
        "/auth/register",
        json={
            "email": registration["user"]["email"],
            "username": "different_username",
            "full_name": "Another User",
            "password": DEFAULT_PASSWORD,
        },
    )

    assert response.status_code == 409


def test_duplicate_username_registration_returns_409(client: TestClient) -> None:
    registration = register_user(client)
    response = client.post(
        "/auth/register",
        json={
            "email": "different@example.com",
            "username": registration["user"]["username"],
            "full_name": "Another User",
            "password": DEFAULT_PASSWORD,
        },
    )

    assert response.status_code == 409


def test_successful_login(client: TestClient) -> None:
    registration = register_user(client)

    response = client.post(
        "/auth/login",
        json={"login": registration["user"]["email"], "password": DEFAULT_PASSWORD},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_auth_me_with_valid_token(client: TestClient) -> None:
    registration = register_user(client)
    token = login_user(client, registration["user"]["email"])

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["id"] == registration["user"]["id"]
    assert response.json()["email"] == registration["user"]["email"]


def test_auth_me_with_invalid_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers=auth_headers("invalid-token"))

    assert response.status_code == 401
