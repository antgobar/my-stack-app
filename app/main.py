from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import health

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/audio", StaticFiles(directory="Audio"), name="audio")

templates = Jinja2Templates(directory="app/templates")

app.include_router(health.router)

AUDIO_DIR = Path("Audio")


def _parse_tracks() -> list[dict]:
    tracks = []
    for f in sorted(AUDIO_DIR.glob("*.mp3")):
        parts = f.stem.split(" - ", 1)
        artist = parts[0] if len(parts) == 2 else "Unknown"
        title = parts[1] if len(parts) == 2 else parts[0]
        tracks.append({"filename": f.name, "artist": artist, "title": title})
    return tracks


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name, "tracks": _parse_tracks()},
    )
