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
