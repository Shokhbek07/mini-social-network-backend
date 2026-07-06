from app.db.session import SessionLocal
from app.services.cleanup_service import cleanup_expired_unverified_users
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.cleanup.cleanup_unverified_users")
def cleanup_unverified_users() -> int:
    db = SessionLocal()
    try:
        deleted_count = cleanup_expired_unverified_users(db)
        db.commit()
        return deleted_count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
