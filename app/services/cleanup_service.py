from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import EmailVerificationToken, User


def cleanup_expired_unverified_users(db: Session) -> int:
    now = datetime.now(UTC)
    latest_active_token = (
        select(
            EmailVerificationToken.user_id,
            func.max(EmailVerificationToken.expires_at).label("latest_expires_at"),
        )
        .where(EmailVerificationToken.used_at.is_(None))
        .group_by(EmailVerificationToken.user_id)
        .subquery()
    )

    users = db.scalars(
        select(User)
        .join(latest_active_token, latest_active_token.c.user_id == User.id)
        .where(
            User.is_verified.is_(False),
            latest_active_token.c.latest_expires_at < now,
        )
    ).all()

    deleted_count = len(users)
    for user in users:
        db.delete(user)

    return deleted_count
