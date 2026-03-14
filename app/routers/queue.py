from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models import QueueItem, Track

router = APIRouter(prefix="/queue", tags=["queue"])


@router.post("/{track_id}", status_code=201)
async def add_to_queue(track_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    item = QueueItem(track_id=track_id)
    session.add(item)
    session.commit()
    session.refresh(item)
    return JSONResponse(
        {"id": item.id, "track_id": item.track_id, "added_at": item.added_at.isoformat()},
        status_code=201,
    )


@router.get("/items")
async def get_queue_items(session: Session = Depends(get_session)) -> list[dict]:
    items = session.exec(select(QueueItem).order_by(QueueItem.added_at)).all()
    result = []
    for item in items:
        track = session.get(Track, item.track_id)
        if track:
            result.append(
                {
                    "item_id": item.id,
                    "track_id": track.id,
                    "track_name": track.track_name,
                    "artist_name": track.artist_name,
                    "file_path": track.file_path,
                    "album_cover_path": track.album_cover_path,
                    "added_at": item.added_at.isoformat(),
                }
            )
    return result


@router.delete("/clear", status_code=204)
async def clear_queue(session: Session = Depends(get_session)) -> None:
    items = session.exec(select(QueueItem)).all()
    for item in items:
        session.delete(item)
    session.commit()


@router.delete("/{item_id}", status_code=204)
async def remove_queue_item(item_id: int, session: Session = Depends(get_session)) -> None:
    item = session.get(QueueItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    session.delete(item)
    session.commit()
