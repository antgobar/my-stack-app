from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.database import seed_tracks
from app.models import Track


@pytest.fixture()
def db_session():
    """Isolated in-memory DB for database unit tests."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    with Session(eng) as session:
        yield session


@pytest.fixture()
def audio_dir(tmp_path: Path) -> Path:
    d = tmp_path / "Audio"
    d.mkdir()
    return d


@pytest.fixture()
def covers_dir(tmp_path: Path) -> Path:
    d = tmp_path / "AlbumCovers"
    d.mkdir()
    return d


def _mp3(directory: Path, name: str) -> Path:
    f = directory / name
    f.touch()
    return f


def _img(directory: Path, name: str) -> Path:
    f = directory / name
    f.touch()
    return f


def test_seed_empty_audio_dir(db_session, audio_dir, covers_dir):
    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)
    assert db_session.exec(select(Track)).all() == []


def test_seed_parses_artist_title(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "HoliznaCC0 - Punk.mp3")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    track = db_session.exec(select(Track)).first()
    assert track is not None
    assert track.artist_name == "HoliznaCC0"
    assert track.track_name == "Punk"
    assert track.file_path == "HoliznaCC0 - Punk.mp3"


def test_seed_unknown_artist_no_separator(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "SongTitle.mp3")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    track = db_session.exec(select(Track)).first()
    assert track is not None
    assert track.artist_name == "Unknown"
    assert track.track_name == "SongTitle"


def test_seed_skips_existing_track(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "Artist - Title.mp3")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)
    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    tracks = db_session.exec(select(Track)).all()
    assert len(tracks) == 1


def test_seed_updates_missing_cover(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "Artist - Title.mp3")
    cover = _img(covers_dir, "cover.png")

    # First seed — no cover available yet
    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)
    track = db_session.exec(select(Track)).first()
    assert track is not None
    assert track.album_cover_path == cover.name

    # Manually clear the cover to simulate a missing-cover scenario
    track.album_cover_path = None
    db_session.add(track)
    db_session.commit()

    # Second seed should restore the cover
    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)
    db_session.refresh(track)
    assert track.album_cover_path == cover.name


def test_seed_prefers_sidecar_cover(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "Artist - Title.mp3")
    sidecar = _img(audio_dir, "Artist - Title.png")
    _img(covers_dir, "other_cover.png")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    track = db_session.exec(select(Track)).first()
    assert track is not None
    assert track.album_cover_path == sidecar.name


def test_seed_falls_back_to_random_cover(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "Artist - Title.mp3")
    cover = _img(covers_dir, "fallback.png")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    track = db_session.exec(select(Track)).first()
    assert track is not None
    assert track.album_cover_path == cover.name


def test_seed_multiple_tracks(db_session, audio_dir, covers_dir):
    _mp3(audio_dir, "Artist A - Song One.mp3")
    _mp3(audio_dir, "Artist B - Song Two.mp3")

    seed_tracks(audio_dir=audio_dir, covers_dir=covers_dir, session=db_session)

    tracks = db_session.exec(select(Track)).all()
    assert len(tracks) == 2
    names = {t.track_name for t in tracks}
    assert names == {"Song One", "Song Two"}
