from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models import QueueItem, Track

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request, session: Session = Depends(get_session)):
    tracks = session.exec(select(Track)).all()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"app_name": settings.app_name, "tracks": tracks},
    )


@router.get("/favourites")
async def favourites(request: Request, session: Session = Depends(get_session)):
    tracks = session.exec(select(Track).where(Track.is_favourite == True)).all()  # noqa: E712
    return templates.TemplateResponse(
        request,
        "favourites.html",
        {"app_name": settings.app_name, "tracks": tracks},
    )


@router.get("/queue")
async def queue_page(request: Request, session: Session = Depends(get_session)):
    items = session.exec(select(QueueItem).order_by(QueueItem.added_at)).all()
    queue = []
    for item in items:
        track = session.get(Track, item.track_id)
        if track:
            queue.append({"item_id": item.id, "track": track, "added_at": item.added_at})
    return templates.TemplateResponse(
        request,
        "queue.html",
        {"app_name": settings.app_name, "queue": queue},
    )
