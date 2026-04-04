"""
@ayaz_musics — Music charts fetcher.
Uses Apple Music RSS (free, no API key needed).
Aggregates weighted charts across countries per continent.
"""

import os
import sys
import json
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

APPLE_BASE = "https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json"

CONTINENTS = {
    "EUROPE":   {"gb": 30, "de": 20, "fr": 20, "es": 15, "tr": 15},
    "AMERICAS": {"us": 50, "br": 30, "mx": 20},
    "ASIA":     {"jp": 50, "kr": 50},
    "TURKEY":   {"tr": 100},
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _week_key() -> str:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    week = now.isocalendar()[1]
    return f"{now.year}_W{week:02d}"


class MusicFetcher(BaseFetcher):
    channel_id = "music"
    sport_id   = "music"

    def fetch(self, date_from: str = "", date_to: str = "",
              continent: str = "EUROPE") -> List[Dict]:
        """Fetch and aggregate chart for one continent."""
        week = _week_key()
        cache_key = f"chart_{continent}_{week}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        weights = CONTINENTS.get(continent, {"gb": 100})
        prev    = self._load_prev(continent)

        # Fetch each country
        country_charts: dict = {}
        for cc, weight in weights.items():
            chart = self._fetch_country(cc)
            if chart:
                country_charts[cc] = (chart, weight)
            time.sleep(0.3)

        if not country_charts:
            return []

        # Weighted aggregation
        scores: dict = {}
        for cc, (chart, weight) in country_charts.items():
            for item in chart:
                key = f"{item['song']}::{item['artist']}"
                if key not in scores:
                    scores[key] = {
                        "song":   item["song"],
                        "artist": item["artist"],
                        "score":  0,
                    }
                rank_pts = (11 - item["rank"]) * weight
                scores[key]["score"] += rank_pts

        merged = sorted(scores.values(), key=lambda x: x["score"], reverse=True)

        # Build rows with trend
        rows = []
        for i, entry in enumerate(merged[:10]):
            rank = i + 1
            key  = f"{entry['song']}::{entry['artist']}"
            trend = self._calc_trend(key, rank, prev)
            weeks_str = self._calc_weeks(key, rank, continent)

            rows.append({
                "id":       f"music-{continent}-{rank}",
                "home":     f"{rank} {trend}",
                "score":    entry["song"][:35],
                "away":     entry["artist"][:28],
                "league":   f"{continent} TOP 10",
                "category": continent,
                "time":     "",
                "status":   weeks_str,
            })

        # Save prev for next week
        self._save_prev(continent, rows)
        self._save_cache(cache_key, rows)
        return rows

    def _fetch_country(self, cc: str) -> List[Dict]:
        """Fetch Apple Music top 10 for one country."""
        url = APPLE_BASE.format(cc=cc)
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            feed = resp.json().get("feed", {}).get("results", [])
            return [{"rank": i + 1, "song": item["name"],
                     "artist": item["artistName"]}
                    for i, item in enumerate(feed)]
        except Exception as e:
            print(f"[music] {cc} error: {e}")
            return []

    def _calc_trend(self, key: str, current_rank: int,
                    prev: List[Dict]) -> str:
        if not prev:
            return "NEW"
        prev_entry = next(
            (x for x in prev
             if f"{x.get('score', '')}::{x.get('away', '')}" == key),
            None
        )
        if not prev_entry:
            return "NEW"
        prev_rank = int(prev_entry["home"].split()[0])
        if current_rank < prev_rank:
            return "↑"
        if current_rank > prev_rank:
            return "↓"
        return "●"

    def _calc_weeks(self, key: str, rank: int, continent: str) -> str:
        history_key = f"history_{continent}"
        history = self._load_cache(history_key) or {}
        count = history.get(key, 0) + 1
        history[key] = count
        self._save_cache(history_key, history)
        return f"{count}w"

    def _prev_path(self, continent: str) -> str:
        return os.path.join(self.cache_dir, f"prev_{continent}.json")

    def _load_prev(self, continent: str) -> List[Dict]:
        path = self._prev_path(continent)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_prev(self, continent: str, rows: List[Dict]):
        with open(self._prev_path(continent), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        if not items:
            return []
        continent = items[0]["category"]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        display = f"{continent} Charts · {MONTH_NAMES[now.month - 1]} {now.year}"
        return [{
            "league":       f"{continent} TOP 10",
            "display_name": display,
            "matches":      items,
        }]
