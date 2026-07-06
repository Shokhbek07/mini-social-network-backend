from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.post import PostCreate, PostDetail, PostRead, PostUpdate


def get_post_or_404(db: Session, post_id: UUID) -> Post:
    post = db.scalar(
        select(Post)
        .options(selectinload(Post.comments), selectinload(Post.likes))
        .where(Post.id == post_id)
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post


def serialize_post(post: Post) -> PostRead:
    return PostRead.model_validate(post)


def serialize_post_detail(post: Post) -> PostDetail:
    comments = sorted(post.comments, key=lambda comment: comment.created_at)
    likes = [like.user_id for like in post.likes]
    return PostDetail(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at,
        comments=comments,
        likes=likes,
    )


def list_posts(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> PaginatedResponse[PostRead]:
    filters = []
    if search:
        search_pattern = f"%{search}%"
        filters.append(or_(Post.title.ilike(search_pattern), Post.content.ilike(search_pattern)))
    if date_from:
        filters.append(Post.created_at >= date_from)
    if date_to:
        filters.append(Post.created_at <= date_to)

    where_clause = and_(*filters) if filters else True
    total = db.scalar(select(func.count()).select_from(Post).where(where_clause)) or 0
    posts = db.scalars(
        select(Post)
        .where(where_clause)
        .order_by(Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PaginatedResponse[PostRead](
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_post(post) for post in posts],
    )


def create_post(db: Session, author: User, payload: PostCreate) -> Post:
    post = Post(author_id=author.id, title=payload.title, content=payload.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post_detail(db: Session, post_id: UUID) -> PostDetail:
    return serialize_post_detail(get_post_or_404(db, post_id))


def update_post(db: Session, post_id: UUID, current_user: User, payload: PostUpdate) -> Post:
    post = get_post_or_404(db, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only post author can modify this post",
        )

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: UUID, current_user: User) -> None:
    post = get_post_or_404(db, post_id)
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only post author can modify this post",
        )
    db.delete(post)
    db.commit()


def list_comments(
    db: Session,
    post_id: UUID,
    page: int,
    page_size: int,
) -> PaginatedResponse[CommentRead]:
    get_post_or_404(db, post_id)
    total = (
        db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id == post_id)) or 0
    )
    comments = db.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PaginatedResponse[CommentRead](
        total=total,
        page=page,
        page_size=page_size,
        items=[CommentRead.model_validate(comment) for comment in comments],
    )


def create_comment(db: Session, post_id: UUID, author: User, payload: CommentCreate) -> Comment:
    get_post_or_404(db, post_id)
    comment = Comment(post_id=post_id, author_id=author.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, post_id: UUID, comment_id: UUID, current_user: User) -> None:
    comment = db.get(Comment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only comment author can delete this comment",
        )
    db.delete(comment)
    db.commit()


def like_post(db: Session, post_id: UUID, current_user: User) -> MessageResponse:
    post = get_post_or_404(db, post_id)
    if post.author_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot like own post")

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="post already liked",
        ) from None

    return MessageResponse(detail="post liked")


def unlike_post(db: Session, post_id: UUID, current_user: User) -> None:
    get_post_or_404(db, post_id)
    like = db.scalar(select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id))
    if like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="like not found")
    db.delete(like)
    db.commit()
