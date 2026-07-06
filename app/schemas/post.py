from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.comment import CommentRead


class PostCreate(BaseModel):
    title: str = Field(min_length=5, max_length=255)
    content: str = Field(min_length=1, max_length=10000)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    content: str | None = Field(default=None, min_length=1, max_length=10000)


class PostRead(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostDetail(PostRead):
    comments: list[CommentRead] = Field(default_factory=list)
    likes: list[UUID] = Field(default_factory=list)
