"""
@ayaz_gamezs — Gaming & esports fetcher.
4 formats: steam_charts, esports, new_releases, game_deals.
Uses Steam API, PandaScore, RAWG, and CheapShark.
"""

import os
import sys
import json
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

PANDASCORE_KEY = os.environ.get("PANDASCORE_KEY", "")

STEAM_CHARTS_URL = "https://store.steampowered.com/api/featuredcategories/"
CHEAPSHARK_URL   = "https://www.cheapshark.com/api/1.0/deals"

ESPORTS_GAMES = {
    "cs2":               "CS2",
    "league-of-legends": "LoL",
    "valorant":          "Valorant",
    "dota-2":            "Dota 2",
}

RAWG_KEY = os.environ.get("RAWG_KEY", "")


class GamesFetcher(BaseFetcher):
    channel_id = "games"
    sport_id   = "games"

    def fetch(self, date_from: str, date_to: str,
              fmt: str = "steam_charts") -> List[Dict]:
        cache_key = f"games_{fmt}_{date_from}"
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        if date_from < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        if fmt == "steam_charts":
            rows = self._fetch_steam()
        elif fmt == "esports":
            rows = self._fetch_esports(date_from)
        elif fmt == "new_releases":
            rows = self._fetch_releases(date_from, date_to)
        elif fmt == "game_deals":
            rows = self._fetch_deals()
        else:
            rows = []

        if date_from < today:
            self._save_cache(cache_key, rows)
        return rows

    # ── Steam Charts ─────────────────────────────────────────────
    def _fetch_steam(self) -> List[Dict]:
        """Top sellers from Steam store API."""
        try:
            resp = requests.get(STEAM_CHARTS_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            top = data.get("top_sellers", {}).get("items", [])
        except Exception as e:
            print(f"[games] Steam error: {e}")
            return []

        rows = []
        rank = 0
        for game in top[:15]:
            name = game.get("name", "")[:28]
            if not self._is_real_game(name):
                continue
            rank += 1
            if rank > 10:
                break
            players = self._get_players(game.get("id", 0))
            rows.append({
                "id":       f"steam-{game.get('id', rank)}",
                "home":     f"#{rank} {name}",
                "score":    self._fmt_players(players),
                "away":     "players",
                "league":   "STEAM TOP 10",
                "category": "CHARTS",
                "time":     "",
                "status":   "PEAK",
            })
        return rows

    def _is_real_game(self, name: str) -> bool:
        skip_keywords = ["upgrade", "dlc", "pack", "bundle",
                         "edition", "soundtrack", "artbook", "pass"]
        name_lower = name.lower()
        return not any(kw in name_lower for kw in skip_keywords)

    def _get_players(self, appid: int) -> int:
        if not appid:
            return 0
        try:
            url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            resp = requests.get(url, params={"appid": appid}, timeout=5)
            return resp.json().get("response", {}).get("player_count", 0)
        except Exception:
            return 0

    def _fmt_players(self, n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n / 1_000:.0f}K"
        return str(n) if n > 0 else "N/A"

    # ── Esports ───────────────────────────────────────────────────
    def _fetch_esports(self, date: str) -> List[Dict]:
        if not PANDASCORE_KEY:
            print("[games] PANDASCORE_KEY not set — skipping esports")
            return []

        rows = []
        headers = {"Authorization": f"Bearer {PANDASCORE_KEY}"}

        for game_slug, game_label in ESPORTS_GAMES.items():
            try:
                url = f"https://api.pandascore.co/{game_slug}/matches/past"
                resp = requests.get(url, headers=headers, timeout=10,
                                    params={"per_page": 5, "sort": "-end_at"})
                if resp.status_code == 401:
                    print("[games] PandaScore auth error")
                    break
                resp.raise_for_status()
                matches = resp.json()
            except Exception as e:
                print(f"[games] PandaScore {game_slug}: {e}")
                continue

            for m in matches[:4]:
                opponents = m.get("opponents", [])
                if len(opponents) < 2:
                    continue
                team_a = opponents[0].get("opponent", {}).get("name", "?")[:16]
                team_b = opponents[1].get("opponent", {}).get("name", "?")[:16]

                results = m.get("results", [])
                score_a = results[0].get("score", 0) if len(results) > 0 else 0
                score_b = results[1].get("score", 0) if len(results) > 1 else 0

                rows.append({
                    "id":       f"esports-{m.get('id', 0)}",
                    "home":     team_a,
                    "score":    f"{score_a} – {score_b}",
                    "away":     team_b,
                    "league":   game_label,
                    "category": "ESPORTS",
                    "time":     "",
                    "status":   "FT",
                })
            time.sleep(0.5)

        return rows

    # ── New Releases ──────────────────────────────────────────────
    def _fetch_releases(self, date_from: str, date_to: str) -> List[Dict]:
        """RAWG.io — free game database API."""
        if not RAWG_KEY:
            return self._sample_releases()

        try:
            url = "https://api.rawg.io/api/games"
            resp = requests.get(url, params={
                "key":       RAWG_KEY,
                "dates":     f"{date_from},{date_to}",
                "ordering":  "-metacritic",
                "page_size": 8,
                "metacritic": "60,100",
            }, timeout=10)
            resp.raise_for_status()
            games = resp.json().get("results", [])
        except Exception as e:
            print(f"[games] RAWG error: {e}")
            return self._sample_releases()

        rows = []
        for i, g in enumerate(games[:8]):
            platforms = ", ".join(
                p["platform"]["name"][:6]
                for p in (g.get("platforms") or [])[:3]
            )
            rows.append({
                "id":       f"release-{g.get('id', i)}",
                "home":     g.get("name", "?")[:28],
                "score":    str(g.get("metacritic", "")) or "TBD",
                "away":     platforms or "Multi",
                "league":   "NEW RELEASES",
                "category": "RELEASES",
                "time":     g.get("released", ""),
                "status":   "NEW",
            })
        return rows

    def _sample_releases(self) -> List[Dict]:
        """Fallback sample data when no RAWG key."""
        return [
            {"id": "rel-1", "home": "Hades II", "score": "92",
             "away": "PC", "league": "NEW RELEASES", "category": "RELEASES",
             "time": "2026-04-01", "status": "NEW"},
            {"id": "rel-2", "home": "Elden Ring DLC", "score": "88",
             "away": "Multi", "league": "NEW RELEASES", "category": "RELEASES",
             "time": "2026-04-03", "status": "NEW"},
        ]

    # ── Game Deals ────────────────────────────────────────────────
    def _fetch_deals(self) -> List[Dict]:
        try:
            resp = requests.get(CHEAPSHARK_URL, params={
                "sortBy":   "savings",
                "pageSize": 8,
                "onSale":   1,
            }, timeout=10)
            resp.raise_for_status()
            deals = resp.json()
        except Exception as e:
            print(f"[games] CheapShark error: {e}")
            return []

        rows = []
        for i, d in enumerate(deals[:10]):
            title   = d.get("title", "?")[:28]
            normal  = float(d.get("normalPrice", "0"))
            sale    = float(d.get("salePrice", "0"))
            savings = round(float(d.get("savings", "0")))
            if sale == 0.0:
                continue
            if len(rows) >= 5:
                break
            rows.append({
                "id":       f"deal-{d.get('gameID', i)}",
                "home":     title,
                "score":    f"${sale:.2f}",
                "away":     f"-{savings}%",
                "league":   "GAME DEALS",
                "category": "DEALS",
                "time":     f"was ${normal:.2f}",
                "status":   "SALE",
            })
        return rows

    def to_reel_groups(self, items: List[Dict],
                       fmt: str = "steam_charts") -> List[Dict]:
        league_map = {
            "steam_charts": "STEAM TOP 10",
            "esports":      None,
            "new_releases": "NEW RELEASES",
            "game_deals":   "GAME DEALS",
        }

        if fmt == "esports":
            game_map: dict = {}
            for item in items:
                game_map.setdefault(item["league"], []).append(item)
            return [{"league": lg, "display_name": lg, "matches": ms}
                    for lg, ms in game_map.items()]

        league = league_map.get(fmt, "GAMING")
        return [{"league": league, "display_name": league, "matches": items}]
