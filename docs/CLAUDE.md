# CLAUDE.md — Ayaz Media Network
> Version: 5.0 | April 2026 | Full Audit
> **Read this file FIRST** — every session.

---

## Project Overview

**Ayaz Media Network** — automated YouTube Shorts generator.
Fetch data from APIs/RSS, generate 1080x1920 MP4, upload to YouTube.

**Owner:** Fatih Ayaz
**Path:** `/Users/fatihayaz/Documents/Projects/ayaz_media_network`
**Stack:** Python 3.14.3, Flask 3.1.3, Pillow 12.2.0, ffmpeg, APScheduler 3.11.2, Anthropic SDK 0.89.0, YouTube Data API v3
**venv:** amn (`source amn/bin/activate`)
**Port:** 5052
**Tests:** 31/31 passing

---

## Routes — ALL VERIFIED WORKING (200)

```
Pages (7):
  GET /                          → redirect to /channel
  GET /channel                   → Channel Manager (continent tabs, data fetch, reel)
  GET /channel-editor/<ch>       → Reel editor (no continent)
  GET /channel-editor/<ch>/<cont>→ Reel editor (continent-specific)
  GET /upload                    → YouTube upload + history
  GET /reel-config               → Per-channel config (legacy, use editor instead)
  GET /techai-editor             → Manual AI news editor
  GET /scheduler                 → APScheduler status

Data APIs (12):
  GET  /api/fetch/channel        → Unified fetch (all channels)
  GET  /api/fetch                → Sports fetch (legacy)
  POST /api/channel/description  → AI description (Claude Haiku)
  POST /api/make-reel            → Generate MP4 (legacy single reel)
  POST /api/make-reel/<ch>/<cont>→ Generate continent reel
  GET  /api/download/<filename>  → Download MP4
  GET  /api/download/<ch>/<file> → Download continent MP4

Config APIs (4):
  GET/POST /api/reel-config/<ch>          → Base channel config
  GET/POST /api/reel-config/<ch>/<cont>   → Continent-specific config

Upload APIs (5):
  POST /api/upload-media          → Background image/video
  GET  /api/music/tracks          → Pixabay tracks list
  POST /api/music/upload          → Custom music upload
  POST /api/music/download-pixabay→ Download Pixabay track
  POST /api/upload/youtube        → Upload to YouTube
  GET  /api/upload/list-reels     → List MP4 files
  GET  /api/upload/log            → Upload history
  GET  /thumbnail/<channel>       → Latest thumbnail JPEG

Techai APIs (4):
  GET  /api/techai/items          → List items
  POST /api/techai/items          → Add item
  DELETE /api/techai/items/<id>   → Delete item
  POST /api/techai/items/<id>/feature → Toggle featured

Scheduler APIs (5):
  GET  /api/scheduler/status      → Schedules + last runs
  POST /api/scheduler/config      → Update config
  POST /api/scheduler/run-now     → Manual trigger
  GET  /api/scheduler/logs        → Last 100 log lines
  POST /api/scheduler/daemon      → Start/stop daemon
```

---

## What ACTUALLY Works (verified)

```
Data fetching:
  Finance:  91 rows (63 stocks + 17 forex + 6 metals + 5 crypto fallback)
  Music:    55 rows (18 countries via Apple Music RSS)
  News:     ~50 rows (10 regions via BBC RSS)
  Games:    13 rows (10 Steam + 3 Deals)
  Techai:   8 rows (from manual items.json)
  Transfer: 8 rows (sample fallback)
  Sports:   0 rows (API quota — use MOCK_DATA=1 for 7 sports)

Continent splitting:
  Finance → AMERICAS(29) EUROPE(37) ASIA(40) AFRICA(18)
  Music   → AMERICAS(20) EUROPE(20) ASIA(15) AFRICA(0)
  News    → splits by BBC regional feeds

Reel generation:
  make_reel() works, generates MP4 with ffmpeg
  Auto-thumbnail generated (1280x720 JPEG)
  Header reads header_title from SPORT_IDENTITY
  Footer reads channel_name from config
  reel_config.json overrides applied (header, footer, colors, speed)
  Continent-specific reels via /api/make-reel/<ch>/<cont>

Channel editor:
  /channel-editor/<ch>/<cont> loads correctly
  4 continent tabs with data preview
  Config saves to channels/{ch}_{CONT}/reel_config.json
  "Make Reel" and "Make All 4" buttons work

YouTube:
  upload_video() implemented with OAuth2 + token refresh
  Needs credentials.json (not configured yet)
  Thumbnail upload supported (thumbnails().set())
```

---

## What is NOT Implemented (honest)

```
Section dividers in reels (STOCKS/FOREX/METALS/CRYPTO headers)  → NOT CODED
Green/red % change colors in reel rows                          → NOT CODED
scheduler.py (standalone)                                       → DOES NOT EXIST
  (scheduling lives in sports_daemon.py with APScheduler)
YouTube credentials.json                                        → NOT CONFIGURED
PANDASCORE_KEY (esports data)                                   → NOT SET
RAWG_KEY (game releases)                                        → NOT SET
AFRICA music data                                               → NO SOURCE
CoinGecko live prices                                           → SSL BLOCKED (static fallback works)
Sports live data                                                → API QUOTA (mock works)
```

---

## Key Files

```
app.py                  — Flask app, 35+ routes
video_maker.py          — Reel engine: header/content/footer, ffmpeg
sports_daemon.py        — Data routing, group_by_continent, split_by_continent, APScheduler
fetcher.py              — SportAPI fetch + MOCK_DATA fallback
youtube.py              — YouTube Data API v3, upload_video()
thumbnail_maker.py      — 1280x720 JPEG thumbnails
channels/finance/       — finance_fetcher.py (yfinance batch, forex, metals, crypto)
channels/music/         — music_fetcher.py (Apple RSS, 18 countries)
channels/news/          — news_fetcher.py (BBC RSS, 10 regions)
channels/games/         — games_fetcher.py (Steam + CheapShark)
channels/techai/        — techai_fetcher.py + items.json
channels/transfer/      — transfer_fetcher.py (RSS + samples)
channels/fixtures/      — fixtures_fetcher.py (SportAPI)
static/*.html           — 7 HTML pages (SPA, client-side rendered)
```

---

## Session Start

```bash
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network
source amn/bin/activate
python -m pytest tests/test_app_routes.py tests/channels/test_fixtures.py -v --tb=short 2>&1 | tail -5
git log --oneline -3
git status --short
```
