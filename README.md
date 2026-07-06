# Mini Social Network Backend

FastAPI backend for a mini social network test task.

The project implements users, JWT authentication, email verification without SMTP, posts,
comments, likes, a public feed, PostgreSQL persistence, Alembic migrations, Docker Compose,
Celery + Redis background cleanup, and a focused pytest suite.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Redis
- Celery + Celery Beat
- Pydantic v2
- Pytest
- Ruff
- Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Environment

`.env.example` contains all required settings:

```env
APP_NAME=Mini Social Network API
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/social_network
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-this-secret-key-in-real-use
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMAIL_VERIFICATION_EXPIRE_HOURS=24
CLEANUP_UNVERIFIED_AFTER_HOURS=48
ADMIN_TOKEN=change-this-admin-token
```

## Migrations

Migrations run automatically when the `app` container starts.

Run manually:

```bash
docker compose exec app alembic upgrade head
```

Create a new migration after model changes:

```bash
docker compose exec app alembic revision --autogenerate -m "describe change"
```

## Tests

Run the required test suite:

```bash
docker compose exec app pytest -q
```

The tests use an isolated in-memory SQLite database and do not touch the Docker PostgreSQL
database.

## Celery Cleanup

The project includes a Celery task:

```text
app.tasks.cleanup.cleanup_unverified_users
```

Celery Beat schedules it every hour. It deletes unverified users whose latest unused email
verification token has expired.

Verify the worker has registered the task:

```bash
docker compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

Manually enqueue cleanup through the API:

```bash
curl -X POST http://localhost:8000/admin/cleanup-unverified-users \
  -H "X-Admin-Token: change-this-admin-token"
```

Call the Celery task directly:

```bash
docker compose exec celery_worker celery -A app.tasks.celery_app call app.tasks.cleanup.cleanup_unverified_users
```

## Project Structure

```text
app/
  api/          FastAPI routers and request dependencies
  core/         configuration and security helpers
  db/           SQLAlchemy base/session
  models/       SQLAlchemy models
  schemas/      Pydantic request/response schemas
  services/     business logic
  tasks/        Celery app and tasks
alembic/        Alembic migration environment and versions
tests/          pytest suite
```

## Endpoints

Auth and users:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /auth/verify-email?token=...`
- `POST /auth/verify-email`
- `POST /auth/resend-verification`
- `PATCH /users/me`

Posts, comments, likes:

- `GET /posts`
- `POST /posts`
- `GET /posts/{post_id}`
- `PATCH /posts/{post_id}`
- `DELETE /posts/{post_id}`
- `GET /posts/{post_id}/comments`
- `POST /posts/{post_id}/comments`
- `DELETE /posts/{post_id}/comments/{comment_id}`
- `POST /posts/{post_id}/like`
- `DELETE /posts/{post_id}/like`

Feed:

- `GET /feed`
- `GET /all`

Admin:

- `POST /admin/cleanup-unverified-users`

## Curl Examples

Register:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user_123","full_name":"User Example","password":"strong-password"}'
```

Login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"user@example.com","password":"strong-password"}'
```

Current user:

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

Verify email:

```bash
curl "http://localhost:8000/auth/verify-email?token=<verification_token>"
```

Create post:

```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer <verified_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"First post","content":"Hello from the mini social network"}'
```

List posts with pagination, search, and date filters:

```bash
curl "http://localhost:8000/posts?page=1&page_size=10&search=hello&date_from=2026-01-01T00:00:00Z"
```

Get post detail with comments and likes:

```bash
curl http://localhost:8000/posts/<post_id>
```

Create comment:

```bash
curl -X POST http://localhost:8000/posts/<post_id>/comments \
  -H "Authorization: Bearer <verified_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"content":"Nice post"}'
```

List comments:

```bash
curl "http://localhost:8000/posts/<post_id>/comments?page=1&page_size=10"
```

Like post:

```bash
curl -X POST http://localhost:8000/posts/<post_id>/like \
  -H "Authorization: Bearer <access_token>"
```

Unlike post:

```bash
curl -X DELETE http://localhost:8000/posts/<post_id>/like \
  -H "Authorization: Bearer <access_token>"
```

Feed:

```bash
curl "http://localhost:8000/feed?page=1&page_size=10"
```

All users/posts feed:

```bash
curl "http://localhost:8000/all?page=1&page_size=10"
```

Enqueue cleanup:

```bash
curl -X POST http://localhost:8000/admin/cleanup-unverified-users \
  -H "X-Admin-Token: change-this-admin-token"
```

## Final Verification Commands

```bash
docker compose up --build
```

```bash
docker compose exec app pytest -q
```

```bash
docker compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

