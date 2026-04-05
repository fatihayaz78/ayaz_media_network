import os
import re
import sys
import json
import uuid
import threading
import subprocess
import requests as req
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from fetcher     import fetch_sport
from video_maker import make_reel

app = Flask(__name__, static_folder="static")
CORS(app)

BASE_DIR    = os.path.dirname(__file__)
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
MUSIC_DIR   = os.path.join(BASE_DIR, "music")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LOG_FILE    = os.path.join(BASE_DIR, "daemon.log")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR,  exist_ok=True)

ALLOWED_EXT       = {".jpg", ".jpeg", ".gif", ".mp4"}
ALLOWED_MUSIC_EXT = {".mp3", ".m4a", ".aac", ".wav", ".ogg"}

PIXABAY_TRACKS = [
    {"id":"pb1","name":"Sport Energy",      "mood":"Enerjik","bpm":128,"url":"https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3"},
    {"id":"pb2","name":"Motivational Rock", "mood":"Güçlü",  "bpm":140,"url":"https://cdn.pixabay.com/download/audio/2023/03/21/audio_f26c7ac78e.mp3"},
    {"id":"pb3","name":"Electronic Drive",  "mood":"Dinamik","bpm":120,"url":"https://cdn.pixabay.com/download/audio/2022/10/25/audio_946b1e8e0d.mp3"},
    {"id":"pb4","name":"Chill Ambient",     "mood":"Sakin",  "bpm":90, "url":"https://cdn.pixabay.com/download/audio/2022/12/12/audio_c5e8e3eb20.mp3"},
    {"id":"pb5","name":"Hip Hop Drums",     "mood":"Agresif","bpm":135,"url":"https://cdn.pixabay.com/download/audio/2023/01/27/audio_d16737dc28.mp3"},
]

# ── Config ───────────────────────────────────────────────────────────────────
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def daemon_status():
    try:
        r = subprocess.run(
            ["launchctl", "list", "com.dailyscoreboard.daemon"],
            capture_output=True, text=True
        )
        if r.returncode == 0 and "pid" in r.stdout.lower():
            return "running"
        return "stopped"
    except Exception:
        return "unknown"

# ── Ana UI ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return app.send_static_file("index.html")

# ── Mevcut API'ler ────────────────────────────────────────────────────────────
@app.route("/api/fetch")
def api_fetch():
    sport_id  = request.args.get("sport_id", "futbol")
    date_from = request.args.get("from", datetime.now().strftime("%Y-%m-%d"))
    date_to   = request.args.get("to", date_from)

    # config.json'dan bu spor için leagues_filter bul
    cfg            = load_config()
    leagues_filter = []
    for schedule in cfg.get("schedules", []):
        sports = schedule.get("sports", [])
        if sport_id in sports:
            leagues_filter.extend(schedule.get("leagues_filter", []))

    # Duplicate temizle
    leagues_filter = list(dict.fromkeys(leagues_filter))

    try:
        data = fetch_sport(sport_id, date_from, date_to,
                           leagues_filter=leagues_filter if leagues_filter else None)
        return jsonify({"ok": True, "data": data, "count": len(data)})
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500

@app.route("/api/fetch/channel")
def api_fetch_channel():
    """Unified fetch endpoint for all channels."""
    channel_id = request.args.get("channel_id", "sports")
    date_from  = request.args.get("from", datetime.now().strftime("%Y-%m-%d"))
    date_to    = request.args.get("to", date_from)
    fmt        = request.args.get("fmt", "")

    try:
        if channel_id == "fixtures":
            from channels.fixtures.fixtures_fetcher import FixturesFetcher
            data = FixturesFetcher().fetch(date_from, date_to)

        elif channel_id == "finance":
            from channels.finance.finance_fetcher import FinanceFetcher
            data = FinanceFetcher().fetch(date_from, date_to)

        elif channel_id == "music":
            from channels.music.music_fetcher import MusicFetcher
            continent = request.args.get("continent", "")
            if continent:
                data = MusicFetcher().fetch(continent=continent)
            else:
                data = MusicFetcher().fetch_all()

        elif channel_id == "techai":
            # Prefer manual items.json if it has data
            manual_items = _load_techai_items() if os.path.exists(TECHAI_ITEMS_PATH) else []
            if manual_items:
                data = _techai_items_to_rows(manual_items)
            else:
                from channels.techai.techai_fetcher import TechAIFetcher
                data = TechAIFetcher().fetch(date_from, date_to)

        elif channel_id == "transfer":
            from channels.transfer.transfer_fetcher import TransferFetcher
            data = TransferFetcher().fetch(date_from, date_to)

        elif channel_id == "news":
            from channels.news.news_fetcher import NewsFetcher
            data = NewsFetcher().fetch(date_from, date_to)

        elif channel_id == "games":
            from channels.games.games_fetcher import GamesFetcher
            if fmt:
                data = GamesFetcher().fetch(date_from, date_to, fmt=fmt)
            else:
                data = GamesFetcher().fetch_combined(date_from, date_to)

        else:
            cfg = load_config()
            leagues_filter = []
            for s in cfg.get("schedules", []):
                if channel_id in s.get("sports", []):
                    leagues_filter.extend(s.get("leagues_filter", []))
            leagues_filter = list(dict.fromkeys(leagues_filter))
            data = fetch_sport(channel_id, date_from, date_to,
                               leagues_filter=leagues_filter or None)

        return jsonify({"ok": True, "data": data, "count": len(data)})

    except Exception as ex:
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "error": str(ex)}), 500


@app.route("/channel")
def channel_page():
    return app.send_static_file("channel.html")


DESCRIPTION_PROMPTS = {
    "finance": """You are a Chief Market Analyst writing a YouTube Shorts description.
Analyze the stock market data below showing top movers across global markets.
Write ONE paragraph (2-3 sentences) highlighting the key market trends,
biggest movers, and overall market sentiment.
Then add 6-8 relevant hashtags on a new line.
Be specific — mention company names and percentages.
Data:
{data}""",
    "music": """You are a music journalist writing a YouTube Shorts description.
Based on the chart data below, write ONE paragraph (2-3 sentences) about
the current music trends, notable artists, and chart highlights.
Then add 6-8 hashtags.
Data:
{data}""",
    "techai": """You are a tech journalist covering AI and technology.
Based on the news headlines below, write ONE paragraph (2-3 sentences)
summarizing the week's biggest developments in AI and tech.
Then add 6-8 hashtags.
Data:
{data}""",
    "news": """You are a news anchor writing a YouTube Shorts description.
Based on the headlines below, write ONE paragraph (2-3 sentences)
summarizing today's most important world news stories.
Then add 6-8 hashtags.
Data:
{data}""",
    "transfer": """You are a football journalist covering transfer news.
Based on the transfer data below, write ONE paragraph (2-3 sentences)
about the latest transfer activity, notable moves, and rumors.
Then add 6-8 hashtags.
Data:
{data}""",
    "games": """You are a gaming journalist writing a YouTube Shorts description.
Based on the gaming data below (charts/deals), write ONE paragraph (2-3 sentences)
about top games, trends, or best deals right now.
Then add 6-8 hashtags.
Data:
{data}""",
    "sports": """You are a sports journalist writing a YouTube Shorts description.
Based on the match results below, write ONE paragraph (2-3 sentences)
summarizing the key results, standout performances, or league highlights.
Then add 6-8 hashtags.
Data:
{data}""",
    "fixtures": """You are a football journalist writing a YouTube Shorts description.
Based on the upcoming fixtures below, write ONE paragraph (2-3 sentences)
previewing the most exciting matches this week.
Then add 6-8 hashtags.
Data:
{data}""",
}


@app.route("/api/channel/description", methods=["POST"])
def generate_description():
    data = request.json or {}
    channel_id = data.get("channel_id", "")
    rows = data.get("rows", [])

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY not set"})

    # Build context from rows
    summary_lines = []
    for r in rows[:30]:
        parts = [r.get("home", ""), r.get("score", ""),
                 r.get("away", ""), r.get("status", "")]
        summary_lines.append(" | ".join(p for p in parts if p))

    data_text = "\n".join(summary_lines[:25])
    prompt_template = DESCRIPTION_PROMPTS.get(channel_id, DESCRIPTION_PROMPTS["news"])
    prompt = prompt_template.replace("{data}", data_text)

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        description = resp.content[0].text.strip()
        return jsonify({"ok": True, "description": description})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/upload-media", methods=["POST"])
def api_upload_media():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yok"}), 400
    f   = request.files["file"]
    sid = request.form.get("sport_id", "unknown")
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": "Geçersiz format"}), 400
    fname = f"{sid}_{uuid.uuid4().hex[:8]}{ext}"
    f.save(os.path.join(UPLOAD_DIR, fname))
    size = os.path.getsize(os.path.join(UPLOAD_DIR, fname))
    sz   = f"{size/1024:.0f} KB" if size < 1_048_576 else f"{size/1_048_576:.1f} MB"
    return jsonify({"ok": True, "filename": fname, "size": sz, "is_video": ext == ".mp4"})

@app.route("/api/music/tracks")
def api_music_tracks():
    return jsonify({"ok": True, "tracks": PIXABAY_TRACKS})

@app.route("/api/music/upload", methods=["POST"])
def api_music_upload():
    if "file" not in request.files:
        return jsonify({"error": "Dosya yok"}), 400
    f   = request.files["file"]
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_MUSIC_EXT:
        return jsonify({"error": "Geçersiz format"}), 400
    fname = f"custom_{uuid.uuid4().hex[:10]}{ext}"
    f.save(os.path.join(MUSIC_DIR, fname))
    size = os.path.getsize(os.path.join(MUSIC_DIR, fname))
    sz   = f"{size/1024:.0f} KB" if size < 1_048_576 else f"{size/1_048_576:.1f} MB"
    return jsonify({"ok": True, "filename": fname, "name": f.filename, "size": sz, "type": "custom"})

@app.route("/api/music/download-pixabay", methods=["POST"])
def api_music_download_pixabay():
    body     = request.get_json(force=True) or {}
    track_id = body.get("track_id")
    track    = next((t for t in PIXABAY_TRACKS if t["id"] == track_id), None)
    if not track:
        return jsonify({"error": "Track bulunamadı"}), 404
    fname = f"pixabay_{track_id}.mp3"
    path  = os.path.join(MUSIC_DIR, fname)
    if not os.path.exists(path):
        try:
            r = req.get(track["url"], timeout=30, stream=True)
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(8192): fh.write(chunk)
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
    size = os.path.getsize(path)
    sz   = f"{size/1024:.0f} KB" if size < 1_048_576 else f"{size/1_048_576:.1f} MB"
    return jsonify({"ok": True, "filename": fname, "name": track["name"], "size": sz})

@app.route("/api/make-reel", methods=["POST"])
def api_make_reel():
    body = request.get_json(force=True)
    if not body:
        return jsonify({"error": "Body yok"}), 400

    sport_id = body.get("sport_id", "sport")
    stamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"reel_{sport_id}_{stamp}.mp4"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    bg_path = None
    if body.get("bg_filename"):
        c = os.path.join(UPLOAD_DIR, body["bg_filename"])
        if os.path.exists(c): bg_path = c

    music_path   = None
    music_volume = float(body.get("music_volume", 0.4))
    if body.get("music_filename"):
        c = os.path.join(MUSIC_DIR, body["music_filename"])
        if os.path.exists(c): music_path = c

    # UI'dan gelen groups → continents formatına çevir
    cfg            = load_config()
    league_display = cfg.get("league_display", {})
    groups         = body.get("groups", [])

    # Kıta bazlı grupla
    cont_map = {}
    for g in groups:
        league   = g.get("league", "")
        info     = league_display.get(league, {})
        # Check group-level continent, then first match's continent field
        matches  = g.get("matches", [])
        continent = (g.get("continent")
                     or info.get("continent")
                     or (matches[0].get("continent") if matches else None)
                     or "OTHER")
        display  = g.get("display_name") or info.get("display") or league
        if continent not in cont_map:
            cont_map[continent] = []
        cont_map[continent].append({
            "league":       league,
            "display_name": display,
            "matches":      matches,
        })

    CONTINENT_ORDER = ["EUROPE", "AMERICAS", "ASIA-PACIFIC", "ASIA",
                       "MOTORSPORT", "COMMODITIES", "CRYPTO", "OTHER"]
    continents = []
    for cont_name in CONTINENT_ORDER:
        if cont_name in cont_map:
            continents.append({
                "name":   cont_name,
                "groups": cont_map[cont_name],
            })

    # Hiç kıta eşleşmezse direkt groups kullan
    if not continents:
        continents = [{"name": body.get("sport_name", ""), "groups": groups}]

    reel_cfg = {
        "channel_name": body.get("channel_name", ""),
        "date":         datetime.now().strftime("%d.%m.%Y"),
        "continents":   continents,
    }

    custom_theme = body.get("custom_theme")

    try:
        make_reel(reel_cfg, out_path, bg_path, music_path, music_volume,
                  sport_id=sport_id, custom_theme=custom_theme)
        return jsonify({"ok": True, "filename": out_name,
                        "download_url": f"/api/download/{out_name}"})
    except Exception as ex:
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "error": str(ex)}), 500

@app.route("/api/download/<filename>")
def api_download(filename):
    if not re.match(r"^[\w\-\.]+$", filename):
        return jsonify({"error": "Geçersiz dosya adı"}), 400
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Dosya bulunamadı"}), 404
    return send_file(path, as_attachment=True, mimetype="video/mp4")

# ── YENİ: Scheduler UI rotaları ───────────────────────────────────────────────
@app.route("/scheduler")
def scheduler_page():
    return app.send_static_file("scheduler.html")

@app.route("/api/scheduler/status")
def api_scheduler_status():
    cfg = load_config()
    return jsonify({
        "ok":           True,
        "daemon":       daemon_status(),
        "youtube":      cfg.get("youtube_enabled", False),
        "channel":      cfg.get("channel_name", ""),
        "music_volume": cfg.get("music_volume", 0.4),
        "music":        cfg.get("music_filename"),
        "schedules":    cfg.get("schedules", []),
        "last_runs":    cfg.get("_last_runs", {}),
        "next_runs":    cfg.get("_next_runs", {}),
    })

@app.route("/api/scheduler/config", methods=["POST"])
def api_scheduler_config():
    body = request.get_json(force=True) or {}
    cfg  = load_config()
    if "channel_name"    in body: cfg["channel_name"]    = body["channel_name"]
    if "youtube_enabled" in body: cfg["youtube_enabled"] = bool(body["youtube_enabled"])
    if "music_volume"    in body: cfg["music_volume"]    = float(body["music_volume"])
    if "music_filename"  in body: cfg["music_filename"]  = body["music_filename"]
    if "schedules" in body:
        existing = {s["id"]: s for s in cfg.get("schedules", [])}
        for ns in body["schedules"]:
            if ns["id"] in existing:
                for k in ("enabled", "cron_hour_utc", "cron_minute_utc"):
                    if k in ns: existing[ns["id"]][k] = ns[k]
        cfg["schedules"] = list(existing.values())
    save_config(cfg)
    return jsonify({"ok": True})

@app.route("/api/scheduler/run-now", methods=["POST"])
def api_scheduler_run_now():
    body = request.get_json(force=True) or {}
    sid  = body.get("id")
    if not sid:
        return jsonify({"error": "id gerekli"}), 400

    def _run():
        subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "sports_daemon.py"), "run", sid],
            cwd=BASE_DIR
        )
    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"ok": True, "message": f"{sid} başlatıldı"})

@app.route("/api/scheduler/logs")
def api_scheduler_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({"ok": True, "lines": []})
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return jsonify({"ok": True, "lines": [l.rstrip() for l in lines[-100:]]})

@app.route("/api/scheduler/daemon", methods=["POST"])
def api_scheduler_daemon():
    body   = request.get_json(force=True) or {}
    action = body.get("action")
    label  = "com.dailyscoreboard.daemon"
    if action == "start":
        subprocess.run(["launchctl", "start", label], capture_output=True)
    elif action == "stop":
        subprocess.run(["launchctl", "stop",  label], capture_output=True)
    else:
        return jsonify({"error": "action: start|stop"}), 400
    import time; time.sleep(1)
    return jsonify({"ok": True, "daemon": daemon_status()})

# ── Reel Config ──────────────────────────────────────────────────────────────
REEL_CONFIG_DIR = os.path.join(BASE_DIR, "channels")

def _reel_config_path(channel_id: str) -> str:
    d = os.path.join(REEL_CONFIG_DIR, channel_id)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "reel_config.json")

def _load_reel_config(channel_id: str) -> dict:
    path = _reel_config_path(channel_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_reel_config(channel_id: str, cfg: dict):
    with open(_reel_config_path(channel_id), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


@app.route("/reel-config")
def reel_config_page():
    return app.send_static_file("reel_config.html")


@app.route("/api/reel-config/<channel_id>")
def api_get_reel_config(channel_id):
    cfg = _load_reel_config(channel_id)
    return jsonify({"ok": True, "config": cfg})


@app.route("/api/reel-config/<channel_id>", methods=["POST"])
def api_set_reel_config(channel_id):
    body = request.get_json(force=True) or {}
    _save_reel_config(channel_id, body)
    return jsonify({"ok": True})


# ── Upload ───────────────────────────────────────────────────────────────────
UPLOAD_LOG_PATH = os.path.join(BASE_DIR, "data", "upload_log.json")


def _load_upload_log() -> list:
    os.makedirs(os.path.dirname(UPLOAD_LOG_PATH), exist_ok=True)
    if os.path.exists(UPLOAD_LOG_PATH):
        with open(UPLOAD_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_upload_log(log: list):
    os.makedirs(os.path.dirname(UPLOAD_LOG_PATH), exist_ok=True)
    with open(UPLOAD_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log[:100], f, ensure_ascii=False, indent=2)


@app.route("/upload")
def upload_page():
    return app.send_static_file("upload.html")


@app.route("/api/upload/list-reels")
def api_upload_list_reels():
    """List available reel files for upload."""
    reels = []
    for d in ["output", "output/phase15b", "output/phase15c", "output/phase14", "output/phase13"]:
        dp = os.path.join(BASE_DIR, d)
        if os.path.isdir(dp):
            for f in sorted(os.listdir(dp)):
                if f.endswith(".mp4"):
                    fp = os.path.join(dp, f)
                    kb = os.path.getsize(fp) // 1024
                    reels.append({"path": os.path.join(d, f), "name": f"{d}/{f}", "size_kb": kb})
    return jsonify({"ok": True, "reels": reels})


@app.route("/api/upload/youtube", methods=["POST"])
def api_upload_youtube():
    body = request.get_json(force=True) or {}
    channel_id = body.get("channel", "")
    file_path  = body.get("file_path", "")
    title      = body.get("title", "")
    description = body.get("description", "")
    tags       = body.get("tags", [])
    category_id = body.get("category_id", "17")
    privacy    = body.get("privacy", "public")

    full_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(full_path):
        return jsonify({"ok": False, "error": f"File not found: {file_path}"})

    try:
        from youtube import upload_video
        result = upload_video(
            full_path, title, description, tags,
            category_id=category_id, privacy=privacy,
        )
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    # Log the upload
    log = _load_upload_log()
    log.insert(0, {
        "id":          uuid.uuid4().hex[:8],
        "channel":     channel_id,
        "file_path":   file_path,
        "title":       title,
        "video_id":    result.get("video_id", ""),
        "url":         result.get("url", ""),
        "privacy":     privacy,
        "uploaded_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "status":      "success" if result.get("ok") else "failed",
        "error":       result.get("error", ""),
    })
    _save_upload_log(log)

    return jsonify(result)


@app.route("/api/upload/log")
def api_upload_log():
    return jsonify({"ok": True, "log": _load_upload_log()})


@app.route("/thumbnail/<channel>")
def api_thumbnail(channel):
    """Serve latest thumbnail for a channel."""
    thumb_dir = os.path.join(BASE_DIR, "output", "thumbnails")
    if not os.path.isdir(thumb_dir):
        return jsonify({"error": "No thumbnails"}), 404
    matches = sorted(
        [f for f in os.listdir(thumb_dir) if f.startswith(channel + "_") and f.endswith(".jpg")],
        reverse=True,
    )
    if not matches:
        return jsonify({"error": "No thumbnail found"}), 404
    return send_file(os.path.join(thumb_dir, matches[0]), mimetype="image/jpeg")


# ── Techai Editor ────────────────────────────────────────────────────────────
TECHAI_ITEMS_PATH = os.path.join(BASE_DIR, "channels", "techai", "items.json")

TECHAI_CATEGORY_EMOJI = {
    "LLM": "\U0001f916", "Hardware": "\U0001f4bb", "Policy": "\U0001f3db",
    "Robotics": "\U0001f9be", "Other": "\U0001f4a1",
}


def _techai_items_to_rows(items: list) -> list:
    """Convert manual techai items to standard row format."""
    # Featured first, then by date
    sorted_items = sorted(items, key=lambda x: (not x.get("featured", False), x.get("date", "")), reverse=False)
    sorted_items = sorted(sorted_items, key=lambda x: x.get("featured", False), reverse=True)
    rows = []
    for i, it in enumerate(sorted_items):
        cat = it.get("category", "Other")
        emoji = TECHAI_CATEGORY_EMOJI.get(cat, "\U0001f4a1")
        title = it.get("title", "")
        if it.get("featured"):
            title = "\u2B50 " + title
        rows.append({
            "id":        f"techai-manual-{it.get('id', i)}",
            "home":      f"{emoji} {cat}",
            "score":     "",
            "away":      title[:60],
            "league":    cat,
            "category":  cat,
            "continent": "AI & TECH",
            "time":      it.get("summary", "")[:100],
            "status":    it.get("source", "")[:20],
        })
    return rows


def _load_techai_items() -> list:
    os.makedirs(os.path.dirname(TECHAI_ITEMS_PATH), exist_ok=True)
    if os.path.exists(TECHAI_ITEMS_PATH):
        with open(TECHAI_ITEMS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_techai_items(items: list):
    os.makedirs(os.path.dirname(TECHAI_ITEMS_PATH), exist_ok=True)
    with open(TECHAI_ITEMS_PATH, "w", encoding="utf-8") as f:
        json.dump(items[:20], f, ensure_ascii=False, indent=2)


@app.route("/techai-editor")
def techai_editor_page():
    return app.send_static_file("techai_editor.html")


@app.route("/api/techai/items")
def api_techai_list():
    return jsonify({"ok": True, "items": _load_techai_items()})


@app.route("/api/techai/items", methods=["POST"])
def api_techai_add():
    body = request.get_json(force=True) or {}
    items = _load_techai_items()
    item = {
        "id":       body.get("id") or uuid.uuid4().hex[:8],
        "title":    (body.get("title") or "")[:80],
        "summary":  (body.get("summary") or "")[:300],
        "source":   (body.get("source") or "")[:40],
        "category": body.get("category", "Other"),
        "date":     body.get("date", datetime.now().strftime("%Y-%m-%d")),
        "featured": bool(body.get("featured", False)),
    }
    items.insert(0, item)
    _save_techai_items(items)
    return jsonify({"ok": True, "item": item})


@app.route("/api/techai/items/<item_id>", methods=["DELETE"])
def api_techai_delete(item_id):
    items = _load_techai_items()
    items = [i for i in items if i.get("id") != item_id]
    _save_techai_items(items)
    return jsonify({"ok": True})


@app.route("/api/techai/items/<item_id>/feature", methods=["POST"])
def api_techai_feature(item_id):
    items = _load_techai_items()
    for i in items:
        if i.get("id") == item_id:
            i["featured"] = not i.get("featured", False)
            break
    _save_techai_items(items)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("=" * 50)
    print("Sports Reel Studio  →  http://localhost:5052")
    print("Channel Manager     →  http://localhost:5052/channel")
    print("Techai Editor       →  http://localhost:5052/techai-editor")
    print("Reel Config         →  http://localhost:5052/reel-config")
    print("Scheduler UI        →  http://localhost:5052/scheduler")
    print("=" * 50)
    app.run(debug=True, port=5052, use_reloader=False)
