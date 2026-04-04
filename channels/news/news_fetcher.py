"""
@ayaz_news — World news fetcher.
Phase 15B: Per-country RSS feeds, top 5 headlines per region.
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

# Per-country/region RSS feeds (BBC regional feeds are reliable and free)
COUNTRY_FEEDS = [
    {
        "country": "USA",
        "flag": "\U0001f1fa\U0001f1f8",
        "continent": "AMERICAS",
        "urls": ["https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"],
    },
    {
        "country": "UK",
        "flag": "\U0001f1ec\U0001f1e7",
        "continent": "EUROPE",
        "urls": ["https://feeds.bbci.co.uk/news/world/rss.xml"],
    },
    {
        "country": "Turkey",
        "flag": "\U0001f1f9\U0001f1f7",
        "continent": "EUROPE",
        "urls": ["https://feeds.bbci.co.uk/turkish/rss.xml"],
    },
    {
        "country": "China",
        "flag": "\U0001f1e8\U0001f1f3",
        "continent": "ASIA",
        "urls": ["https://feeds.bbci.co.uk/news/world/asia/rss.xml"],
    },
    {
        "country": "India",
        "flag": "\U0001f1ee\U0001f1f3",
        "continent": "ASIA",
        "urls": ["https://feeds.bbci.co.uk/news/world/south_asia/rss.xml"],
    },
    {
        "country": "Saudi Arabia",
        "flag": "\U0001f1f8\U0001f1e6",
        "continent": "MIDEAST",
        "urls": ["https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"],
    },
    {
        "country": "Germany",
        "flag": "\U0001f1e9\U0001f1ea",
        "continent": "EUROPE",
        "urls": ["https://feeds.bbci.co.uk/news/world/europe/rss.xml"],
    },
    {
        "country": "Brazil",
        "flag": "\U0001f1e7\U0001f1f7",
        "continent": "AMERICAS",
        "urls": ["https://feeds.bbci.co.uk/news/world/latin_america/rss.xml"],
    },
    {
        "country": "Japan",
        "flag": "\U0001f1ef\U0001f1f5",
        "continent": "ASIA",
        "urls": ["https://feeds.bbci.co.uk/news/world/asia/rss.xml"],
    },
    {
        "country": "France",
        "flag": "\U0001f1eb\U0001f1f7",
        "continent": "EUROPE",
        "urls": ["https://feeds.bbci.co.uk/news/world/europe/rss.xml"],
    },
]

MAX_PER_COUNTRY = 5


class NewsFetcher(BaseFetcher):
    channel_id = "news"
    sport_id   = "news"

    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        cache_key = f"news_{date_from}"
        if date_from < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        rows = self._fetch_all_countries()

        if date_from < today:
            self._save_cache(cache_key, rows)
        return rows

    def _fetch_all_countries(self) -> List[Dict]:
        """Fetch top 5 headlines per country/region from RSS."""
        all_rows = []
        seen_urls = set()  # avoid duplicate feeds (asia appears twice)

        for cf in COUNTRY_FEEDS:
            country  = cf["country"]
            flag     = cf["flag"]
            continent = cf["continent"]

            for url in cf["urls"]:
                if url in seen_urls:
                    # Re-use already fetched feed but still assign to this country
                    pass
                seen_urls.add(url)

                try:
                    feed = feedparser.parse(url)
                    entries = feed.entries[:10]
                except Exception as e:
                    print(f"[news] RSS error {country}: {e}")
                    continue

                count = 0
                for entry in entries:
                    if count >= MAX_PER_COUNTRY:
                        break
                    title = (entry.get("title") or "")[:120]
                    summary = (entry.get("summary") or entry.get("description") or "")[:120]
                    if not title:
                        continue

                    all_rows.append({
                        "id":        f"news-{country}-{count}",
                        "home":      title,
                        "score":     "",
                        "away":      summary,
                        "league":    f"{flag} {country}",
                        "category":  f"{flag} {country}",
                        "continent": continent,
                        "time":      "",
                        "status":    "TODAY",
                    })
                    count += 1

                time.sleep(0.3)

        print(f"[news] Total rows: {len(all_rows)}")
        return all_rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        from collections import defaultdict
        by_country = defaultdict(list)
        for item in items:
            by_country[item["league"]].append(item)

        # Maintain country order from COUNTRY_FEEDS
        order = [f"{cf['flag']} {cf['country']}" for cf in COUNTRY_FEEDS]
        groups = []
        for label in order:
            if label in by_country:
                groups.append({
                    "league":       label,
                    "display_name": label,
                    "continent":    "NEWS",
                    "matches":      by_country[label],
                })
        return groups
