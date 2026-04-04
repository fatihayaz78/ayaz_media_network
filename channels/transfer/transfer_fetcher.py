"""
@ayaz_transfer — Football transfer news fetcher.
Layer 1: Confirmed deals — no working API (TransferMarkt 404, football-data.org no endpoint).
Layer 2: Rumours via RSS feeds + Claude AI extraction.
"""

import os
import sys
import json
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

RSS_FEEDS = [
    "https://www.skysports.com/rss/12040",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.goal.com/feeds/en/news",
    "https://theathletic.com/rss/news/",
]

SOURCE_RELIABILITY = {
    "sky sports": 4, "skysports": 4,
    "bbc":        4, "bbc sport": 4,
    "goal":       3, "goal.com":  3,
    "fabrizio":   5, "romano":    5,
}

SYSTEM_PROMPT = """You are a football transfer news analyst.
Extract transfer information from news headlines.
Always respond with valid JSON array only. No markdown. No preamble."""

USER_TEMPLATE = """Extract football transfer information from these headlines.
For each headline return one JSON object:
- If it IS transfer news: {{"is_transfer": true, "type": "confirmed" or "rumour", "player": "Name", "from_club": "Club", "to_club": "Club", "fee": "€XXXm or Free or Loan or ?", "source": "source", "headline": "max 48 chars"}}
- If NOT transfer news: {{"is_transfer": false}}

Return a JSON array. One object per headline.

Headlines:
{headlines_json}"""


def _stars(source: str) -> str:
    s = source.lower()
    for key, val in SOURCE_RELIABILITY.items():
        if key in s:
            return "⭐" * val
    return "⭐⭐⭐"


class TransferFetcher(BaseFetcher):
    channel_id = "transfer"
    sport_id   = "transfer"

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
        cache_key = f"transfer_{date_from}"
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        if date_from < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        rows: List[Dict] = []
        rows.extend(self._fetch_confirmed(date_from, date_to))
        rows.extend(self._fetch_rumours())

        if date_from < today:
            self._save_cache(cache_key, rows)
        return rows

    def _fetch_confirmed(self, date_from: str, date_to: str) -> List[Dict]:
        """Confirmed transfers — no working free API available.
        TransferMarkt RapidAPI returns 404, football-data.org has no transfers endpoint.
        Returns [] and relies on RSS+Claude for all transfer data.
        """
        print("[transfer] No confirmed-deals API available. RSS+Claude only.")
        return []

    def _fetch_rumours(self) -> List[Dict]:
        """RSS feeds + Claude AI extraction."""
        raw_items = []
        for url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                source = feed.feed.get("title", url)
                for entry in feed.entries[:15]:
                    raw_items.append({
                        "headline": entry.get("title", "")[:150],
                        "source":   source,
                    })
                time.sleep(0.4)
            except Exception as e:
                print(f"[transfer] RSS error {url}: {e}")

        if not raw_items:
            return []

        if self.client:
            return self._extract_with_claude(raw_items)
        return self._fallback_rumours(raw_items)

    def _extract_with_claude(self, items: List[Dict]) -> List[Dict]:
        headlines = [{"headline": i["headline"], "source": i["source"]}
                     for i in items[:30]]
        try:
            resp = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user",
                           "content": USER_TEMPLATE.format(
                               headlines_json=json.dumps(headlines))}],
            )
            raw = resp.content[0].text.strip()
            clean = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
        except Exception as e:
            print(f"[transfer] Claude error: {e}")
            return self._fallback_rumours(items)

        rows = []
        for i, item in enumerate(parsed):
            if not item.get("is_transfer"):
                continue
            rows.append({
                "id":       f"tx-rumour-{i}",
                "home":     item.get("player", "?")[:22],
                "score":    item.get("fee", "?")[:12],
                "away":     f"{item.get('from_club', '?')[:10]} → {item.get('to_club', '?')[:10]}",
                "league":   "HOT RUMOURS",
                "category": "RUMOURS",
                "time":     item.get("headline", "")[:48],
                "status":   _stars(item.get("source", "")),
            })
        return rows[:8]

    def _fallback_rumours(self, items: List[Dict]) -> List[Dict]:
        rows = []
        for i, item in enumerate(items[:6]):
            hl = item["headline"]
            if not any(w in hl.lower() for w in
                       ["transfer", "sign", "join", "move", "deal", "fee", "bid",
                        "loan", "contract", "agree", "complete", "medical",
                        "swap", "release", "free agent", "extend"]):
                continue
            rows.append({
                "id":       f"tx-fallback-{i}",
                "home":     hl[:22],
                "score":    "?",
                "away":     item["source"][:22],
                "league":   "HOT RUMOURS",
                "category": "RUMOURS",
                "time":     hl[:48],
                "status":   _stars(item["source"]),
            })
        return rows[:6]

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        confirmed = [i for i in items if i["category"] == "CONFIRMED"]
        rumours   = [i for i in items if i["category"] == "RUMOURS"]
        groups = []
        if confirmed:
            groups.append({
                "league":       "DONE DEALS",
                "display_name": "Done Deals ✓",
                "matches":      confirmed,
            })
        if rumours:
            groups.append({
                "league":       "HOT RUMOURS",
                "display_name": "Hot Rumours 🔥",
                "matches":      rumours,
            })
        return groups
