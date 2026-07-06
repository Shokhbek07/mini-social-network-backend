from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.feed import FeedUser
from app.services.feed_service import get_feed

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=PaginatedResponse[FeedUser])
@router.get("/all", response_model=PaginatedResponse[FeedUser])
def feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[FeedUser]:
    return get_feed(db, page, page_size)
