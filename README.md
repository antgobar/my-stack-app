# MySpot

A Spotify clone built with FastAPI, Postgres, and Redis.

## Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Migrations | Alembic |
| Templates | Jinja2 + Bootstrap 5 |
| Database | Postgres 15 |
| Cache | Redis 7 |
| Package manager | uv |

## Audio Files

> **Note:** Add your MP3 files to a folder named `Audio/` in the project root before starting the app. Files should be named in the format `Artist - Title.mp3`. This folder is not included in the repository.

## Local Development

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker + Docker Compose

### Setup

```bash
# 1. Install Python dependencies
uv sync


# 5. Start dev server
uv run uvicorn app.main:app --reload
```

App: http://localhost:8000  
API docs: http://localhost:8000/docs

## Tests

```bash
uv run pytest       # run all tests
uv run ruff check . # lint
```
