from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_db_and_tables, seed_tracks
from app.routers import health, pages, queue, tracks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    seed_tracks()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/audio", StaticFiles(directory="Audio", check_dir=False), name="audio")
app.mount("/covers", StaticFiles(directory="AlbumCovers", check_dir=False), name="covers")

app.include_router(health.router)
app.include_router(tracks.router)
app.include_router(queue.router)
app.include_router(pages.router)
