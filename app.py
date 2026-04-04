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
            continent = request.args.get("continent", "EUROPE")
            data = MusicFetcher().fetch(continent=continent)

        elif channel_id == "techai":
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
            game_fmt = fmt or "game_deals"
            data = GamesFetcher().fetch(date_from, date_to, fmt=game_fmt)

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
        continent = info.get("continent", "OTHER")
        display  = info.get("display", league)
        if continent not in cont_map:
            cont_map[continent] = []
        cont_map[continent].append({
            "league":       league,
            "display_name": display,
            "matches":      g.get("matches", []),
        })

    CONTINENT_ORDER = ["EUROPE", "AMERICAS", "ASIA-PACIFIC", "MOTORSPORT", "OTHER"]
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

    try:
        make_reel(reel_cfg, out_path, bg_path, music_path, music_volume, sport_id=sport_id)
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

if __name__ == "__main__":
    print("=" * 50)
    print("Sports Reel Studio  →  http://localhost:5050")
    print("Scheduler UI        →  http://localhost:5050/scheduler")
    print("=" * 50)
    app.run(debug=True, port=5052, use_reloader=False)
