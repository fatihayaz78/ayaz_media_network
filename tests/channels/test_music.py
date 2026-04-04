import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.music.music_fetcher import MusicFetcher


def test_fetch_europe():
    f = MusicFetcher()
    items = f.fetch(continent="EUROPE")
    assert len(items) == 10


def test_fetch_turkey():
    f = MusicFetcher()
    items = f.fetch(continent="TURKEY")
    assert len(items) == 10


def test_row_fields():
    f = MusicFetcher()
    items = f.fetch(continent="AMERICAS")
    for item in items:
        assert item["home"]   # rank + trend
        assert item["score"]  # song title
        assert item["away"]   # artist
        assert "w" in item["status"]  # weeks


def test_trend_arrows():
    f = MusicFetcher()
    items = f.fetch(continent="EUROPE")
    trends = [i["home"].split()[-1] for i in items]
    for t in trends:
        assert t in ("↑", "↓", "●", "NEW")


def test_video_maker_renders_music():
    import tempfile
    from video_maker import make_reel

    f = MusicFetcher()
    items = f.fetch(continent="EUROPE")
    groups = f.to_reel_groups(items)
    config = {
        "channel_name": "ayaz_musics",
        "date": "04.04.2026",
        "continents": [{"name": "CHARTS", "groups": groups}],
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out = tmp.name

    try:
        make_reel(config, out, sport_id="music")
        assert os.path.getsize(out) > 10_000
        print(f"music reel: {os.path.getsize(out) // 1024}KB")
    finally:
        os.unlink(out)
