"""
Abstract base class for all Ayaz Media Network channel fetchers.
All channel fetchers must extend this class.

Data contract:
  Every fetcher returns List[Dict] where each dict has:
    id       : str  — unique identifier (for deduplication)
    home     : str  — LEFT column in reel
    score    : str  — CENTER column (empty string if not applicable)
    away     : str  — RIGHT column (empty string if not applicable)
    league   : str  — group/league name
    category : str  — continent/section for grouping
    time     : str  — optional label (time, platform, etc.)
    status   : str  — badge text (FT, NEW, ▲, ▼, etc.)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):

    # Override in subclass
    channel_id: str = ""   # e.g. "fixtures", "finance", "music"
    sport_id:   str = ""   # maps to SPORT_IDENTITY key in video_maker.py

    # ── Cache helpers ─────────────────────────────────────────
    @property
    def cache_dir(self) -> str:
        base = os.path.join(os.path.dirname(__file__), "..", "cache", self.channel_id)
        os.makedirs(base, exist_ok=True)
        return base

    def _cache_path(self, key: str) -> str:
        safe = key.replace("/", "-").replace(":", "-")
        return os.path.join(self.cache_dir, f"{safe}.json")

    def _load_cache(self, key: str) -> Optional[List[Dict]]:
        path = self._cache_path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Cache read error {key}: {e}")
            return None

    def _save_cache(self, key: str, data: List[Dict]) -> None:
        try:
            with open(self._cache_path(key), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Cache write error {key}: {e}")

    # ── Abstract interface ────────────────────────────────────
    @abstractmethod
    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        """
        Fetch content for date range (YYYY-MM-DD format).
        Returns list of standard row dicts.
        Must implement caching for past dates.
        """
        pass

    @abstractmethod
    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        """
        Convert fetched items to reel group format consumed by video_maker.py.

        Returns:
        [
          {
            "league":       str,   # group header text
            "display_name": str,   # display name (can differ from league)
            "matches": [
              {
                "id":     str,
                "home":   str,   # left column
                "score":  str,   # center column (empty = wide row)
                "away":   str,   # right column
                "league": str,
                "status": str,
                "time":   str,
              }
            ]
          }
        ]
        """
        pass

    # ── Shared utilities ──────────────────────────────────────
    def deduplicate(self, rows: List[Dict]) -> List[Dict]:
        seen, unique = set(), []
        for r in rows:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)
        return unique
