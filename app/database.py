from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

AUDIO_DIR = Path("Audio")


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def seed_tracks() -> None:
    from app.models import Track  # local import to avoid circular deps at module load

    with Session(engine) as session:
        for f in sorted(AUDIO_DIR.glob("*.mp3")):
            file_path = f.name
            existing = session.exec(select(Track).where(Track.file_path == file_path)).first()
            if existing:
                continue

            parts = f.stem.split(" - ", 1)
            artist = parts[0] if len(parts) == 2 else "Unknown"
            title = parts[1] if len(parts) == 2 else parts[0]

            cover_path = None
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = AUDIO_DIR / (f.stem + ext)
                if candidate.exists():
                    cover_path = candidate.name
                    break

            session.add(Track(track_name=title, artist_name=artist, file_path=file_path, album_cover_path=cover_path))

        session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
