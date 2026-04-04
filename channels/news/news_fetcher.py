"""
@ayaz_news — World news fetcher.
Uses RSS feeds for collection, Claude API for curation.
Falls back to raw RSS if ANTHROPIC_API_KEY is not set.
"""

import os
import sys
import json
import time
from typing import List, Dict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

try:
    import feedparser
except ImportError:
    raise ImportError("pip install feedparser")

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("pip install anthropic")

RSS_SOURCES = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.theguardian.com/world/rss",
    "https://techcrunch.com/feed/",
]

SOURCE_GEO = {
    "BBC":          ("EUROPE",   "\U0001f1ec\U0001f1e7 UK"),
    "BBC News":     ("EUROPE",   "\U0001f1ec\U0001f1e7 UK"),
    "Reuters":      ("EUROPE",   "\U0001f1ec\U0001f1e7 UK"),
    "The Guardian": ("EUROPE",   "\U0001f1ec\U0001f1e7 UK"),
    "TechCrunch":   ("AMERICAS", "\U0001f1fa\U0001f1f8 USA"),
    "AP News":      ("GLOBAL",   "\U0001f30d Global"),
    "Al Jazeera":   ("GLOBAL",   "\U0001f30d Global"),
}

CATEGORY_EMOJI = {
    "POLITICS":   "🌍",
    "TECHNOLOGY": "💻",
    "ECONOMY":    "📈",
    "SCIENCE":    "🔬",
    "HEALTH":     "🏥",
    "CLIMATE":    "🌱",
    "CONFLICT":   "⚠️",
    "CULTURE":    "🎭",
}

SYSTEM_PROMPT = """You are a world news editor for @ayaz_news YouTube Shorts.
Select today's most important global news stories.
Always respond with valid JSON array only. No markdown. No preamble.
Be strictly factual and neutral."""

USER_TEMPLATE = """Select the 8 most important world news stories from today.

Return a JSON array:
[
  {{
    "category": "POLITICS",
    "emoji": "🌍",
    "line1": "max 50 chars clear headline",
    "line2": "max 50 chars context",
    "region": "EU / US / ASIA / GLOBAL / MIDEAST",
    "importance": 8
  }}
]

Rules: max 8 items, at least 4 categories, at least 3 regions, order by importance.

News items:
{news_json}"""


class NewsFetcher(BaseFetcher):
    channel_id = "news"
    sport_id   = "news"

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            if os.path.exists(env):
                for line in open(env):
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
        self.client = Anthropic(api_key=api_key) if api_key else None

    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        cache_key = f"news_{date_from}"
        if date_from < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        raw = self._collect_rss()
        if not raw:
            return []

        if self.client:
            processed = self._process_with_claude(raw)
        else:
            processed = self._fallback_process(raw)

        rows = self._to_rows(processed)
        if date_from < today:
            self._save_cache(cache_key, rows)
        return rows

    def _collect_rss(self) -> List[Dict]:
        items = []
        for url in RSS_SOURCES:
            try:
                feed = feedparser.parse(url)
                source = feed.feed.get("title", "")[:30]
                for entry in feed.entries[:12]:
                    items.append({
                        "title":   entry.get("title", "")[:150],
                        "summary": entry.get("summary", "")[:200],
                        "source":  source,
                    })
                time.sleep(0.4)
            except Exception as e:
                print(f"[news] RSS error {url}: {e}")
        return items[:50]

    def _process_with_claude(self, items: List[Dict]) -> List[Dict]:
        news_json = json.dumps(items[:40], ensure_ascii=False)
        try:
            resp = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user",
                           "content": USER_TEMPLATE.format(news_json=news_json)}],
            )
            raw = resp.content[0].text.strip()
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception as e:
            print(f"[news] Claude error: {e}")
            return self._fallback_process(items)

    def _fallback_process(self, items: List[Dict]) -> List[Dict]:
        categories = list(CATEGORY_EMOJI.keys())
        result = []
        for i, item in enumerate(items[:8]):
            result.append({
                "category":   categories[i % len(categories)],
                "emoji":      list(CATEGORY_EMOJI.values())[i % len(CATEGORY_EMOJI)],
                "line1":      item["title"][:50],
                "line2":      (item.get("summary") or item["source"])[:80],
                "source":     item["source"],
                "region":     "GLOBAL",
                "importance": 5,
            })
        return result

    def _to_rows(self, processed: List[Dict]) -> List[Dict]:
        rows = []
        for i, item in enumerate(processed):
            cat   = item.get("category", "POLITICS")
            emoji = item.get("emoji", CATEGORY_EMOJI.get(cat, "\U0001f4f0"))
            source = item.get("source", "")
            # Geo lookup from source
            geo = None
            for src_key, geo_val in SOURCE_GEO.items():
                if src_key.lower() in source.lower():
                    geo = geo_val
                    break
            continent = (geo[0] if geo else
                        item.get("region", "GLOBAL"))
            country = geo[1] if geo else "\U0001f30d Global"

            rows.append({
                "id":        f"news-{i}-{cat}",
                "home":      f"{emoji} {cat}",
                "score":     "",
                "away":      item.get("line1", "")[:50],
                "league":    cat,
                "category":  country,
                "continent": continent,
                "time":      item.get("line2", "")[:80],
                "status":    "TODAY",
            })
        return rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        cat_map: dict = {}
        for item in items:
            cat = item["league"]
            cat_map.setdefault(cat, []).append(item)

        groups = []
        for cat in CATEGORY_EMOJI:
            if cat in cat_map:
                groups.append({
                    "league":       cat,
                    "display_name": cat,
                    "continent":    "NEWS",
                    "matches":      cat_map[cat],
                })
        return groups
