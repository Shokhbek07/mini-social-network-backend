import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
FULL_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё\s-]+$")


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    full_name: str = Field(min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_RE.fullmatch(value):
            raise ValueError("username may contain only latin letters, digits and underscore")
        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if not FULL_NAME_RE.fullmatch(value):
            raise ValueError("full_name may contain only letters, spaces and hyphens")
        return value


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    full_name: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is not None and not USERNAME_RE.fullmatch(value):
            raise ValueError("username may contain only latin letters, digits and underscore")
        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is not None and not FULL_NAME_RE.fullmatch(value):
            raise ValueError("full_name may contain only letters, spaces and hyphens")
        return value
