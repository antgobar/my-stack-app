from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Track


@pytest.fixture(name="engine")
def engine_fixture():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # Patch lifespan hooks so they don't touch the real filesystem or DB
    with patch("app.main.create_db_and_tables"), patch("app.main.seed_tracks"):
        with TestClient(app) as client:
            yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="track_factory")
def track_factory_fixture(session: Session):
    """Insert Track rows into the test session and return them."""

    def _create(**kwargs) -> Track:
        defaults = {
            "track_name": "Test Track",
            "artist_name": "Test Artist",
            "file_path": "test.mp3",
            "album_cover_path": None,
            "is_favourite": False,
        }
        defaults.update(kwargs)
        track = Track(**defaults)
        session.add(track)
        session.commit()
        session.refresh(track)
        return track

    return _create
