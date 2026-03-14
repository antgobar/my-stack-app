from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import settings
from app.database import create_db_and_tables, engine, seed_tracks
from app.models import Track
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    seed_tracks()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/audio", StaticFiles(directory="Audio"), name="audio")
app.mount("/covers", StaticFiles(directory="AlbumCovers"), name="covers")

templates = Jinja2Templates(directory="app/templates")

app.include_router(health.router)


@app.get("/")
async def index(request: Request):
    with Session(engine) as session:
        tracks = session.exec(select(Track)).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name, "tracks": tracks},
    )
