from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models import Track

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request):
    with Session(engine) as session:
        tracks = session.exec(select(Track)).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name, "tracks": tracks},
    )


@router.get("/favourites")
async def favourites(request: Request):
    with Session(engine) as session:
        tracks = session.exec(select(Track).where(Track.is_favourite == True)).all()  # noqa: E712
    return templates.TemplateResponse(
        "favourites.html",
        {"request": request, "app_name": settings.app_name, "tracks": tracks},
    )
