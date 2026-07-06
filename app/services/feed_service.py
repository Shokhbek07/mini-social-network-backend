from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.post import Post
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.feed import FeedPost, FeedUser


def get_feed(db: Session, page: int, page_size: int) -> PaginatedResponse[FeedUser]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(
        select(User)
        .options(selectinload(User.posts).selectinload(Post.likes))
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = []
    for user in users:
        posts = sorted(user.posts, key=lambda post: post.created_at, reverse=True)
        items.append(
            FeedUser(
                username=user.username,
                posts=[
                    FeedPost(
                        id=post.id,
                        title=post.title,
                        content=post.content,
                        likes=[like.user_id for like in post.likes],
                    )
                    for post in posts
                ],
            )
        )

    return PaginatedResponse[FeedUser](
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )
