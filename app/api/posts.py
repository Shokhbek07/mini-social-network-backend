from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_verified_user
from app.db.session import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.post import PostCreate, PostDetail, PostRead, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PaginatedResponse[PostRead])
def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[PostRead]:
    return post_service.list_posts(db, page, page_size, search, date_from, date_to)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> Post:
    return post_service.create_post(db, current_user, payload)


@router.get("/{post_id}", response_model=PostDetail)
def get_post(post_id: UUID, db: Session = Depends(get_db)) -> PostDetail:
    return post_service.get_post_detail(db, post_id)


@router.patch("/{post_id}", response_model=PostRead)
def update_post(
    post_id: UUID,
    payload: PostUpdate,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> Post:
    return post_service.update_post(db, post_id, current_user, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> None:
    post_service.delete_post(db, post_id, current_user)


@router.get("/{post_id}/comments", response_model=PaginatedResponse[CommentRead])
def list_comments(
    post_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CommentRead]:
    return post_service.list_comments(db, post_id, page, page_size)


@router.post("/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> Comment:
    return post_service.create_comment(db, post_id, current_user, payload)


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> None:
    post_service.delete_comment(db, post_id, comment_id, current_user)


@router.post("/{post_id}/like", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    return post_service.like_post(db, post_id, current_user)


@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    post_service.unlike_post(db, post_id, current_user)
