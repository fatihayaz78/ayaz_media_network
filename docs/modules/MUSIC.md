# modules/MUSIC.md — @ayaz_musics
> Updated: Sprint 2 (April 2026)

## Status: ✅ Built
Fetcher: channels/music/music_fetcher.py | Theme: music (violet)
API: Apple Music RSS (free, no key needed)
URL: https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json
Schedule: Every Friday — 4 reels at 08/09/10/11:00 UTC
Tests: tests/channels/test_music.py — 5 passed ✅

## Continents & Weights
EUROPE:   gb=30%, de=20%, fr=20%, es=15%, tr=15%
AMERICAS: us=50%, br=30%, mx=20%
ASIA:     jp=50%, kr=50%
TURKEY:   tr=100% (separate reel)

## Aggregation
Score = (11 - rank) × weight. Merge all countries, sort descending, take top 10.

## Column Mapping
home=rank+trend("1 ↑"), score=song_title, away=artist, status=weeks_on_chart("3w"), league="EUROPE TOP 10"

## Trend Logic
↑ = rank improved vs last week | ↓ = rank worse | ● = same | NEW = first appearance
Prev chart saved: cache/music/prev_{continent}.json (updated weekly)

## Known Issues
- gb/us/br endpoints occasionally timeout (graceful degradation — works with partial data)
- All trends show "NEW" on first run (expected — prev cache empty)
- Spotify Charts not integrated yet (optional backup source)
