# CLAUDE.md — Ayaz Media Network
> Version: 4.0 | April 2026
> **Read this file FIRST** — every session, both Claude.ai and Claude Code.

---

## Project Overview

**Ayaz Media Network** — automated YouTube Shorts/Reels generator.
Fetches live data from APIs/RSS, generates 1080x1920 MP4 reels, uploads to YouTube.

**Owner:** Fatih Ayaz
**Path:** `/Users/fatihayaz/Documents/Projects/ayaz_media_network`
**Stack:** Python 3.14.3, Flask 3.1.3, Pillow 12.2.0, ffmpeg, APScheduler 3.11.2, Anthropic SDK 0.89.0, YouTube Data API v3
**venv:** amn (`source amn/bin/activate`)
**Port:** 5052
**Tests:** 23/23 passing (`pytest tests/test_app_routes.py tests/channels/test_fixtures.py -v`)

---

## Channels (13 total)

| Channel  | Theme ID  | Data Source             | Header Title           | YT Category |
|----------|-----------|-------------------------|------------------------|-------------|
| futbol   | futbol    | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| basket   | basket    | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| tenis    | tenis     | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| motor    | motor     | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| dovus    | dovus     | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| amerikan | amerikan  | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| voley    | voley     | SportAPI / Mock         | WEEKLY SCORES          | Sports (17) |
| finance  | finance   | yfinance batch + CoinGecko | WEEKLY MARKETS      | News (25)   |
| music    | music     | Apple Music RSS (18 countries) | WEEKLY WORLD TOP 5 | Music (10) |
| news     | news      | BBC RSS (10 regions)    | WEEKLY WORLD NEWS      | News (25)   |
| games    | games     | Steam + CheapShark      | WEEKLY GAME NEWS       | Gaming (20) |
| techai   | techai    | Manual editor / RSS     | AI & TECH WEEKLY       | SciTech (28)|
| transfer | transfer  | RSS + Claude + samples  | WEEKLY TRANSFER NEWS   | Sports (17) |

---

## Build Status

```
Phase 1:    ✅ Scaffold + Fixtures channel
Phase 2:    ✅ Finance, Music, TechAI channels
Phase 3:    ✅ Transfer, News, Games channels
Phase 4:    ✅ Daemon + App integration
Phase 5:    ✅ Studio UI + Scheduler UI
Phase 6:    ✅ Production readiness (fonts, env, git, YouTube guide)
Phase 7:    ✅ Production go-live (schedules enabled, datetime fix)
Phase 8:    ✅ Fixtures rate limit fix (6h cache, quota detection)
Phase 9:    ✅ Finance redesign, music country level, scroll fix
Phase 10:   ✅ Channel Manager UI, color palettes, AI description
Phase 11:   ✅ Bug fixes (tickers, toggles, persistence, date presets)
Phase 12:   ✅ Music all-continents, news geo, games combined, redirect
Phase 13:   ✅ Per-channel header titles, test reels
Phase 14:   ✅ Visual QA fixes, 1.5x speed, font visibility
Phase 15A:  ✅ Bug fixes (underline/overlay), /reel-config UI
Phase 15B:  ✅ News RSS overhaul (10 countries), transfer fix, sport mocks
Phase 15C:  ✅ Techai manual editor (/techai-editor)
Phase 16:   ✅ YouTube upload + /upload UI + per-channel YT config
Phase 17:   📋 PLANNED (thumbnail generation + channel branding)
```

---

## Web Routes (app.py, port 5052)

```
Pages:
  GET  /                              → redirect to /channel
  GET  /channel                       → Channel Manager UI
  GET  /techai-editor                 → Techai manual news editor
  GET  /upload                        → YouTube upload UI
  GET  /reel-config                   → Per-channel reel + YT config
  GET  /scheduler                     → Scheduler UI

Data APIs:
  GET  /api/fetch                     → Sports fetch (legacy)
  GET  /api/fetch/channel             → Unified channel fetch
  POST /api/channel/description       → AI description generator (Claude Haiku)
  POST /api/make-reel                 → Generate MP4 reel
  GET  /api/download/<filename>       → Download generated MP4

Media:
  POST /api/upload-media              → Upload background image/video
  GET  /api/music/tracks              → List Pixabay tracks
  POST /api/music/upload              → Upload custom music
  POST /api/music/download-pixabay    → Download Pixabay track

YouTube:
  POST /api/upload/youtube            → Upload MP4 to YouTube
  GET  /api/upload/list-reels         → List available reel files
  GET  /api/upload/log                → Upload history

Reel Config:
  GET  /api/reel-config/<channel>     → Get channel config
  POST /api/reel-config/<channel>     → Save channel config

Techai:
  GET  /api/techai/items              → List manual items
  POST /api/techai/items              → Add item
  DELETE /api/techai/items/<id>       → Delete item
  POST /api/techai/items/<id>/feature → Toggle featured

Scheduler:
  GET  /api/scheduler/status          → Schedules + last runs
  POST /api/scheduler/config          → Update config
  POST /api/scheduler/run-now         → Trigger manual run
  GET  /api/scheduler/logs            → Last 100 log lines
  POST /api/scheduler/daemon          → Start/stop daemon
```

---

## Key Files

```
video_maker.py       — reel engine, SPORT_IDENTITY (15 themes), generate_header/footer/content
sports_daemon.py     — data routing, group_by_continent(), MOCK_DATA, APScheduler
fetcher.py           — SportAPI fetch + MOCK_DATA fallback (7 sports)
youtube.py           — YouTube Data API v3, OAuth2, upload_video()
app.py               — Flask app, all routes (30+)

channels/finance/    — finance_fetcher.py (yfinance batch, 180 tickers, commodities)
channels/music/      — music_fetcher.py (Apple RSS, 18 countries, fetch_all)
channels/news/       — news_fetcher.py (BBC RSS, 10 regions)
channels/games/      — games_fetcher.py (Steam + CheapShark, fetch_combined)
channels/techai/     — techai_fetcher.py + items.json (manual editor)
channels/transfer/   — transfer_fetcher.py (RSS + Claude + samples)
channels/fixtures/   — fixtures_fetcher.py (SportAPI, 6h cache)
channels/base_fetcher.py — abstract base class
```

---

## Data & Config

```
channels/{ch}/reel_config.json  — per-channel reel + YouTube config
channels/techai/items.json      — techai manual items (max 20)
data/upload_log.json            — YouTube upload history
config.json                     — global config (schedules, league_display)
.env                            — API keys (not committed)
cache/{ch}/                     — fetch cache per channel
```

---

## Known Issues

| Issue | File | Priority |
|---|---|---|
| YouTube credentials.json missing | youtube.py | 🔴 Config |
| CoinGecko SSL on local network | finance_fetcher.py | 🟡 Network |
| Sports API quota exhaustion | fetcher.py | 🟡 Quota (use MOCK_DATA=1) |
| Fixtures: SportAPI monthly quota | fixtures_fetcher.py | 🟡 Quota |
| PANDASCORE_KEY not set (esports) | games_fetcher.py | 🟢 Optional |
| RAWG_KEY not set (game releases) | games_fetcher.py | 🟢 Optional |

---

## Golden Rules

1. **Read MD before touching code** — relevant module doc always first
2. **Update MD + CHANGELOG after every change** — no exceptions
3. **Never break** existing behavior in fetcher.py / sports_daemon.py
4. **Never remove** entries from video_maker.py SPORT_IDENTITY
5. **Test before done** — `pytest tests/ -v` must pass
6. **Home/score/away contract** — universal row format across all channels

---

## Session Start Checklist

```bash
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network
source amn/bin/activate
pytest tests/test_app_routes.py tests/channels/test_fixtures.py -v --tb=short 2>&1 | tail -5
git log --oneline -5
git status --short
cat docs/CLAUDE.md | head -40
```

Report format:
```
=== AYAZ MEDIA NETWORK — SESSION START ===
Build:  Phase 16 ✅ COMPLETE | Phase 17 📋 PLANNED
Tests:  23/23 passing
Git:    [hash] (clean, main)
Port:   5052
=== READY ===
```
