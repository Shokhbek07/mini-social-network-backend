from fastapi import FastAPI

from app.api import admin, auth, feed, posts, users
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(admin.router)
    app.include_router(auth.router)
    app.include_router(feed.router)
    app.include_router(posts.router)
    app.include_router(users.router)

    return app


app = create_app()
