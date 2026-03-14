from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlmodel import Session, select

from app.config import settings
from app.database import create_db_and_tables, engine, seed_tracks
from app.models import Track
from app.routers import health


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


@app.get("/tracks/search")
async def search_tracks(q: str = "") -> list[dict]:
    with Session(engine) as session:
        pattern = f"%{q}%"
        tracks = session.exec(
            select(Track).where(
                or_(
                    Track.track_name.ilike(pattern),
                    Track.artist_name.ilike(pattern),
                )
            )
        ).all()
    return [t.model_dump() for t in tracks]


@app.post("/tracks/{track_id}/favourite")
async def toggle_favourite(track_id: int) -> JSONResponse:
    with Session(engine) as session:
        track = session.get(Track, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        track.is_favourite = not track.is_favourite
        session.add(track)
        session.commit()
        return JSONResponse({"is_favourite": track.is_favourite})


@app.get("/favourites")
async def favourites(request: Request):
    with Session(engine) as session:
        tracks = session.exec(select(Track).where(Track.is_favourite == True)).all()  # noqa: E712
    return templates.TemplateResponse(
        "favourites.html",
        {"request": request, "app_name": settings.app_name, "tracks": tracks},
    )
