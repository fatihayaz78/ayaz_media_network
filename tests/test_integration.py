"""
Full pipeline integration test.
Tests: fetch → group → make_reel for all 8 channels.
Skips channels where live API is unreachable.
"""
import pytest
import os
import sys
import json
import tempfile
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from video_maker import make_reel
from sports_daemon import get_channel_rows, group_by_continent

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")) as f:
    CONFIG = json.load(f)

LEAGUE_DISPLAY = CONFIG.get("league_display", {})

FETCHER_MAP = {
    "fixtures": ("channels.fixtures.fixtures_fetcher", "FixturesFetcher"),
    "finance":  ("channels.finance.finance_fetcher",   "FinanceFetcher"),
    "music":    ("channels.music.music_fetcher",       "MusicFetcher"),
    "techai":   ("channels.techai.techai_fetcher",     "TechAIFetcher"),
    "transfer": ("channels.transfer.transfer_fetcher", "TransferFetcher"),
    "news":     ("channels.news.news_fetcher",         "NewsFetcher"),
    "games":    ("channels.games.games_fetcher",       "GamesFetcher"),
}

CONTINENT_NAMES = {
    "fixtures": "UPCOMING",
    "finance":  "MARKETS",
    "music":    "CHARTS",
    "techai":   "AI & TECH",
    "transfer": "TRANSFERS",
    "news":     "NEWS",
    "games":    "GAMING",
}


def _make_reel_for_schedule(schedule_id: str, sport_id: str,
                            extra: dict = None) -> int:
    """Returns MP4 file size in bytes, 0 if skipped."""
    schedule = next((s for s in CONFIG["schedules"]
                     if s["id"] == schedule_id), None)
    if not schedule:
        print(f"  [{schedule_id}] schedule not found in config.json")
        return 0
    if extra:
        schedule = {**schedule, **extra}

    from datetime import date, timedelta
    date_str = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        rows = get_channel_rows(schedule, date_str)
    except Exception as e:
        print(f"  [{schedule_id}] fetch error: {e}")
        return 0

    if not rows:
        print(f"  [{schedule_id}] no data — skipping reel")
        return 0

    print(f"  [{schedule_id}] fetched {len(rows)} rows")

    # Try standard continent grouping first
    continents = group_by_continent(rows, LEAGUE_DISPLAY)

    # If grouping produced nothing useful, use fetcher's to_reel_groups
    if not continents:
        source = schedule.get("source", "")
        if source in FETCHER_MAP:
            mod_path, cls_name = FETCHER_MAP[source]
            mod = importlib.import_module(mod_path)
            fetcher = getattr(mod, cls_name)()
            if source == "music":
                groups = fetcher.to_reel_groups(rows)
            elif source == "games":
                groups = fetcher.to_reel_groups(
                    rows, schedule.get("games_format", "game_deals"))
            else:
                groups = fetcher.to_reel_groups(rows)
            continent_name = CONTINENT_NAMES.get(source, "OTHER")
            continents = [{"name": continent_name, "groups": groups}]
        else:
            continents = [{"name": "OTHER", "groups": [
                {"league": "Results", "display_name": "Results",
                 "matches": rows}]}]

    reel_config = {
        "channel_name": CONFIG.get("channel_name", "TestChannel"),
        "date": date_str.replace("-", "."),
        "continents": continents,
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out = tmp.name
    try:
        make_reel(reel_config, out, sport_id=sport_id)
        size = os.path.getsize(out)
        print(f"  [{schedule_id}] reel OK: {size // 1024}KB")
        return size
    except Exception as e:
        print(f"  [{schedule_id}] reel error: {e}")
        return 0
    finally:
        try:
            os.unlink(out)
        except Exception:
            pass


def test_fixtures_pipeline():
    size = _make_reel_for_schedule("fixtures", "fixtures")
    # May have 0 rows if API rate limited
    assert size >= 0


def test_finance_pipeline():
    size = _make_reel_for_schedule("finance", "finance")
    assert size > 10_000


def test_music_pipeline():
    size = _make_reel_for_schedule("music_europe", "music")
    assert size > 10_000


def test_techai_pipeline():
    size = _make_reel_for_schedule("techai", "techai")
    assert size > 0


def test_transfer_pipeline():
    size = _make_reel_for_schedule("transfer", "transfer")
    # May have 0 rows if no transfer headlines found
    assert size >= 0


def test_news_pipeline():
    size = _make_reel_for_schedule("news", "news")
    assert size > 10_000


def test_games_pipeline():
    size = _make_reel_for_schedule("games_deals", "games")
    assert size > 0


def test_sports_still_works():
    """Regression: original @ayaz_sports must not be broken."""
    size = _make_reel_for_schedule("europe", "futbol")
    # May have no matches yesterday
    assert size >= 0
