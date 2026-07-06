from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.tasks.cleanup import cleanup_unverified_users

router = APIRouter(prefix="/admin", tags=["admin"])


class TaskQueuedResponse(BaseModel):
    task_id: str
    detail: str


@router.post("/cleanup-unverified-users", response_model=TaskQueuedResponse)
def enqueue_cleanup_unverified_users(
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> TaskQueuedResponse:
    if x_admin_token != get_settings().admin_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid admin token")

    result = cleanup_unverified_users.delay()
    return TaskQueuedResponse(task_id=result.id, detail="cleanup task enqueued")
