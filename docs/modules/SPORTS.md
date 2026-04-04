# modules/SPORTS.md — @ayaz_sports & @ayaz_fixtures
> Updated: Sprint 1 (April 2026)

## @ayaz_sports ✅ Production
Fetcher: `fetcher.py` | Theme: futbol/basket/amerikan/motor
API: SportAPI7 (RAPIDAPI_KEY from .env)
Endpoint: GET /api/v1/sport/{sport}/scheduled-events/{date}
Rate: 50 req/month (BASIC plan), 2s between calls

Sports: futbol→football | basket→basketball | amerikan→american-football | motor→motorsport
Schedules: europe(22:00), americas(06:00), global(Mon 10:00), asiapac(disabled)
Column: home=team, score="3–1", away=team, status=FT/AET, time=kickoff

## @ayaz_fixtures ✅ Built
Fetcher: channels/fixtures/fixtures_fetcher.py | Theme: fixtures (green)
Same API as sports — filter reversed to upcoming (not_started/scheduled)
Groups by DATE not league: "TUE · 07 Apr"
Column: home=team, score="vs", away=team, status=kickoff_time, time=short_league
Schedule: Monday 07:00 UTC, fetches next 7 days
Tests: tests/channels/test_fixtures.py — 5 passed ✅

## Known Issues
- ~~RAPIDAPI_KEY hardcoded~~ — moved to .env (Sprint 6)
- 50 req/month BASIC plan — fixtures uses 6h cache + stale fallback (Sprint 8)
- FIXTURES_CACHE_ONLY=1 env var available for test runs
