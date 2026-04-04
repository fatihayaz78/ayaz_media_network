# modules/NEWS.md — @ayaz_news
> Updated: Sprint 3 (April 2026)

## Status: ✅ Built
Fetcher: channels/news/news_fetcher.py | Theme: news (indigo)
API: RSS feeds + Anthropic Claude API (ANTHROPIC_API_KEY)
Model: claude-haiku-4-5-20251001
Schedule: Daily 06:00 UTC
Tests: tests/channels/test_news.py — 6 passed ✅

## RSS Sources
BBC World: feeds.bbci.co.uk/news/world/rss.xml
Reuters:   feeds.reuters.com/reuters/worldNews
Guardian:  theguardian.com/world/rss
TechCrunch: techcrunch.com/feed/

## Categories
POLITICS | TECHNOLOGY | ECONOMY | SCIENCE | HEALTH | CLIMATE | CONFLICT | CULTURE

## Column Mapping (Wide Row Mode — score="")
home=emoji+category("🌍 POLITICS"), score="" (wide mode), away=headline, time=detail/context, status="TODAY"

## Claude Prompt Rules
- Max 8 items, at least 4 categories, at least 3 regions
- Order by importance descending
- Strictly factual, neutral tone

## Fallback
Without API key: round-robin categories, raw RSS titles as headlines.
With key: proper categorization, concise summaries, diversity enforcement.

## Reel Size
~556KB for 8 wide-row stories
