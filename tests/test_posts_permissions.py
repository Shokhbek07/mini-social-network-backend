from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.helpers import (
    auth_headers,
    create_post,
    login_user,
    register_user,
    verify_registered_user,
)


def test_unverified_user_cannot_create_post(client: TestClient) -> None:
    registration = register_user(client)
    token = login_user(client, registration["user"]["email"])

    response = client.post(
        "/posts",
        json={"title": "Blocked post", "content": "Blocked content"},
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_verified_user_can_create_post(client: TestClient, db_session: Session) -> None:
    registration = register_user(client)
    verify_registered_user(db_session, registration)
    token = login_user(client, registration["user"]["email"])

    response = client.post(
        "/posts",
        json={"title": "Allowed post", "content": "Allowed content"},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Allowed post"


def test_user_cannot_like_own_post(client: TestClient, db_session: Session) -> None:
    registration = register_user(client)
    verify_registered_user(db_session, registration)
    token = login_user(client, registration["user"]["email"])
    post = create_post(client, token)

    response = client.post(f"/posts/{post['id']}/like", headers=auth_headers(token))

    assert response.status_code == 403


def test_duplicate_like_returns_409(client: TestClient, db_session: Session) -> None:
    author = register_user(client)
    verify_registered_user(db_session, author)
    author_token = login_user(client, author["user"]["email"])
    post = create_post(client, author_token)

    liker = register_user(client)
    liker_token = login_user(client, liker["user"]["email"])

    first_response = client.post(f"/posts/{post['id']}/like", headers=auth_headers(liker_token))
    second_response = client.post(f"/posts/{post['id']}/like", headers=auth_headers(liker_token))

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_non_owner_cannot_edit_post(client: TestClient, db_session: Session) -> None:
    author = register_user(client)
    verify_registered_user(db_session, author)
    author_token = login_user(client, author["user"]["email"])
    post = create_post(client, author_token)

    other_user = register_user(client)
    verify_registered_user(db_session, other_user)
    other_token = login_user(client, other_user["user"]["email"])

    response = client.patch(
        f"/posts/{post['id']}",
        json={"title": "Blocked edit"},
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403
