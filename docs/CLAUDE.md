# CLAUDE.md — Ayaz Media Network
> Version: 3.0 | April 2026
> **Read this file FIRST** — every session, both Claude.ai and Claude Code.

---

## Roles & Workflow

```
Claude.ai  = PM + Architect
  - Talks with Fatih Ayaz
  - Reads Claude Code's state report
  - Writes prompts for Claude Code
  - Makes architectural decisions
  - NEVER writes code directly

Claude Code = Developer + Software Architect  
  - Reads all MD files before starting work
  - Implements what Claude.ai instructs
  - Reports current state back to Claude.ai
  - Updates MD files + CHANGELOG after every change
  - Runs tests before declaring done
```

### Every Session Flow

```
1. Claude Code → runs startup checks → pastes report to Claude.ai
2. Claude.ai   → reads report + MD files → writes prompt
3. Claude Code → implements → runs tests → updates docs
4. Claude Code → pastes completion report to Claude.ai
5. Repeat
```

---

## Project Overview

**Ayaz Media Network** — automated YouTube Shorts factory.
Fetch data → generate 1080×1920 MP4 → upload to YouTube.
8 channels, 13 schedules, zero manual work after setup.

**Owner:** Fatih Ayaz
**Path:** `/Users/fatihayaz/Documents/Projects/ayaz_media_network`
**Stack:** Python 3.14.3, Flask 3.1.3, Pillow 12.2.0, ffmpeg, APScheduler 3.11.2, Anthropic SDK 0.89.0
**venv:** amn (source amn/bin/activate)
**Port:** 5052

---

## Build Status

```
Phase 1–8:  ✅ COMPLETE
Phase 9:    ✅ COMPLETE (finance redesign, music country level, scroll fix)
Phase 10:   ✅ COMPLETE (Channel Manager UI, color palettes, AI description)
Phase 11:   ✅ COMPLETE (bug fixes: tickers, toggles, persistence, date presets)
Phase 12:   ✅ COMPLETE (music all-continents, news geo, games combined, redirect)
Phase 13:   📋 PLANNED  (manual testing, UI visual QA, reel design approval)
See CHANGELOG.md for details.
```

---

## Channels (8 total)

| Channel | Module Doc | Status |
|---|---|---|
| @ayaz_sports | modules/SPORTS.md | ✅ Production |
| @ayaz_fixtures | modules/SPORTS.md | ✅ Built |
| @ayaz_finance | modules/FINANCE.md | ✅ Built |
| @ayaz_musics | modules/MUSIC.md | ✅ Built |
| @ayaz_techai | modules/TECHAI.md | ✅ Built |
| @ayaz_transfer | modules/TRANSFER.md | ✅ RSS+Claude |
| @ayaz_news | modules/NEWS.md | ✅ Built |
| @ayaz_gamezs | modules/GAMES.md | ✅ Built |

---

## Known Issues

| Issue | File | Priority |
|---|---|---|
| YouTube credentials.json missing | youtube.py | 🔴 Config |
| CoinGecko SSL on local network | finance_fetcher.py | 🟡 Network |
| Crypto: 0 rows until network fix | finance_fetcher.py | 🟡 Network |
| Fixtures: SportAPI monthly quota | fixtures_fetcher.py | 🟡 Quota |
| Sports: API quota on test runs | fetcher.py | 🟡 Quota |
| PANDASCORE_KEY not set (esports) | games_fetcher.py | 🟢 Optional |
| RAWG_KEY not set (game releases) | games_fetcher.py | 🟢 Optional |

---

## Doc Index (read before touching that module)

```
CLAUDE.md              ← this file
CHANGELOG.md           ← history of changes
ARCHITECTURE.md        ← data flow, contracts, API routes
UI.md                  ← visual spec, 15 themes, layout zones
modules/SPORTS.md      ← fetcher.py + fixtures_fetcher.py
modules/FINANCE.md     ← finance_fetcher.py
modules/MUSIC.md       ← music_fetcher.py
modules/TECHAI.md      ← techai_fetcher.py
modules/TRANSFER.md    ← transfer_fetcher.py
modules/NEWS.md        ← news_fetcher.py
modules/GAMES.md       ← games_fetcher.py
prompts/AI_PROMPTS.md  ← Claude API prompt library
NEXT_SESSION_PROMPT.md ← paste into Claude Code
```

---

## Golden Rules

1. **Read MD before touching code** — relevant module doc always first
2. **Update MD + CHANGELOG after every change** — no exceptions
3. **Never break** `fetcher.py` / `sports_daemon.py` existing behavior
4. **Never remove** entries from `video_maker.py` SPORT_IDENTITY
5. **Home/score/away contract** — universal row format, see ARCHITECTURE.md
6. **Test before done** — `pytest tests/test_app_routes.py -v` must pass

---

## Session Startup Script (Claude Code)

```bash
#!/bin/bash
# Run this at start of every Claude Code session
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network

echo "=== AYAZ MEDIA NETWORK — SESSION START ==="
echo ""
echo "--- Docs ---"
cat CLAUDE.md | head -30
echo ""
cat CHANGELOG.md | tail -30
echo ""
echo "--- Tests ---"
python -m pytest tests/test_app_routes.py -v --tb=short 2>&1 | tail -20
echo ""
echo "--- Git ---"
git status --short
git log --oneline -3
echo ""
echo "=== READY — paste this report to Claude.ai ==="
```

---

## Resolved Issues (Phase 6–7)

- ~~Roboto fonts 404~~ — fixed Sprint 6 (multi-source download)
- ~~TransferMarkt 404~~ — removed, RSS+Claude only (Sprint 6)
- ~~ANTHROPIC_API_KEY not set~~ — configured, AI channels live (Sprint 7)
- ~~datetime.utcnow() deprecation~~ — fixed across 10 files (Sprint 7)
- ~~Schedules disabled~~ — 12/13 enabled (Sprint 7)
