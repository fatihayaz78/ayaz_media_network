"""
@ayaz_fixtures — Upcoming match schedule fetcher.
Same SportAPI as fetcher.py, filter reversed to upcoming events.
Groups by DATE (not by league) so output shows: MON · 07 Apr → matches.
"""

import os
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

RAPIDAPI_KEY  = os.environ.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "sportapi7.p.rapidapi.com"
BASE_URL      = "https://sportapi7.p.rapidapi.com/api/v1"

HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type":    "application/json",
}

SPORT_SLUGS = {
    "futbol":   "football",
    "basket":   "basketball",
    "amerikan": "american-football",
}

# Filter for upcoming (inverse of FINISHED_STATUSES in fetcher.py)
UPCOMING_STATUSES = {"not_started", "scheduled", "tbd", "postponed"}

LEAGUES_FILTER = [
    "Premier League",
    "Trendyol Süper Lig",
    "LaLiga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "VriendenLoterij Eredivisie",
    "UEFA Champions League, Knockout stage",
    "NBA",
]

DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


CACHE_TTL_HOURS = 6  # Fixtures valid for 6h (schedule doesn't change often)


class FixturesFetcher(BaseFetcher):
    channel_id = "fixtures"
    sport_id   = "fixtures"

    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        """Fetch upcoming matches for date range with aggressive caching."""
        # Cache-only mode: never hit API (for tests / quota protection)
        if os.environ.get("FIXTURES_CACHE_ONLY"):
            cache_key = f"fixtures_range_{date_from}_{date_to}"
            cached = self._load_cache(cache_key)
            print(f"[fixtures] Cache-only mode: {len(cached) if cached else 0} rows")
            return cached or []

        # Range-level cache with 6h TTL
        cache_key = f"fixtures_range_{date_from}_{date_to}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            age = self._cache_age_hours(cache_key)
            if age < CACHE_TTL_HOURS:
                print(f"[fixtures] Cache hit ({age:.1f}h old, {len(cached)} rows)")
                return cached

        # Fetch fresh data
        dates = self._get_dates(date_from, date_to)
        all_rows: List[Dict] = []

        for date in dates:
            rows = self._fetch_by_date(date)
            if rows is None:
                # API quota exhausted — stop burning requests
                break
            all_rows.extend(rows)

        result = self.deduplicate(all_rows)

        if result:
            self._save_cache(cache_key, result)
        elif cached is not None:
            print("[fixtures] API failed, using stale cache")
            return cached

        return result

    def _fetch_by_date(self, date: str) -> Optional[List[Dict]]:
        """Fetch upcoming matches for a single date with retry."""
        # Per-date cache for past dates
        per_date_key = f"fixtures_{date}"
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        if date < today:
            cached = self._load_cache(per_date_key)
            if cached is not None:
                return cached

        url = f"{BASE_URL}/sport/football/scheduled-events/{date}"

        for attempt in range(3):
            try:
                time.sleep(2)  # Conservative: 50 req/month quota
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code == 429:
                    msg = resp.json().get("message", "")
                    if "MONTHLY" in msg.upper():
                        print(f"[fixtures] Monthly quota exhausted — stopping")
                        return None  # Signal to stop all requests
                    wait = 2 ** attempt
                    print(f"[fixtures] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except requests.exceptions.HTTPError:
                print(f"[fixtures] HTTP error {date} (attempt {attempt+1})")
                if attempt == 2:
                    return []
            except Exception as e:
                print(f"[fixtures] fetch error {date}: {e}")
                return []
        else:
            return []

        rows = []
        for e in data.get("events", []):
            status_type = (e.get("status") or {}).get("type", "").lower()
            if status_type not in UPCOMING_STATUSES:
                continue

            home_team = (e.get("homeTeam") or {}).get("name", "")
            away_team = (e.get("awayTeam") or {}).get("name", "")
            if not home_team or not away_team:
                continue

            tournament    = e.get("tournament") or {}
            league_name   = tournament.get("name", "")
            category      = (tournament.get("category") or {}).get("name", "")

            if LEAGUES_FILTER:
                if league_name not in LEAGUES_FILTER:
                    continue

            ts = e.get("startTimestamp")
            kickoff = ""
            if ts:
                try:
                    kickoff = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M")
                except Exception:
                    pass

            rows.append({
                "id":       f"fix-{e.get('id', '')}",
                "home":     home_team,
                "score":    "vs",
                "away":     away_team,
                "league":   league_name,
                "category": category,
                "time":     league_name[:12],
                "status":   kickoff or "TBD",
                "date":     date,
            })

        if date < today:
            self._save_cache(per_date_key, rows)

        return rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        """
        Group by date — each date becomes one 'league' group.
        Output format matches video_maker.py expectations.
        """
        # Sort by date then by time
        items_sorted = sorted(items, key=lambda x: (x.get("date", ""), x.get("status", "")))

        # Group by date
        date_map: dict = {}
        for item in items_sorted:
            d = item.get("date", "")
            if d not in date_map:
                date_map[d] = []
            date_map[d].append(item)

        groups = []
        for date_str, matches in date_map.items():
            label = self._format_date_label(date_str)
            groups.append({
                "league":       label,
                "display_name": label,
                "matches":      matches,
            })

        return groups

    def _format_date_label(self, date_str: str) -> str:
        """'2026-04-07' → 'TUE · 07 Apr'"""
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            day = DAY_NAMES[d.weekday()]
            return f"{day} · {d.day:02d} {MONTH_NAMES[d.month-1]}"
        except Exception:
            return date_str

    def _get_dates(self, date_from: str, date_to: str) -> List[str]:
        try:
            a = datetime.strptime(date_from, "%Y-%m-%d")
            b = datetime.strptime(date_to,   "%Y-%m-%d")
        except ValueError:
            return [date_from[:10]]
        dates, cur = [], a
        while cur <= b:
            dates.append(cur.strftime("%Y-%m-%d"))
            cur += timedelta(days=1)
        return dates[:14]   # max 2 weeks
