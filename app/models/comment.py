from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class Comment(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "comments"
    __table_args__ = (Index("ix_comments_created_at", "created_at"),)

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
