import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.news.news_fetcher import NewsFetcher


def test_rss_collection():
    f = NewsFetcher()
    items = f._collect_rss()
    assert len(items) > 5


def test_fetch_returns_rows():
    f = NewsFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03")
    assert len(rows) > 0


def test_wide_row_mode():
    f = NewsFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03")
    for r in rows:
        assert r["score"] == ""


def test_row_fields():
    f = NewsFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03")
    for r in rows:
        assert all(k in r for k in ["id", "home", "score", "away", "league", "status"])
        assert r["away"] != ""


def test_to_reel_groups():
    f = NewsFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03")
    groups = f.to_reel_groups(rows)
    assert len(groups) > 0


def test_video_maker_renders_news():
    import tempfile
    from video_maker import make_reel

    f = NewsFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03")
    groups = f.to_reel_groups(rows)
    config = {
        "channel_name": "ayaz_news",
        "date": "03.04.2026",
        "continents": [{"name": "NEWS", "groups": groups}],
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out = tmp.name

    try:
        make_reel(config, out, sport_id="news")
        assert os.path.getsize(out) > 10_000
        print(f"news reel: {os.path.getsize(out) // 1024}KB")
    finally:
        os.unlink(out)
