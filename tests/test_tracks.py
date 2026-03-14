import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def seed(track_factory):
    track_factory(
        track_name="Punk",
        artist_name="HoliznaCC0",
        file_path="HoliznaCC0 - Punk.mp3",
    )
    track_factory(
        track_name="Super Metal",
        artist_name="Loyalty Freak Music",
        file_path="Loyalty Freak Music - Super Metal.mp3",
    )


def test_search_returns_all_tracks(client: TestClient):
    response = client.get("/tracks/search")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {t["track_name"] for t in data}
    assert names == {"Punk", "Super Metal"}


def test_search_filters_by_track_name(client: TestClient):
    response = client.get("/tracks/search?q=punk")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["track_name"] == "Punk"


def test_search_filters_by_artist_name(client: TestClient):
    response = client.get("/tracks/search?q=holizna")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["artist_name"] == "HoliznaCC0"


def test_search_returns_empty_list(client: TestClient):
    response = client.get("/tracks/search?q=zzznomatch")
    assert response.status_code == 200
    assert response.json() == []


def test_toggle_favourite_on(client: TestClient, session):
    from sqlmodel import select

    from app.models import Track

    track = session.exec(select(Track).where(Track.track_name == "Punk")).first()
    assert track is not None
    assert track.is_favourite is False

    response = client.post(f"/tracks/{track.id}/favourite")
    assert response.status_code == 200
    assert response.json() == {"is_favourite": True}

    session.refresh(track)
    assert track.is_favourite is True


def test_toggle_favourite_off(client: TestClient, session):
    from sqlmodel import select

    from app.models import Track

    track = session.exec(select(Track).where(Track.track_name == "Punk")).first()
    assert track is not None

    client.post(f"/tracks/{track.id}/favourite")
    response = client.post(f"/tracks/{track.id}/favourite")
    assert response.status_code == 200
    assert response.json() == {"is_favourite": False}

    session.refresh(track)
    assert track.is_favourite is False


def test_toggle_favourite_not_found(client: TestClient):
    response = client.post("/tracks/999/favourite")
    assert response.status_code == 404
    assert response.json()["detail"] == "Track not found"
