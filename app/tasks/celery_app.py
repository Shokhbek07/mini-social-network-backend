from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "mini_social_network",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.timezone = "UTC"
celery_app.conf.imports = ("app.tasks.cleanup",)
celery_app.conf.beat_schedule = {
    "cleanup-unverified-users-hourly": {
        "task": "app.tasks.cleanup.cleanup_unverified_users",
        "schedule": crontab(minute=0),
    }
}
