"""
@ayaz_techai — AI & Tech news fetcher.
Uses RSS feeds for collection, Claude API for curation.
Falls back to raw RSS if ANTHROPIC_API_KEY is not set.
"""

import os
import sys
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

try:
    import feedparser
except ImportError:
    raise ImportError("Run: pip install feedparser")

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("Run: pip install anthropic")

RSS_SOURCES = {
    "model_news": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://venturebeat.com/ai/feed/",
    ],
    "research": [
        "https://export.arxiv.org/rss/cs.AI",
    ],
}

CATEGORY_DISPLAY = {
    "MODEL_UPDATE": "MODEL UPDATES",
    "BIG_TECH":     "BIG TECH",
    "TOOLS":        "TOOLS",
    "FUNDING":      "FUNDING",
    "RESEARCH":     "RESEARCH",
    "REGULATION":   "REGULATION",
}

SYSTEM_PROMPT = """You are a news editor for @ayaz_techai YouTube Shorts channel.
Extract the most important AI and tech news this week.
Always respond with valid JSON array only. No markdown. No preamble.
Max line length: 50 characters per line."""

USER_TEMPLATE = """Analyze these AI and tech news items.
Select the 8 most important ones.

Return a JSON array only:
[
  {{
    "category": "MODEL_UPDATE",
    "emoji": "🤖",
    "line1": "max 48 chars headline",
    "line2": "max 48 chars detail",
    "company": "Anthropic",
    "importance": 9
  }}
]

Categories: MODEL_UPDATE / BIG_TECH / TOOLS / FUNDING / RESEARCH / REGULATION
Order by importance descending. Max 8 items.

News items:
{news_json}"""


class TechAIFetcher(BaseFetcher):
    channel_id = "techai"
    sport_id   = "techai"

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            break
        self.client = Anthropic(api_key=api_key) if api_key else None

    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        week = now.isocalendar()[1]
        year = now.year
        cache_key = f"techai_{year}_W{week:02d}"

        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        raw_items = self._collect_rss()
        if not raw_items:
            return []

        if self.client:
            processed = self._process_with_claude(raw_items)
        else:
            processed = self._fallback_process(raw_items)

        rows = self._to_rows(processed)
        self._save_cache(cache_key, rows)
        return rows

    def _collect_rss(self) -> List[Dict]:
        items = []
        for category, urls in RSS_SOURCES.items():
            for url in urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:15]:
                        items.append({
                            "title":   entry.get("title", "")[:150],
                            "summary": entry.get("summary", "")[:300],
                            "source":  feed.feed.get("title", url)[:40],
                        })
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[techai] RSS error {url}: {e}")

        return items[:50]

    def _process_with_claude(self, items: List[Dict]) -> List[Dict]:
        news_json = json.dumps(items[:40], ensure_ascii=False)
        try:
            resp = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": USER_TEMPLATE.format(news_json=news_json),
                }],
            )
            raw = resp.content[0].text.strip()
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            print(f"[techai] Claude error: {e}")
            return self._fallback_process(items)

    def _fallback_process(self, items: List[Dict]) -> List[Dict]:
        """Use first 8 items without AI processing."""
        result = []
        for i, item in enumerate(items[:8]):
            result.append({
                "category":   "BIG_TECH",
                "emoji":      "📰",
                "line1":      item["title"][:48],
                "line2":      item["source"][:48],
                "company":    item["source"][:20],
                "importance": 5,
            })
        return result

    def _to_rows(self, processed: List[Dict]) -> List[Dict]:
        rows = []
        for i, item in enumerate(processed):
            cat = item.get("category", "BIG_TECH")
            rows.append({
                "id":       f"techai-{i}-{item.get('company', '')[:10]}",
                "home":     f"{item.get('emoji', '📰')} {item.get('company', 'AI')}",
                "score":    "",
                "away":     item.get("line1", "")[:48],
                "league":   CATEGORY_DISPLAY.get(cat, cat),
                "category": cat,
                "time":     item.get("line2", "")[:48],
                "status":   "NEW",
            })
        return rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        cat_map: dict = {}
        for item in items:
            cat = CATEGORY_DISPLAY.get(item["category"], item["category"])
            cat_map.setdefault(cat, []).append(item)

        groups = []
        for display in CATEGORY_DISPLAY.values():
            if display in cat_map:
                groups.append({
                    "league":       display,
                    "display_name": display,
                    "matches":      cat_map[display],
                })
        return groups
