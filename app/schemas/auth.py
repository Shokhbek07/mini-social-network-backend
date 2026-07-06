from pydantic import BaseModel, Field

from app.schemas.common import MessageResponse
from app.schemas.user import UserBase, UserRead


class RegisterRequest(UserBase):
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=320, description="Email or username")
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserRead
    verification_token: str | None = None


class VerificationTokenResponse(BaseModel):
    verification_token: str


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)


class VerifyEmailResponse(MessageResponse):
    pass
