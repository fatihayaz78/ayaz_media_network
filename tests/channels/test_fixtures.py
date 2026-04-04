import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from channels.fixtures.fixtures_fetcher import FixturesFetcher
from datetime import datetime, timedelta


def test_fetch_returns_list():
    f = FixturesFetcher()
    today = datetime.utcnow()
    next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    items = f.fetch(today_str, next_week)
    assert isinstance(items, list)


def test_rows_have_required_fields():
    f = FixturesFetcher()
    today = datetime.utcnow()
    next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    items = f.fetch(today_str, next_week)
    for item in items[:5]:
        assert "id" in item
        assert "home" in item
        assert "score" in item
        assert "away" in item
        assert "league" in item
        assert item["score"] == "vs"


def test_to_reel_groups_structure():
    f = FixturesFetcher()
    today = datetime.utcnow()
    next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    items = f.fetch(today_str, next_week)
    groups = f.to_reel_groups(items)
    assert isinstance(groups, list)
    for g in groups:
        assert "league" in g
        assert "display_name" in g
        assert "matches" in g
        assert isinstance(g["matches"], list)


def test_date_label_format():
    f = FixturesFetcher()
    label = f._format_date_label("2026-04-06")
    assert "·" in label
    assert any(d in label for d in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])


def test_video_maker_can_render_fixtures():
    """Integration test — renders a real MP4 with fixtures theme."""
    import tempfile
    from video_maker import make_reel

    config = {
        "channel_name": "TestChannel",
        "date": "07.04.2026",
        "continents": [{
            "name": "UPCOMING",
            "groups": [{
                "league": "TUE · 07 Apr",
                "display_name": "Tuesday April 7",
                "matches": [
                    {"id": "t1", "home": "Real Madrid", "score": "vs", "away": "Bayern Munich",
                     "status": "21:00", "time": "UCL", "league": "TUE · 07 Apr"},
                    {"id": "t2", "home": "Arsenal", "score": "vs", "away": "Man City",
                     "status": "19:45", "time": "EPL", "league": "TUE · 07 Apr"},
                    {"id": "t3", "home": "Barcelona", "score": "vs", "away": "Atletico",
                     "status": "20:00", "time": "LaLiga", "league": "TUE · 07 Apr"},
                ]
            }]
        }]
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        output = f.name

    try:
        make_reel(config, output, sport_id="fixtures")
        assert os.path.exists(output)
        assert os.path.getsize(output) > 10_000   # at least 10KB
        print(f"fixtures reel OK: {os.path.getsize(output)/1024:.0f} KB")
    finally:
        os.unlink(output)
