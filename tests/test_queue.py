from fastapi.testclient import TestClient


def test_add_to_queue(client: TestClient, track_factory):
    track = track_factory(track_name="Punk", artist_name="HoliznaCC0", file_path="punk.mp3")

    response = client.post(f"/queue/{track.id}")

    assert response.status_code == 201
    data = response.json()
    assert data["track_id"] == track.id
    assert "id" in data
    assert "added_at" in data


def test_add_to_queue_not_found(client: TestClient):
    response = client.post("/queue/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Track not found"


def test_get_queue_items_empty(client: TestClient):
    response = client.get("/queue/items")

    assert response.status_code == 200
    assert response.json() == []


def test_get_queue_items(client: TestClient, track_factory, queue_item_factory):
    track = track_factory(track_name="Punk", artist_name="HoliznaCC0", file_path="punk.mp3")
    queue_item_factory(track_id=track.id)

    response = client.get("/queue/items")

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["track_name"] == "Punk"
    assert items[0]["artist_name"] == "HoliznaCC0"
    assert items[0]["file_path"] == "punk.mp3"
    assert items[0]["track_id"] == track.id
    assert "item_id" in items[0]
    assert "added_at" in items[0]


def test_clear_queue(client: TestClient, track_factory, queue_item_factory):
    track = track_factory(file_path="punk.mp3")
    queue_item_factory(track_id=track.id)
    queue_item_factory(track_id=track.id)

    response = client.delete("/queue/clear")

    assert response.status_code == 204
    assert client.get("/queue/items").json() == []


def test_clear_queue_empty(client: TestClient):
    response = client.delete("/queue/clear")

    assert response.status_code == 204


def test_remove_queue_item(client: TestClient, track_factory, queue_item_factory):
    track = track_factory(file_path="punk.mp3")
    item = queue_item_factory(track_id=track.id)

    response = client.delete(f"/queue/{item.id}")

    assert response.status_code == 204
    remaining = client.get("/queue/items").json()
    assert all(i["item_id"] != item.id for i in remaining)


def test_remove_queue_item_not_found(client: TestClient):
    response = client.delete("/queue/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Queue item not found"
