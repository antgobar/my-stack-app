from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlmodel import Session, select

from app.database import get_session
from app.models import Track

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/search")
async def search_tracks(q: str = "", session: Session = Depends(get_session)) -> list[dict]:
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


@router.post("/{track_id}/favourite")
async def toggle_favourite(track_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    track.is_favourite = not track.is_favourite
    session.add(track)
    session.commit()
    return JSONResponse({"is_favourite": track.is_favourite})
