import random
from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

AUDIO_DIR = Path("Audio")
COVERS_DIR = Path("AlbumCovers")


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def seed_tracks() -> None:
    from app.models import Track  # local import to avoid circular deps at module load

    covers = (
        sorted(COVERS_DIR.glob("*.png"))
        + sorted(COVERS_DIR.glob("*.jpg"))
        + sorted(COVERS_DIR.glob("*.jpeg"))
    )

    with Session(engine) as session:
        for f in sorted(AUDIO_DIR.glob("*.mp3")):
            file_path = f.name
            existing = session.exec(select(Track).where(Track.file_path == file_path)).first()

            cover_path = None
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = AUDIO_DIR / (f.stem + ext)
                if candidate.exists():
                    cover_path = candidate.name
                    break

            if cover_path is None and covers:
                cover_path = random.choice(covers).name

            if existing:
                if existing.album_cover_path is None and cover_path:
                    existing.album_cover_path = cover_path
                    session.add(existing)
                continue

            parts = f.stem.split(" - ", 1)
            artist = parts[0] if len(parts) == 2 else "Unknown"
            title = parts[1] if len(parts) == 2 else parts[0]

            session.add(
                Track(
                    track_name=title,
                    artist_name=artist,
                    file_path=file_path,
                    album_cover_path=cover_path,
                )
            )

        session.commit()


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
