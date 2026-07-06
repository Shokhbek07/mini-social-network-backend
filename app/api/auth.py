from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    VerificationTokenResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    user, verification_token = auth_service.register_user(db, payload)
    return RegisterResponse(
        user=UserRead.model_validate(user), verification_token=verification_token
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login_user(db, payload)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/verify-email", response_model=VerifyEmailResponse)
def verify_email_get(token: str, db: Session = Depends(get_db)) -> VerifyEmailResponse:
    auth_service.verify_email_token(db, token)
    return VerifyEmailResponse(detail="email verified")


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email_post(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> VerifyEmailResponse:
    auth_service.verify_email_token(db, payload.token)
    return VerifyEmailResponse(detail="email verified")


@router.post("/resend-verification", response_model=VerificationTokenResponse)
def resend_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VerificationTokenResponse:
    token = auth_service.resend_verification_token(db, current_user)
    return VerificationTokenResponse(verification_token=token)
