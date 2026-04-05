# Fixtures Channel
YouTube: @ayaz_fixtures | Theme: fixtures | Continent split: YES (continent field)

## Data Source
SportAPI7 (same as sports) — QUOTA LIMITED (50 req/month)
Fetches upcoming matches for next 7 days.
6h cache TTL, stale cache fallback on API failure.

## Row Format
home="Team A" | score="vs" | away="Team B" | time="21:00" | status="MON 07 Apr"
Groups by date: "MON . 07 Apr" format

## Status
- API: QUOTA LIMITED (same 50/month as sports)
- Cache: WORKING (6h TTL)
- FIXTURES_CACHE_ONLY env var available
