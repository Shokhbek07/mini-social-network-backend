from uuid import UUID

from pydantic import BaseModel


class FeedPost(BaseModel):
    id: UUID
    title: str
    content: str
    likes: list[UUID]


class FeedUser(BaseModel):
    username: str
    posts: list[FeedPost]
