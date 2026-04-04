# modules/GAMES.md — @ayaz_gamezs
> Updated: Sprint 3+4 (April 2026)

## Status: ✅ Built (3 of 4 formats working)
Fetcher: channels/games/games_fetcher.py | Theme: games (purple)
Tests: tests/channels/test_games.py — 6 passed ✅

## 4 Formats

### steam_charts (Thursday 10:00 UTC)
API: store.steampowered.com (free, no key)
Content: Top sellers → concurrent players per game
Column: home="#1 Counter-Strike 2", score="183K", away="players", status="PEAK"
Fix applied: _is_real_game() filters promo/DLC/upgrade items

### esports (Daily 08:00 UTC) — ⚠️ needs PANDASCORE_KEY
API: api.pandascore.co (free tier: 100 req/day)
Games: cs2, league-of-legends, valorant, dota-2
Column: home=team_a, score="3–1", away=team_b, status="FT", league="CS2"
Env: PANDASCORE_KEY

### new_releases (Tuesday 10:00 UTC) — ⚠️ needs RAWG_KEY
API: api.rawg.io (free tier: RAWG_KEY)
Column: home=game_name, score=metacritic("92"), away=platforms("PC/PS5"), status="NEW"
Fallback: sample data (Hades II, Elden Ring DLC) when no key

### game_deals (Daily 12:00 UTC)
API: cheapshark.com/api (free, no key, no SSL issues)
Column: home=game_title, score=sale_price("$11.99"), away=discount("-80%"), status="SALE"
Fix applied: sale==0.0 skipped (free giveaways filtered out)

## Known Issues
- PandaScore: requires PANDASCORE_KEY env var
- RAWG: requires RAWG_KEY env var
- Steam: player count API may return 0 for some appids
