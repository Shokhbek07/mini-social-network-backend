from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import EmailVerificationToken, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.user_service import (
    ensure_email_available,
    ensure_username_available,
    get_user_by_email_or_username,
)


def create_email_verification_token(db: Session, user: User) -> EmailVerificationToken:
    expires_at = datetime.now(UTC) + timedelta(hours=get_settings().email_verification_expire_hours)
    verification_token = EmailVerificationToken(
        token=token_urlsafe(32),
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(verification_token)
    db.flush()
    return verification_token


def register_user(db: Session, payload: RegisterRequest) -> tuple[User, str]:
    email = str(payload.email)
    ensure_email_available(db, email)
    ensure_username_available(db, payload.username)

    user = User(
        email=email,
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)

    try:
        db.flush()
        verification_token = create_email_verification_token(db, user)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        detail = "email or username already exists"
        message = str(exc.orig).lower()
        if "uq_users_email" in message or "email" in message:
            detail = "email already registered"
        elif "uq_users_username" in message or "username" in message:
            detail = "username already taken"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from None

    db.refresh(user)
    return user, verification_token.token


def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = get_user_by_email_or_username(db, payload.login)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return TokenResponse(access_token=create_access_token(user.id))


def verify_email_token(db: Session, token: str) -> User:
    verification_token = db.scalar(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    if verification_token is None or verification_token.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid verification token",
        )

    if verification_token.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="verification token expired",
        )

    user = db.get(User, verification_token.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid verification token",
        )

    user.is_verified = True
    verification_token.used_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def resend_verification_token(db: Session, user: User) -> str:
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email already verified"
        )

    verification_token = create_email_verification_token(db, user)
    db.commit()
    return verification_token.token
