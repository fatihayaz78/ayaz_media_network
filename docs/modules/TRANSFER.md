# modules/TRANSFER.md — @ayaz_transfer
> Updated: Sprint 3 (April 2026)

## Status: ✅ Built (RSS+Claude — no confirmed-deals API)
Fetcher: channels/transfer/transfer_fetcher.py | Theme: transfer (orange)
API: RSS feeds + Claude API (TransferMarkt removed — both endpoints returned 404)
Schedule: Daily 09:00 UTC
Tests: tests/channels/test_transfer.py — 6 passed ✅

## Data Layers
Layer 1 (BROKEN): TransferMarkt via RapidAPI — both endpoints return 404
  /v1/transfers/list → 404
  /v1/transfers/search → 404
  → Current plan doesn't include this endpoint
  → Fix: upgrade plan OR use football-data.org OR use transfermarkt-scraper

Layer 2 (RSS): Sky Sports, BBC Sport, Goal.com
  Without Claude: keyword filter ("transfer","sign","join","move","deal","fee","bid")
  With Claude: extracts player/clubs/fee from any football headline

## Column Mapping
DONE DEALS: home=player, score=fee(€180M), away="ClubA→ClubB", status="✓ DONE", league="DONE DEALS"
RUMOURS:    home=player, score=fee_estimate, away="ClubA→ClubB", status=⭐⭐⭐(reliability), league="HOT RUMOURS"

## Reliability Stars
⭐⭐⭐⭐⭐ = Fabrizio Romano
⭐⭐⭐⭐  = Sky Sports, BBC
⭐⭐⭐   = Goal.com, other major outlets

## Claude Prompt (extract from RSS)
System: "You are a football transfer news analyst. Extract transfer information. Always respond with valid JSON array only."
Output: [{is_transfer, type, player, from_club, to_club, fee, source, headline}]

## Phase 6 Resolution
Option A: football-data.org — no transfers endpoint in free tier ❌
Option B: transfermarkt-scraper — package not stable ❌
Option C: RSS+Claude only ✅ — _fetch_confirmed() returns []
Hardcoded RAPIDAPI_KEY removed. All API keys via os.environ + .env
