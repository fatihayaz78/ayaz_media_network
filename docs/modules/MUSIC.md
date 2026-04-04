# modules/MUSIC.md — @ayaz_musics
> Updated: Sprint 9 (April 2026)

## Status: ✅ Built (Country-level)
Fetcher: channels/music/music_fetcher.py | Theme: music (violet)
API: Apple Music RSS (free, no key needed)
URL: https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json
Schedule: Every Friday — 3 reels at 08/09/10:00 UTC
Tests: tests/test_app_routes.py — music route passing ✅

## Countries & Flags (Phase 9 — per-country top 5)

### EUROPE (5 countries × 5 songs = 25 rows)
- 🇬🇧 UK (gb) — weight 30
- 🇩🇪 Germany (de) — weight 20
- 🇫🇷 France (fr) — weight 20
- 🇪🇸 Spain (es) — weight 15
- 🇹🇷 Turkey (tr) — weight 15

### AMERICAS (3 countries × 5 songs = 15 rows)
- 🇺🇸 USA (us) — weight 50
- 🇧🇷 Brazil (br) — weight 30
- 🇲🇽 Mexico (mx) — weight 20

### ASIA (3 countries × 5 songs = 15 rows)
- 🇯🇵 Japan (jp) — weight 40
- 🇰🇷 South Korea (kr) — weight 40
- 🇮🇳 India (in) — weight 20

## Fetch Method
- 1 API call per country (Apple Music RSS)
- Top 5 songs per country (not merged continent top 10)
- Each row has category=flag+country, continent=EUROPE/AMERICAS/ASIA

## Column Mapping
home=rank+trend("1 ↑"), score=song_title, away=artist, status=weeks_on_chart("3w"), league="UK TOP 5", category="🇬🇧 UK"

## Trend Logic
↑ = rank improved vs last week | ↓ = rank worse | ● = same | NEW = first appearance
Prev chart saved: cache/music/prev_{continent}.json (updated weekly)

## Known Issues
- Occasional country timeout (graceful degradation — works with partial data)
- All trends show "NEW" on first run (expected — prev cache empty)
