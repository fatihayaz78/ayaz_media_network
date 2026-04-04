"""
sports_daemon.py — Sports Reel Studio arka plan süreci
Çalıştır: python sports_daemon.py
launchd tarafından boot'ta otomatik başlatılır (setup_launchd.sh ile kur)
"""

import os
import sys
import json
import logging
import signal
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fetcher      import fetch_sport
from video_maker  import make_reel
from youtube      import upload_video, build_title, build_description

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(BASE_DIR, "daemon.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("daemon")

# ── Sabit yollar ─────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
MUSIC_DIR   = os.path.join(BASE_DIR, "music")
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONTINENT_ORDER = [
    "EUROPE", "AMERICAS", "ASIA-PACIFIC", "MOTORSPORT", "OTHER",
    # New channel categories
    "UPCOMING", "CONFIRMED", "RUMOURS",
    "CHARTS", "DEALS", "ESPORTS", "RELEASES",
    "CRYPTO",
    "MODEL_UPDATE", "BIG_TECH", "TOOLS", "FUNDING", "RESEARCH", "REGULATION",
    "POLITICS", "TECHNOLOGY", "ECONOMY", "SCIENCE", "HEALTH", "CLIMATE",
    "CONFLICT", "CULTURE",
    "TURKEY",
]


# ── Config ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def update_run_log(schedule_id: str, status: str, detail: str = ""):
    cfg = load_config()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cfg.setdefault("_last_runs", {})[schedule_id] = {
        "time":   now,
        "status": status,
        "detail": detail,
    }
    save_config(cfg)


# ── Kıta bazlı gruplama ───────────────────────────────────────────────────────
def group_by_continent(rows: list, league_display: dict) -> list:
    """
    Maç listesini kıta bazlı gruplar.
    app.py ile aynı format: [{"name": "EUROPE", "groups": [...]}, ...]
    """
    cont_map: dict = {}

    for row in rows:
        league    = row.get("league", "")
        info      = league_display.get(league, {})
        continent = info.get("continent") or row.get("category", "OTHER")
        display   = info.get("display") or row.get("league", league)

        if continent not in cont_map:
            cont_map[continent] = {}
        if league not in cont_map[continent]:
            cont_map[continent][league] = {
                "display_name": display,
                "matches":      [],
            }
        cont_map[continent][league]["matches"].append(row)

    continents = []
    for cont_name in CONTINENT_ORDER:
        if cont_name not in cont_map:
            continue
        groups = [
            {
                "league":       lg,
                "display_name": data["display_name"],
                "matches":      data["matches"],
            }
            for lg, data in cont_map[cont_name].items()
        ]
        continents.append({"name": cont_name, "groups": groups})

    return continents


# ── Kanal yönlendirici ────────────────────────────────────────────────────────
def get_channel_rows(schedule: dict, date_str: str) -> list:
    """
    Routes to the correct fetcher based on schedule["source"] field.

    source values:
      "sportapi"  → existing fetch_sport() (sports, amerikan, basket)
      "fixtures"  → FixturesFetcher (upcoming matches)
      "finance"   → FinanceFetcher (stocks + crypto)
      "music"     → MusicFetcher (Apple Music charts)
      "techai"    → TechAIFetcher (AI news)
      "transfer"  → TransferFetcher (football transfers)
      "news"      → NewsFetcher (world news)
      "games"     → GamesFetcher (steam/esports/deals)
    """
    source = schedule.get("source", "sportapi")

    if source == "fixtures":
        from channels.fixtures.fixtures_fetcher import FixturesFetcher
        from datetime import date, timedelta
        today = date.today()
        week_end = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        return FixturesFetcher().fetch(today_str, week_end)

    elif source == "finance":
        from channels.finance.finance_fetcher import FinanceFetcher
        return FinanceFetcher().fetch(date_str, date_str)

    elif source == "music":
        from channels.music.music_fetcher import MusicFetcher
        continent = schedule.get("continent", "EUROPE")
        return MusicFetcher().fetch(continent=continent)

    elif source == "techai":
        from channels.techai.techai_fetcher import TechAIFetcher
        from datetime import date, timedelta
        week_start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        return TechAIFetcher().fetch(week_start, date_str)

    elif source == "transfer":
        from channels.transfer.transfer_fetcher import TransferFetcher
        return TransferFetcher().fetch(date_str, date_str)

    elif source == "news":
        from channels.news.news_fetcher import NewsFetcher
        return NewsFetcher().fetch(date_str, date_str)

    elif source == "games":
        from channels.games.games_fetcher import GamesFetcher
        fmt = schedule.get("games_format", "steam_charts")
        return GamesFetcher().fetch(date_str, date_str, fmt=fmt)

    else:
        # Default: existing sports behavior
        sports = schedule.get("sports", [])
        leagues_filter = schedule.get("leagues_filter", [])
        all_rows = []
        for sport_id in sports:
            try:
                rows = fetch_sport(sport_id, date_str, date_str,
                                   leagues_filter=leagues_filter or None)
                logger.info(f"  {sport_id}: {len(rows)} rows")
                all_rows.extend(rows)
            except Exception as e:
                logger.warning(f"  {sport_id} fetch error: {e}")
        return all_rows


# ── Ana iş akışı ──────────────────────────────────────────────────────────────
def run_schedule(schedule: dict):
    sid     = schedule["id"]
    label   = schedule["label"]
    cfg     = load_config()
    channel = cfg.get("channel_name", "DailyScoreBoard")
    yt_on   = cfg.get("youtube_enabled", False)

    logger.info(f"=== {label} ({sid}) başlıyor ===")

    today     = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    date_str  = yesterday.strftime("%Y-%m-%d")

    # ── 1. Veri çek ──────────────────────────────────────────────────────────
    sports         = schedule.get("sports", [])
    all_rows       = get_channel_rows(schedule, date_str)
    logger.info(f"  Toplam fetch: {len(all_rows)} satır")

    if not all_rows:
        logger.info("  Veri yok — reel atlandı")
        update_run_log(sid, "skipped", "Veri bulunamadı")
        return

    # ── 2. Kıta bazlı grupla ─────────────────────────────────────────────────
    league_display = cfg.get("league_display", {})
    continents     = group_by_continent(all_rows, league_display)

    total_matches = sum(
        len(g["matches"])
        for c in continents
        for g in c["groups"]
    )
    logger.info(f"  Toplam: {total_matches} maç, {len(continents)} kıta")

    # ── 3. Reel üret ─────────────────────────────────────────────────────────
    stamp    = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_name = f"reel_{sid}_{stamp}.mp4"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    music_path   = None
    music_fname  = cfg.get("music_filename")
    music_volume = float(cfg.get("music_volume", 0.4))
    if music_fname:
        p = os.path.join(MUSIC_DIR, music_fname)
        if os.path.exists(p):
            music_path = p

    bg_path  = None
    bg_fname = cfg.get(f"bg_{sid}")
    if bg_fname:
        p = os.path.join(UPLOAD_DIR, bg_fname)
        if os.path.exists(p):
            bg_path = p

    # Scheduleın birincil sporunu kimlik rengi için kullan
    primary_sport = sports[0] if sports else "futbol"

    reel_config = {
        "channel_name": channel,
        "date":         yesterday.strftime("%d.%m.%Y"),
        "continents":   continents,
    }

    try:
        make_reel(
            reel_config, out_path,
            bg_path, music_path, music_volume,
            sport_id=primary_sport,
        )
        logger.info(f"  Reel üretildi: {out_name}")
    except Exception as e:
        logger.error(f"  Reel üretme hatası: {e}")
        update_run_log(sid, "error", f"video_maker: {e}")
        return

    # ── 4. YouTube'a yükle ───────────────────────────────────────────────────
    if not yt_on:
        logger.info("  YouTube kapalı — upload atlandı")
        update_run_log(sid, "ok_local", out_name)
        return

    sport_labels = schedule.get("sport_labels", {})
    sport_name   = " & ".join(sport_labels.values()) if sport_labels else label

    title = build_title(
        schedule.get("youtube_title", "Sports Results | {date} | {channel}"),
        sport_name, channel,
    )
    description = build_description(
        schedule.get("youtube_description", "Daily sports results.\n#{channel}"),
        sport_name, channel,
    )
    tags = schedule.get("youtube_tags", ["sports", "scores"])

    result = upload_video(out_path, title, description, tags)
    if result["ok"]:
        logger.info(f"  YouTube: {result['url']}")
        update_run_log(sid, "ok_youtube", result["url"])
    else:
        logger.error(f"  YouTube upload hatası: {result['error']}")
        update_run_log(sid, "error_youtube", result["error"])


# ── Scheduler ─────────────────────────────────────────────────────────────────
def start_scheduler():
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron      import CronTrigger
    except ImportError:
        logger.error("APScheduler kurulu değil. Kur: pip install apscheduler")
        sys.exit(1)

    scheduler = BlockingScheduler(timezone="UTC")
    cfg       = load_config()

    for sched in cfg.get("schedules", []):
        if not sched.get("enabled", False):
            logger.info(f"  {sched['id']} devre dışı — atlandı")
            continue

        h = sched["cron_hour_utc"]
        m = sched["cron_minute_utc"]

        if sched.get("race_week_only"):
            trigger = CronTrigger(day_of_week="mon", hour=h, minute=m, timezone="UTC")
        else:
            trigger = CronTrigger(hour=h, minute=m, timezone="UTC")

        def make_job(s=sched):
            return lambda: run_schedule(s)

        scheduler.add_job(
            make_job(),
            trigger=trigger,
            id=sched["id"],
            name=sched["label"],
            max_instances=1,
            coalesce=True,
        )
        logger.info(
            f"  Zamanlandı: {sched['label']} → "
            f"{h:02d}:{m:02d} UTC "
            f"{'(Pazartesi)' if sched.get('race_week_only') else 'her gün'}"
        )

    def write_next_runs():
        runs = {}
        for job in scheduler.get_jobs():
            nxt = getattr(job, "next_fire_time", None) or getattr(job, "next_run_time", None)
            if nxt:
                runs[job.id] = nxt.strftime("%Y-%m-%d %H:%M UTC")
        cfg2             = load_config()
        cfg2["_next_runs"] = runs
        save_config(cfg2)

    scheduler.add_listener(lambda e: write_next_runs(), mask=0x1)

    def shutdown(sig, frame):
        logger.info("Kapatılıyor...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT,  shutdown)

    logger.info("=== Sports Daemon başladı ===")
    write_next_runs()
    scheduler.start()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "run":
        target = sys.argv[2]
        cfg    = load_config()
        for s in cfg.get("schedules", []):
            if s["id"] == target:
                run_schedule(s)
                break
        else:
            print(f"Bilinmeyen schedule id: {target}")
            print(f"Mevcut idler: {[s['id'] for s in cfg.get('schedules', [])]}")
    else:
        start_scheduler()
