"""
fetcher.py — SportAPI (RapidAPI) üzerinden spor verisi çeker
Cache: her spor+tarih kombinasyonu cache/sport_date.json olarak saklanır
Rate limit: istekler arası 0.5s bekleme
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    "tenis":    "tennis",
    "amerikan": "american-football",
    "voley":    "volleyball",
    "dovus":    "mma",
    "diger":    "ice-hockey",
    "motor":    "motorsport",
}

FINISHED_STATUSES = {"finished", "ended", "after extra time", "after penalties", "aet", "ap"}

LEAGUE_COUNTRY = {
    "Premier League":                        "England",
    "Trendyol Süper Lig":                    "Turkey",
    "LaLiga":                                "Spain",
    "Serie A":                               "Italy",
    "Bundesliga":                            "Germany",
    "Ligue 1":                               "France",
    "VriendenLoterij Eredivisie":            "Netherlands",
    "Liga Portugal Betclic":                 "Portugal",
    "Pro League":                            "Belgium",
    "UEFA Champions League, Knockout stage": "Europe",
    "NBA":                                   "USA",
    "NFL":                                   "USA",
    "MLS":                                   "USA",
    "Brasileirão Betano":                    "Brazil",
    "Liga Profesional de Fútbol, Apertura":  "Argentina",
    "J1 League, East":                       "Japan",
    "J1 League, West":                       "Japan",
    "K League 1":                            "South Korea",
    "Chinese Super League":                  "China",
    "A-League Men":                          "Australia",
    "EuroLeague":                            "Europe",
    "BSL":                                   "Turkey",
    "Formula 1":                             "International",
    "MotoGP":                                "International",
    "Moto2":                                 "International",
    "Moto3":                                 "International",
}

# Cache dizini
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(sport_slug: str, date: str) -> str:
    return os.path.join(CACHE_DIR, f"{sport_slug}_{date}.json")


def _load_cache(sport_slug: str, date: str) -> Optional[List[Dict]]:
    path = _cache_path(sport_slug, date)
    if not os.path.exists(path):
        return None
    # Bugünün verisi için cache kullanma (henüz tamamlanmamış maç olabilir)
    if date == datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d"):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(sport_slug: str, date: str, data: List[Dict]):
    try:
        with open(_cache_path(sport_slug, date), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def get_dates(date_from: str, date_to: str) -> List[str]:
    try:
        a = datetime.strptime(date_from, "%Y-%m-%d")
        b = datetime.strptime(date_to,   "%Y-%m-%d")
    except ValueError:
        return [date_from[:10]]
    dates, cur = [], a
    while cur <= b:
        dates.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return dates[:7]


def _is_correct_country(league_name: str, category_name: str) -> bool:
    expected = LEAGUE_COUNTRY.get(league_name)
    if not expected:
        return True
    return expected.lower() in category_name.lower()


def fetch_by_date(sport_slug: str, date: str) -> List[Dict]:
    # Cache kontrolü
    cached = _load_cache(sport_slug, date)
    if cached is not None:
        print(f"[{sport_slug} {date}] cache'den {len(cached)} maç")
        return cached

    url = f"{BASE_URL}/sport/{sport_slug}/scheduled-events/{date}"
    try:
        time.sleep(0.5)  # Rate limit koruması
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.HTTPError as e:
        if "429" in str(e):
            print(f"[{sport_slug} {date}] Rate limit — 60s bekleniyor...")
            time.sleep(60)
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e2:
                print(f"[{sport_slug} {date}] fetch hatası (retry): {e2}")
                return []
        else:
            print(f"[{sport_slug} {date}] fetch hatası: {e}")
            return []
    except Exception as e:
        print(f"[{sport_slug} {date}] fetch hatası: {e}")
        return []

    events  = data.get("events", [])
    results = []

    for e in events:
        status_type = (e.get("status") or {}).get("type", "").lower()
        status_desc = (e.get("status") or {}).get("description", "").lower()

        is_finished = (
            status_type in FINISHED_STATUSES
            or "ended"    in status_desc
            or "finished" in status_desc
            or "after"    in status_desc
        )
        if not is_finished:
            continue

        home_score = (e.get("homeScore") or {}).get("display")
        away_score = (e.get("awayScore") or {}).get("display")
        if home_score is None or away_score is None:
            continue

        home_team = (e.get("homeTeam") or {}).get("name", "")
        away_team = (e.get("awayTeam") or {}).get("name", "")
        if not home_team or not away_team:
            continue

        tournament    = e.get("tournament") or {}
        league_name   = tournament.get("name", sport_slug)
        category      = tournament.get("category") or {}
        category_name = category.get("name", "")

        if not _is_correct_country(league_name, category_name):
            continue

        ts = e.get("startTimestamp")
        time_str = ""
        if ts:
            try:
                time_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M")
            except Exception:
                pass

        results.append({
            "id":       f"sapi-{e.get('id', '')}",
            "home":     home_team,
            "score":    f"{home_score} – {away_score}",
            "away":     away_team,
            "league":   league_name,
            "category": category_name,
            "time":     time_str,
            "status":   status_desc.upper() if status_desc else "FT",
        })

    # Cache'e kaydet
    _save_cache(sport_slug, date, results)
    print(f"[{sport_slug} {date}] API'den {len(results)} maç — cache'lendi")
    return results


def filter_by_leagues(rows: List[Dict], leagues_filter: List[str]) -> List[Dict]:
    if not leagues_filter:
        return rows
    filter_lower = [f.lower() for f in leagues_filter]
    return [r for r in rows if r["league"].lower() in filter_lower]


MOCK_DATA = {
    "futbol": [
        {"id":"m-f1","home":"Manchester City","score":"3 - 1","away":"Arsenal","league":"Premier League","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f2","home":"Real Madrid","score":"2 - 0","away":"Barcelona","league":"LaLiga","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f3","home":"Bayern Munich","score":"4 - 2","away":"Dortmund","league":"Bundesliga","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f4","home":"PSG","score":"1 - 0","away":"Lyon","league":"Ligue 1","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f5","home":"Inter","score":"2 - 2","away":"Juventus","league":"Serie A","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f6","home":"Galatasaray","score":"3 - 0","away":"Fenerbahce","league":"Trendyol S\u00fcper Lig","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-f7","home":"Flamengo","score":"2 - 1","away":"Palmeiras","league":"Brasileir\u00e3o Betano","category":"AMERICAS","time":"FT","status":"FT"},
    ],
    "basket": [
        {"id":"m-b1","home":"Lakers","score":"112 - 108","away":"Celtics","league":"NBA","category":"AMERICAS","time":"FT","status":"FT"},
        {"id":"m-b2","home":"Warriors","score":"124 - 115","away":"Nets","league":"NBA","category":"AMERICAS","time":"FT","status":"FT"},
        {"id":"m-b3","home":"Anadolu Efes","score":"85 - 79","away":"CSKA Moscow","league":"EuroLeague","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-b4","home":"Real Madrid","score":"92 - 88","away":"Barcelona","league":"EuroLeague","category":"EUROPE","time":"FT","status":"FT"},
    ],
    "tenis": [
        {"id":"m-t1","home":"Djokovic","score":"6-3 6-4","away":"Alcaraz","league":"ATP","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-t2","home":"Sinner","score":"7-6 6-2","away":"Medvedev","league":"ATP","category":"EUROPE","time":"FT","status":"FT"},
        {"id":"m-t3","home":"Swiatek","score":"6-1 6-3","away":"Sabalenka","league":"WTA","category":"EUROPE","time":"FT","status":"FT"},
    ],
    "motor": [
        {"id":"m-m1","home":"Verstappen","score":"1st","away":"Norris 2nd","league":"Formula 1","category":"MOTORSPORT","time":"FT","status":"FT"},
        {"id":"m-m2","home":"Leclerc","score":"3rd","away":"Hamilton 4th","league":"Formula 1","category":"MOTORSPORT","time":"FT","status":"FT"},
        {"id":"m-m3","home":"Bagnaia","score":"1st","away":"Martin 2nd","league":"MotoGP","category":"MOTORSPORT","time":"FT","status":"FT"},
    ],
    "dovus": [
        {"id":"m-d1","home":"Jon Jones","score":"KO R2","away":"Stipe Miocic","league":"UFC","category":"AMERICAS","time":"FT","status":"FT"},
        {"id":"m-d2","home":"Islam Makhachev","score":"SUB R3","away":"Dustin Poirier","league":"UFC","category":"AMERICAS","time":"FT","status":"FT"},
    ],
    "amerikan": [
        {"id":"m-a1","home":"Kansas City Chiefs","score":"27 - 24","away":"Philadelphia Eagles","league":"NFL","category":"AMERICAS","time":"FT","status":"FT"},
        {"id":"m-a2","home":"San Francisco 49ers","score":"31 - 17","away":"Dallas Cowboys","league":"NFL","category":"AMERICAS","time":"FT","status":"FT"},
    ],
    "voley": [
        {"id":"m-v1","home":"Brazil","score":"3 - 1","away":"Poland","league":"VNL","category":"AMERICAS","time":"FT","status":"FT"},
        {"id":"m-v2","home":"Italy","score":"3 - 0","away":"France","league":"VNL","category":"EUROPE","time":"FT","status":"FT"},
    ],
}


def fetch_sport(sport_id: str, date_from: str, date_to: str,
                leagues_filter: Optional[List[str]] = None) -> List[Dict]:
    # When MOCK_DATA=1, skip API entirely and return mock data
    if os.environ.get("MOCK_DATA") == "1":
        mock = MOCK_DATA.get(sport_id, [])
        if mock:
            print(f"[fetcher] Using mock data for {sport_id}: {len(mock)} rows")
            return mock

    dates      = get_dates(date_from, date_to)
    sport_slug = SPORT_SLUGS.get(sport_id, "football")
    all_rows: List[Dict] = []

    for date in dates:
        rows = fetch_by_date(sport_slug, date)
        all_rows.extend(rows)

    # Duplicate temizle
    seen, unique = set(), []
    for r in all_rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)

    if leagues_filter:
        unique = filter_by_leagues(unique, leagues_filter)

    return unique