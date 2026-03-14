# MySpot

A Spotify-style music player built with FastAPI + SQLModel + SQLite.

## Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Templates | Jinja2 + Bootstrap 5 |
| Database | SQLite (auto-created on startup) |
| Package manager | uv |
| Linting / formatting | Ruff |

## Features

### Core (all implemented)

- [x] Track listing with title, artist, and album cover
- [x] Currently playing track display
- [x] Play / pause (click and spacebar shortcut)
- [x] Skip to next / previous track
- [x] Audio streaming via HTML5 `<audio>`
- [x] Volume control
- [x] Select a track to play

### Aspirational (5 of 8 implemented)

- [x] Add, remove, and view favourite tracks
- [x] Track progress / seek bar (native HTML5 controls)
- [x] Add tracks to queue, play from queue with auto-advance
- [x] Live search with debounce (by title or artist)
- [ ] Playlists
- [ ] Shuffle mode
- [ ] Recently played history
- [ ] Session persistence (resume playback position)

### Technical

- [x] ~35 tests across 6 files (tracks, queue, pages, database, health)
- [x] CI pipeline via GitHub Actions (lint + test on every push)
- [x] Auto-seeding of tracks from `Audio/` directory on startup
- [x] Album cover auto-assignment from `AlbumCovers/`

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```bash
# Clone the repository
git clone <repo-url> && cd my-stack-app

# Install all dependencies (uv creates .venv automatically)
uv sync

# Start the dev server
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000 — the app is ready.

The SQLite database is created automatically on first startup. Tracks are seeded from filenames in `Audio/`, and album covers are assigned from `AlbumCovers/`.

## Audio Files

Place MP3 files in the `Audio/` directory at the project root. Files should follow the naming convention:

```
Artist - Title.mp3
```

The seed logic parses the filename to extract artist and track name. If no separator is found, the artist defaults to "Unknown".

Album covers in `AlbumCovers/` are auto-assigned — a sidecar image with the same name as the MP3 is preferred, otherwise a random cover is used as a fallback.

## Makefile

| Command | Description |
|---|---|
| `make install` | Install dependencies via `uv sync` |
| `make run` | Start the dev server on port 8000 |
| `make test` | Run all tests (verbose) |
| `make format` | Auto-fix lint issues and format code |

## Tests

```bash
uv run pytest            # run all tests
uv run pytest -v         # verbose
uv run ruff check .      # lint
uv run ruff format .     # format
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Track listing page |
| `GET` | `/favourites` | Favourites page |
| `GET` | `/queue` | Queue management page |
| `GET` | `/tracks/search?q=` | Search tracks by title or artist (JSON) |
| `POST` | `/tracks/{id}/favourite` | Toggle favourite status |
| `POST` | `/queue/{track_id}` | Add track to queue |
| `GET` | `/queue/items` | List queue items (JSON) |
| `DELETE` | `/queue/{item_id}` | Remove item from queue |
| `DELETE` | `/queue/clear` | Clear entire queue |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Auto-generated OpenAPI docs |

## Infrastructure (AWS Fargate)

The app deploys to AWS Fargate via CDK (TypeScript). All infrastructure lives in `infrastructure/`.

### Architecture

| Component | Detail |
|---|---|
| VPC | 2 AZs, public subnets only, no NAT gateway |
| ECS Cluster | Fargate launch type |
| Fargate Task | 0.25 vCPU / 512 MB, public IP |
| Load Balancer | Internet-facing ALB, health check on `/health` |
| Container | Multi-stage Docker build, non-root user, gunicorn + uvicorn |
| Data | Ephemeral SQLite + media baked into image, seeded on startup |

### Prerequisites

- Node.js 24+
- AWS CLI configured with credentials
- Docker running (CDK builds the image locally)

### Deploy

```bash
cd infrastructure
npm install
npx cdk bootstrap   # one-time per account/region
npx cdk deploy
```

The ALB DNS name is printed after deploy.

### Infrastructure Tests

```bash
cd infrastructure
npx jest              # run all tests (snapshot + assertions)
npx jest -u           # update snapshots after intentional changes
```

### Estimated Cost

| Resource | Monthly |
|---|---|
| Fargate (0.25 vCPU, 512 MB) | ~$9 |
| ALB | ~$16 |
| NAT Gateway | $0 (public subnets only) |
| **Total** | **~$25** |

## Given More Time

If I had more time to develop this further, I would add:

1. **S3 object storage** — move album covers and audio files to S3 and serve them via presigned URLs, separating file downloads from the backend service and reducing load on the application container.

2. **Separate upload service** — dedicated compute (e.g. a second Fargate service or Lambda) for ingesting and processing audio uploads, so upload processing doesn't affect the listening experience.

3. **CI/CD deployment pipeline** — full pipeline from GitHub Actions to AWS Fargate: build Docker image, push to ECR, deploy updated ECS task definition, with rolling deployments and health check gating.

4. **Multi-tenancy with authentication** — user accounts with login and session management, so favourites, queues, and playlists are scoped per user rather than global.

5. **CloudFront CDN** — put a CDN in front of S3 for low-latency global delivery of audio and cover art, with cache-control headers for efficient caching.

6. **PostgreSQL (RDS)** — migrate from SQLite to Postgres for production-grade concurrency, durability, and connection pooling.

7. **Observability** — structured JSON logging, CloudWatch metrics, and distributed tracing via AWS X-Ray for production monitoring and debugging.

8. **Remaining aspirational features** — playlists (create, edit, reorder), shuffle mode, recently played history, and session persistence to resume playback position across visits.
