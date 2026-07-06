from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_by_email_or_username(db: Session, value: str) -> User | None:
    return db.scalar(select(User).where(or_(User.email == value, User.username == value)))


def ensure_email_available(db: Session, email: str) -> None:
    if get_user_by_email(db, email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")


def ensure_username_available(db: Session, username: str) -> None:
    if get_user_by_username(db, username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already taken")


def update_current_user(db: Session, user: User, payload: UserUpdate) -> User:
    if payload.username is not None and payload.username != user.username:
        ensure_username_available(db, payload.username)
        user.username = payload.username

    if payload.full_name is not None:
        user.full_name = payload.full_name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already taken",
        ) from None

    db.refresh(user)
    return user
