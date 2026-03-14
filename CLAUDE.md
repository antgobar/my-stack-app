# MY Stack App

FastAPI + SQLModel + Postgres + Redis, deployed to AWS via CDK.

## Stack
- **FastAPI** with Jinja2 templates and Bootstrap 5
- **SQLModel** (SQLAlchemy + Pydantic ORM)
- **Alembic** for migrations
- **Postgres 15** + **Redis 7**
- **AWS CDK (TypeScript)** — EC2 t2.micro, RDS db.t3.micro, ElastiCache cache.t3.micro

## Local Development

### Prerequisites
- Python 3.11+
- Docker + Docker Compose
- Node.js 18+ (for CDK)

### Setup
```bash
# Clone and enter project
git clone <repo-url> && cd my-stack-app

# Install dependencies (uv creates .venv automatically)
uv sync

# Copy and configure env vars
cp .env.example .env
# Edit .env with your values

# Start Postgres + Redis
docker compose up db redis -d

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn app.main:app --reload
```

App runs at http://localhost:8000

### Full Docker Stack
```bash
docker compose up        # starts web + db + redis
docker compose down      # stop all
docker compose logs web  # view app logs
```

## Database Migrations

```bash
# After changing models
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head

# Roll back one step
uv run alembic downgrade -1
```

## Running Tests

```bash
uv run pytest
uv run pytest -v                # verbose
uv run pytest tests/test_api.py # specific file
```

## Infrastructure (AWS CDK)

```bash
cd infrastructure
npm install
npm run cdk bootstrap    # first time only, per AWS account/region
npm run cdk diff         # preview changes
npm run cdk deploy       # deploy to AWS
npm run cdk destroy      # tear down to avoid costs
```

## Deployment (Manual)

```bash
# SSH to EC2
ssh -i key.pem ec2-user@<ec2-ip>

# Pull latest and restart
git pull && docker compose up -d --build
```

## Environment Variables

See `.env.example` for all required variables. Key ones:
- `DATABASE_URL` — Postgres connection string
- `REDIS_URL` — Redis connection string
- `SECRET_KEY` — App secret key (generate with `openssl rand -hex 32`)
- `ENVIRONMENT` — `local` | `production`
