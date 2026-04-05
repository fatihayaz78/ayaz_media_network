"""Test that all new app.py routes respond correctly."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


def test_root_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200


def test_scheduler_serves_html(client):
    r = client.get("/scheduler")
    assert r.status_code == 200


def test_fetch_channel_finance(client):
    r = client.get("/api/fetch/channel?channel_id=finance&from=2026-04-03&to=2026-04-03")
    j = r.get_json()
    assert j["ok"] is True
    assert isinstance(j["data"], list)
    assert j["count"] >= 0


def test_fetch_channel_music(client):
    r = client.get("/api/fetch/channel?channel_id=music&continent=EUROPE")
    j = r.get_json()
    assert j["ok"] is True


def test_fetch_channel_news(client):
    r = client.get("/api/fetch/channel?channel_id=news&from=2026-04-03&to=2026-04-03")
    j = r.get_json()
    assert j["ok"] is True
    assert j["count"] >= 0


def test_fetch_channel_games_deals(client):
    r = client.get("/api/fetch/channel?channel_id=games&fmt=game_deals&from=2026-04-03&to=2026-04-03")
    j = r.get_json()
    assert j["ok"] is True


def test_fetch_channel_techai(client):
    r = client.get("/api/fetch/channel?channel_id=techai&from=2026-03-27&to=2026-04-03")
    j = r.get_json()
    assert j["ok"] is True


def test_fetch_channel_unknown_falls_back(client):
    r = client.get("/api/fetch/channel?channel_id=futbol&from=2026-04-03&to=2026-04-03")
    j = r.get_json()
    assert j["ok"] is True


def test_scheduler_status(client):
    r = client.get("/api/scheduler/status")
    j = r.get_json()
    assert j["ok"] is True
    assert "schedules" in j
    ids = [s["id"] for s in j["schedules"]]
    assert "europe" in ids
    assert "fixtures" in ids
    assert "finance" in ids
    assert "news" in ids


def test_channel_page_serves_html(client):
    r = client.get("/channel")
    assert r.status_code == 200
    assert b"Channel Manager" in r.data


def test_channel_description_api(client):
    r = client.post("/api/channel/description",
                    json={"channel_id": "finance", "rows": []})
    j = r.get_json()
    # Without ANTHROPIC_API_KEY, should return ok=False with error
    assert "ok" in j
    if not j["ok"]:
        assert "error" in j


def test_reel_config_page(client):
    r = client.get("/reel-config")
    assert r.status_code == 200
    assert b"Reel Config" in r.data


def test_reel_config_api(client):
    # GET should return empty or existing config
    r = client.get("/api/reel-config/finance")
    j = r.get_json()
    assert j["ok"] is True
    assert "config" in j

    # POST should save config
    r = client.post("/api/reel-config/finance",
                    json={"header_text": "TEST", "reel_speed": 1.5})
    j = r.get_json()
    assert j["ok"] is True

    # GET again should return saved config
    r = client.get("/api/reel-config/finance")
    j = r.get_json()
    assert j["config"]["header_text"] == "TEST"

    # Cleanup: remove test config
    import os
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        "channels", "finance", "reel_config.json")
    if os.path.exists(path):
        os.remove(path)


def test_techai_editor_page(client):
    r = client.get("/techai-editor")
    assert r.status_code == 200
    assert b"Techai Editor" in r.data


def test_techai_items_api(client):
    # GET items
    r = client.get("/api/techai/items")
    j = r.get_json()
    assert j["ok"] is True
    assert isinstance(j["items"], list)

    # POST new item
    r = client.post("/api/techai/items",
                    json={"title": "Test Item", "category": "LLM", "source": "Test"})
    j = r.get_json()
    assert j["ok"] is True
    item_id = j["item"]["id"]

    # DELETE item
    r = client.delete(f"/api/techai/items/{item_id}")
    j = r.get_json()
    assert j["ok"] is True


def test_upload_page(client):
    r = client.get("/upload")
    assert r.status_code == 200
    assert b"YouTube Upload" in r.data


def test_upload_list_reels(client):
    r = client.get("/api/upload/list-reels")
    j = r.get_json()
    assert j["ok"] is True
    assert isinstance(j["reels"], list)


def test_upload_log(client):
    r = client.get("/api/upload/log")
    j = r.get_json()
    assert j["ok"] is True
    assert isinstance(j["log"], list)


def test_thumbnail_generation():
    from thumbnail_maker import generate_thumbnail
    import tempfile
    path = tempfile.mktemp(suffix=".jpg")
    try:
        generate_thumbnail("finance", "05.04.2026", ["Test item 1", "Test item 2"], path)
        assert os.path.exists(path)
        assert os.path.getsize(path) >= 10 * 1024  # at least 10KB
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_thumbnail_route_exists(client):
    # finance thumbnail was generated in Task 17.6
    r = client.get("/thumbnail/finance")
    assert r.status_code == 200
    assert r.content_type == "image/jpeg"


def test_thumbnail_route_404(client):
    r = client.get("/thumbnail/nonexistent_channel_xyz")
    assert r.status_code == 404
