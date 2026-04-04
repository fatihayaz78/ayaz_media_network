import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.games.games_fetcher import GamesFetcher


def test_steam_charts():
    f = GamesFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03", fmt="steam_charts")
    assert isinstance(rows, list)
    print(f"Steam: {len(rows)} games")


def test_game_deals():
    f = GamesFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03", fmt="game_deals")
    assert isinstance(rows, list)
    if rows:
        assert rows[0]["status"] == "SALE"
        assert rows[0]["score"].startswith("$")
    print(f"Deals: {len(rows)} games")


def test_new_releases():
    f = GamesFetcher()
    rows = f.fetch("2026-03-27", "2026-04-03", fmt="new_releases")
    assert len(rows) > 0
    print(f"Releases: {len(rows)} games")


def test_row_fields():
    f = GamesFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03", fmt="game_deals")
    if not rows:
        pytest.skip("CheapShark unreachable")
    for r in rows:
        assert all(k in r for k in ["id", "home", "score", "away", "league", "status"])


def test_reel_groups():
    f = GamesFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03", fmt="game_deals")
    if not rows:
        rows = f._sample_releases()
    groups = f.to_reel_groups(rows, fmt="game_deals")
    assert len(groups) > 0


def test_video_maker_renders_games():
    import tempfile
    from video_maker import make_reel

    f = GamesFetcher()
    rows = f.fetch("2026-04-03", "2026-04-03", fmt="game_deals")
    if not rows:
        rows = f._sample_releases()
    groups = f.to_reel_groups(rows, fmt="game_deals")
    config = {
        "channel_name": "ayaz_gamezs",
        "date": "03.04.2026",
        "continents": [{"name": "GAMING", "groups": groups}],
    }

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        out = tmp.name

    try:
        make_reel(config, out, sport_id="games")
        assert os.path.getsize(out) > 10_000
        print(f"games reel: {os.path.getsize(out) // 1024}KB")
    finally:
        os.unlink(out)
