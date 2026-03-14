# MY Stack App

A FastAPI web application with Postgres and Redis, deployed to AWS via CDK.

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
| Server | Gunicorn + Uvicorn workers |
| Infrastructure | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions |

## Local Development

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker + Docker Compose
- Node.js 24+ *(for CDK only)*

### Setup

```bash
# 1. Install Python dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env — defaults work with docker compose

# 3. Start Postgres + Redis
docker compose up db redis -d

# 4. Run migrations
uv run alembic upgrade head

# 5. Start dev server (hot reload)
uv run uvicorn app.main:app --reload
```

App: http://localhost:8000  
API docs: http://localhost:8000/docs

### Full Docker Stack

```bash
docker compose up          # start web + db + redis
docker compose up --build  # rebuild after Dockerfile changes
docker compose down        # stop and remove containers
docker compose logs -f web # tail app logs
```

## Database Migrations

```bash
# Generate migration after model changes
uv run alembic revision --autogenerate -m "add users table"

# Apply migrations
uv run alembic upgrade head

# Roll back one step
uv run alembic downgrade -1
```

## Tests

```bash
uv run pytest          # run all tests
uv run pytest -v       # verbose output
uv run ruff check .    # lint
```

## Project Structure

```
my-stack-app/
├── app/
│   ├── main.py          # FastAPI app factory + router mounting
│   ├── config.py        # Settings (pydantic-settings, reads .env)
│   ├── database.py      # SQLModel engine + get_session dependency
│   ├── models/          # SQLModel table models
│   ├── routers/         # APIRouter modules (one file per resource)
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS, JS, images
├── alembic/             # Migration scripts
├── infrastructure/      # AWS CDK (TypeScript)
│   ├── bin/app.ts       # CDK app entrypoint
│   └── lib/stack.ts     # Stack definition (EC2, RDS, ElastiCache)
├── tests/               # pytest tests
├── .cursor/rules/       # Cursor AI rules (injected into Claude context)
├── .github/workflows/   # CI/CD (test + deploy)
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml       # Python dependencies (uv)
└── CLAUDE.md            # Dev commands reference
```

## Infrastructure (AWS CDK)

Free-tier AWS resources:

| Resource | Type | Notes |
|---|---|---|
| EC2 | `t2.micro` | 750 hrs/month free |
| RDS Postgres | `db.t3.micro` | 20GB, single-AZ |
| ElastiCache Redis | `cache.t3.micro` | Single node |

```bash
cd infrastructure
npm install

# First time only (per AWS account + region)
npx cdk bootstrap

# Preview changes
npm run cdk:diff

# Deploy
npm run cdk:deploy

# Tear down (avoid ongoing costs)
npm run cdk:destroy
```

## Required GitHub Secrets

For the deploy workflow to work, add these to your repo settings:

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | e.g. `eu-west-1` |
| `EC2_INSTANCE_ID` | Instance ID from CDK output |

## Environment Variables

See `.env.example` for all variables. Key ones:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection string |
| `SECRET_KEY` | App secret (`openssl rand -hex 32`) |
| `ENVIRONMENT` | `local` or `production` |
