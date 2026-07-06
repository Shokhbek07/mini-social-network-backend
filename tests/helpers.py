from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import EmailVerificationToken, User

DEFAULT_PASSWORD = "strong-password"


def unique_suffix() -> str:
    return uuid4().hex[:12]


def register_user(
    client: TestClient,
    *,
    email: str | None = None,
    username: str | None = None,
    full_name: str = "Test User",
    password: str = DEFAULT_PASSWORD,
) -> dict:
    suffix = unique_suffix()
    payload = {
        "email": email or f"user_{suffix}@example.com",
        "username": username or f"user_{suffix}",
        "full_name": full_name,
        "password": password,
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    data["password"] = password
    return data


def login_user(client: TestClient, login: str, password: str = DEFAULT_PASSWORD) -> str:
    response = client.post("/auth/login", json={"login": login, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def verify_registered_user(db: Session, registration: dict) -> None:
    token = registration["verification_token"]
    verification_token = db.scalar(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    assert verification_token is not None

    user = db.get(User, verification_token.user_id)
    assert user is not None

    user.is_verified = True
    verification_token.used_at = datetime.now(UTC)
    db.commit()


def create_post(client: TestClient, token: str, *, title: str = "Test post title") -> dict:
    response = client.post(
        "/posts",
        json={"title": title, "content": "Test post content"},
        headers=auth_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()
