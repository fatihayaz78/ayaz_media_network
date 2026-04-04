"""
@ayaz_musics — Music charts fetcher.
Uses Apple Music RSS (free, no API key needed).
Phase 9: per-country top 5 (not merged continent top 10).
"""

import os
import sys
import json
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

APPLE_BASE = "https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json"

COUNTRIES = {
    "EUROPE": [
        {"code": "gb", "name": "UK",          "flag": "\U0001f1ec\U0001f1e7", "weight": 25},
        {"code": "de", "name": "Germany",      "flag": "\U0001f1e9\U0001f1ea", "weight": 20},
        {"code": "fr", "name": "France",       "flag": "\U0001f1eb\U0001f1f7", "weight": 20},
        {"code": "es", "name": "Spain",        "flag": "\U0001f1ea\U0001f1f8", "weight": 15},
        {"code": "tr", "name": "Turkey",       "flag": "\U0001f1f9\U0001f1f7", "weight": 15},
        {"code": "it", "name": "Italy",        "flag": "\U0001f1ee\U0001f1f9", "weight": 15},
        {"code": "nl", "name": "Netherlands",  "flag": "\U0001f1f3\U0001f1f1", "weight": 10},
        {"code": "se", "name": "Sweden",       "flag": "\U0001f1f8\U0001f1ea", "weight": 10},
    ],
    "AMERICAS": [
        {"code": "us", "name": "USA",          "flag": "\U0001f1fa\U0001f1f8", "weight": 50},
        {"code": "br", "name": "Brazil",       "flag": "\U0001f1e7\U0001f1f7", "weight": 30},
        {"code": "mx", "name": "Mexico",       "flag": "\U0001f1f2\U0001f1fd", "weight": 20},
        {"code": "ar", "name": "Argentina",    "flag": "\U0001f1e6\U0001f1f7", "weight": 15},
        {"code": "cl", "name": "Chile",        "flag": "\U0001f1e8\U0001f1f1", "weight": 10},
    ],
    "ASIA": [
        {"code": "jp", "name": "Japan",        "flag": "\U0001f1ef\U0001f1f5", "weight": 40},
        {"code": "kr", "name": "South Korea",  "flag": "\U0001f1f0\U0001f1f7", "weight": 40},
        {"code": "in", "name": "India",        "flag": "\U0001f1ee\U0001f1f3", "weight": 20},
        {"code": "ph", "name": "Philippines",  "flag": "\U0001f1f5\U0001f1ed", "weight": 10},
        {"code": "id", "name": "Indonesia",    "flag": "\U0001f1ee\U0001f1e9", "weight": 10},
    ],
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
        """Fetch top 5 per country for a continent."""
        week = _week_key()
        cache_key = f"chart_{continent}_{week}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        countries = COUNTRIES.get(continent, COUNTRIES["EUROPE"])
        prev = self._load_prev(continent)

        rows = []
        for country in countries:
            cc   = country["code"]
            name = country["name"]
            flag = country["flag"]

            chart = self._fetch_country(cc)
            if not chart:
                continue

            # Take top 5 per country
            for i, item in enumerate(chart[:5]):
                rank = i + 1
                key  = f"{item['song']}::{item['artist']}"
                trend = self._calc_trend(key, rank, prev)
                weeks_str = self._calc_weeks(key, rank, continent)

                rows.append({
                    "id":        f"music-{continent}-{cc}-{rank}",
                    "home":      f"{rank} {trend}",
                    "score":     item["song"][:35],
                    "away":      item["artist"][:28],
                    "league":    f"{name} TOP 5",
                    "category":  f"{flag} {name}",
                    "continent": continent,
                    "time":      "",
                    "status":    weeks_str,
                })

            time.sleep(0.3)

        # Save prev for next week
        self._save_prev(continent, rows)
        self._save_cache(cache_key, rows)
        return rows

    def fetch_all(self) -> List[Dict]:
        """Fetch all continents at once. Returns rows with continent field."""
        all_rows = []
        for continent in COUNTRIES.keys():
            rows = self.fetch(continent=continent)
            all_rows.extend(rows)
        return all_rows

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
            return "\u2191"
        if current_rank > prev_rank:
            return "\u2193"
        return "\u25cf"

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

        # Group by league (per-country)
        by_league = defaultdict(list)
        for item in items:
            by_league[item["league"]].append(item)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        continent = items[0].get("continent", items[0].get("category", ""))

        groups = []
        for league, league_items in by_league.items():
            country_label = league_items[0].get("category", continent)
            groups.append({
                "league":       league,
                "display_name": f"{country_label} \u00b7 {league}",
                "continent":    continent,
                "matches":      league_items,
            })
        return groups
