import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.techai.techai_fetcher import TechAIFetcher


def test_rss_collection():
    f = TechAIFetcher()
    items = f._collect_rss()
    assert len(items) > 0
    assert "title" in items[0]


def test_fetch_returns_rows():
    f = TechAIFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03")
    assert len(rows) > 0


def test_row_fields():
    f = TechAIFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03")
    for r in rows:
        assert all(k in r for k in ["id", "home", "score", "away", "league", "status"])


def test_wide_row_mode():
    """score must be empty string to trigger wide rendering."""
    f = TechAIFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03")
    for r in rows:
        assert r["score"] == "", f"Expected empty score, got: {r['score']}"


def test_to_reel_groups():
    f = TechAIFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03")
    groups = f.to_reel_groups(rows)
    assert len(groups) > 0
    for g in groups:
        assert g["league"] in [
            "MODEL UPDATES", "BIG TECH", "TOOLS",
            "FUNDING", "RESEARCH", "REGULATION",
        ]


def test_video_maker_renders_techai():
    import tempfile
    from video_maker import make_reel

    f = TechAIFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03")
    groups = f.to_reel_groups(rows)
    config = {
        "channel_name": "ayaz_techai",
        "date": "04.04.2026",
        "continents": [{"name": "AI & TECH", "groups": groups}],
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out = tmp.name

    try:
        make_reel(config, out, sport_id="techai")
        assert os.path.getsize(out) > 10_000
        print(f"techai reel: {os.path.getsize(out) // 1024}KB")
    finally:
        os.unlink(out)
