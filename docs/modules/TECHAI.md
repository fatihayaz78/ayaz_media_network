# modules/TECHAI.md — @ayaz_techai
> Updated: Sprint 2 (April 2026)

## Status: ✅ Built
Fetcher: channels/techai/techai_fetcher.py | Theme: techai (sky blue)
API: RSS feeds + Anthropic Claude API (ANTHROPIC_API_KEY)
Model: claude-haiku-4-5-20251001 (~$0.004/call, ~$0.03/week)
Schedule: Monday, Wednesday, Friday 08:00 UTC
Tests: tests/channels/test_techai.py — 6 passed ✅

## RSS Sources
model_news: techcrunch.com, theverge.com/ai, venturebeat.com/ai
research:   export.arxiv.org/rss/cs.AI

## Categories
MODEL_UPDATE | BIG_TECH | TOOLS | FUNDING | RESEARCH | REGULATION

## Column Mapping (Wide Row Mode — score="")
home=emoji+company("🤖 Anthropic"), score="" (triggers wide mode), away=headline(line1), time=detail(line2), status="NEW"

## Claude System Prompt (exact — do not change)
"You are a news editor for @ayaz_techai YouTube Shorts channel. Extract the most important AI and tech news this week. Always respond with valid JSON array only. No markdown. No preamble. Max line length: 50 characters per line."

## Fallback
Without ANTHROPIC_API_KEY: uses raw RSS titles, all categorized as BIG_TECH.
With key: proper categories, concise headlines, importance ranking.

## Wide Row Rendering
score=="" → video_maker.py renders: label(home, small muted) + headline(away, bold) + detail(time, dim)

## Cost Estimate
~4,000 input tokens + ~500 output tokens per call
claude-haiku-4-5-20251001 pricing: ~$0.004/call
Weekly (3 calls): ~$0.012 | Monthly: ~$0.05
