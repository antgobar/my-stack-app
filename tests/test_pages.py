from fastapi.testclient import TestClient


def test_index_empty(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200


def test_index_ok(client: TestClient, track_factory):
    track_factory(track_name="Punk", artist_name="HoliznaCC0", file_path="punk.mp3")
    track_factory(
        track_name="Super Metal", artist_name="Loyalty Freak Music", file_path="metal.mp3"
    )

    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "Punk" in body
    assert "Super Metal" in body


def test_favourites_empty(client: TestClient):
    response = client.get("/favourites")
    assert response.status_code == 200


def test_favourites_ok(client: TestClient, track_factory):
    track_factory(
        track_name="Favourite Song",
        artist_name="Artist A",
        file_path="fav.mp3",
        is_favourite=True,
    )

    response = client.get("/favourites")
    assert response.status_code == 200
    assert "Favourite Song" in response.text


def test_favourites_excludes_non_favourites(client: TestClient, track_factory):
    track_factory(
        track_name="Loved Track",
        artist_name="Artist A",
        file_path="loved.mp3",
        is_favourite=True,
    )
    track_factory(
        track_name="Not Loved Track",
        artist_name="Artist B",
        file_path="notloved.mp3",
        is_favourite=False,
    )

    response = client.get("/favourites")
    assert response.status_code == 200
    body = response.text
    assert "Loved Track" in body
    assert "Not Loved Track" not in body


def test_queue_page_empty(client: TestClient):
    response = client.get("/queue")
    assert response.status_code == 200
    assert "Your queue is empty." in response.text


def test_queue_page_ok(client: TestClient, track_factory, queue_item_factory):
    track = track_factory(track_name="Punk", artist_name="HoliznaCC0", file_path="punk.mp3")
    queue_item_factory(track_id=track.id)

    response = client.get("/queue")
    assert response.status_code == 200
    body = response.text
    assert "Punk" in body
    assert "HoliznaCC0" in body
