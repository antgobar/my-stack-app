# MY Stack App

MySpot — a Spotify-style music player built with FastAPI + SQLModel + SQLite.

## Stack
- **FastAPI** with Jinja2 templates and Bootstrap 5
- **SQLModel** (SQLAlchemy + Pydantic ORM)
- **SQLite** — auto-created on startup via `create_db_and_tables()`
- **uv** — dependency management and virtual environment
- **Ruff** — linting and formatting

## Local Development

### Prerequisites
- Python 3.13+

### Setup
```bash
# Clone and enter project
git clone <repo-url> && cd my-stack-app

# Install dependencies (uv creates .venv automatically)
uv sync

# Start dev server (DB is created automatically on first run)
uv run uvicorn app.main:app --reload
```

App runs at http://localhost:8000

## Running Tests

```bash
uv run pytest
uv run pytest -v                      # verbose
uv run pytest tests/test_health.py   # specific file
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```

## Environment Variables

Configured via `.env` file (optional — defaults work for local development):
- `DATABASE_URL` — SQLite path (default: `sqlite:///./myspot.db`)
- `REDIS_URL` — Redis connection string (default: `redis://localhost:6379/0`)
- `SECRET_KEY` — App secret key (generate with `openssl rand -hex 32`)
- `ENVIRONMENT` — `local` | `production`
