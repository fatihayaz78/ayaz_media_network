# CHANGELOG.md — Ayaz Media Network
> Updated after every sprint/session.
> Format: ## [Sprint N] Date — Title

---

## [Sprint 7] April 2026 — Production Go-Live
**Phase:** 7 | **Status:** ✅ Complete

### What was built
- Task 7.1: datetime.utcnow() deprecation fixed across 10 files (11 occurrences)
  Also fixed 2x datetime.utcfromtimestamp() in fetcher.py and fixtures_fetcher.py
  All use datetime.now(timezone.utc).replace(tzinfo=None) — Python 3.14 clean
- Task 7.2: 12/13 schedules enabled in config.json (asiapac paused)
  youtube_enabled remains false (pending credentials.json)
- Task 7.3: Production smoke test — 6/7 channels producing reels:
  finance 1,416KB · music 406KB · techai 328KB · news 282KB ·
  games 145KB · transfer 118KB · fixtures skipped (SportAPI rate limit)
- Task 7.4: AI channels verified with Claude API:
  techai 8 rows (BIG TECH, TOOLS categories) · news 8 rows (POLITICS, ECONOMY)
  transfer 2 rows (Claude-extracted rumours with player/club data)
- Task 7.5: scripts/start_daemon.sh — production-ready with venv, .env, key checks

### Test results
```
tests/test_app_routes.py    9/9 passed (0 deprecation warnings)
```

### Files changed
- channels/finance/finance_fetcher.py    — datetime fix
- channels/music/music_fetcher.py        — datetime fix
- channels/techai/techai_fetcher.py      — datetime fix
- channels/news/news_fetcher.py          — datetime fix
- channels/transfer/transfer_fetcher.py  ��� datetime fix
- channels/games/games_fetcher.py        — datetime fix
- channels/fixtures/fixtures_fetcher.py  — datetime fix + utcfromtimestamp fix
- fetcher.py                             — datetime fix + utcfromtimestamp fix
- youtube.py                             — datetime fix
- tests/channels/test_fixtures.py        — datetime fix
- config.json                            — 12/13 schedules enabled
- scripts/start_daemon.sh                — production version
- docs/CHANGELOG.md                      — this entry
- docs/CLAUDE.md                         — phase status updated

### Pending (Phase 8)
- YouTube credentials.json → automated uploads
- SportAPI rate limits → caching strategy or plan upgrade
- PANDASCORE_KEY → esports data
- RAWG_KEY → game releases
- CoinGecko SSL fix (low priority)

---

## [Sprint 6] April 2026 — Production Readiness
**Phase:** 6 | **Status:** ✅ Complete

### What was built
- Task 6.1: Roboto fonts fixed — multi-source ensure_fonts() with 3 fallback URLs
  (googlefonts/roboto source works: Regular 503KB, Bold 502KB, Italic 520KB)
- Task 6.2: TransferMarkt (broken RapidAPI) removed — RSS+Claude only pipeline
  scripts/download_fonts.py standalone font checker added
- Task 6.3: Hardcoded API keys removed from fetcher.py, fixtures_fetcher.py,
  transfer_fetcher.py — all now use os.environ + .env
  .env.example created, .gitignore created
- Task 6.4: Git repository initialized — commit 098a870 (52 files)
- Task 6.5: docs/YOUTUBE_SETUP.md created — step-by-step OAuth2 guide
  youtube.py updated with --auth and --test-upload flags
- Task 6.6: 6/7 channels producing reels:
  finance 1,830KB · music 412KB · news 550KB · techai 329KB ·
  games 146KB · transfer 132KB · fixtures skipped (SportAPI rate limit)

### Test results
```
tests/test_app_routes.py        9/9 passed
tests/channels/test_transfer.py 6/6 passed (RSS+Claude)
```

### Files changed
- video_maker.py         — multi-source font download
- fetcher.py             — hardcoded key removed
- fixtures_fetcher.py    — hardcoded key removed
- transfer_fetcher.py    — TransferMarkt removed, hardcoded key removed
- youtube.py             — --auth / --test-upload flags
- .env.example           — new
- .gitignore             — new
- docs/YOUTUBE_SETUP.md  — new
- scripts/download_fonts.py — new
- CHANGELOG.md           — this entry
- CLAUDE.md              — phase status updated

### Pending (Phase 7)
- Set ANTHROPIC_API_KEY → enables Claude-curated techai/news/transfer
- Set PANDASCORE_KEY → esports data
- Set RAWG_KEY → game releases
- YouTube credentials.json → automated uploads
- SportAPI rate limits → caching strategy or plan upgrade

---

## [Sprint 5] April 2026 — Studio UI & Scheduler UI
**Phase:** 5 | **Status:** ✅ Complete

### What was built
- `index.html` — 19 channels, 8 sidebar groups, per-channel localStorage names
- `scheduler.html` — 13 schedules, channel column, no_data badge
- `doFetch()` routes `fetch_mode:"sport"` vs `fetch_mode:"channel"`
- `makeReel()` uses THEME_MAP for correct video theme per channel
- `getDefaultDates()` — fixtures=next7days, music/techai=last7days
- Flask route tests: 9/9 passing

### Test results
```
tests/test_app_routes.py    9 passed
```

### Files changed
- `static/index.html`    — full rewrite (19 channels)
- `static/scheduler.html` — channel column added
- `tests/test_app_routes.py` — new file

---

## [Sprint 4] April 2026 — Daemon + App Integration
**Phase:** 4 | **Status:** ✅ Complete

### What was built
- `sports_daemon.py` — `get_channel_rows()` routes all 8 channels
- `sports_daemon.py` — `group_by_continent()` uses `row["category"]` fallback
- `sports_daemon.py` — CONTINENT_ORDER expanded with new category names
- `app.py` — `/api/fetch/channel` endpoint (all 8 channels)
- `config.json` — `news` and `games_deals` schedules added
- Bug fixes: Steam filter, CheapShark $0 filter, TransferMarkt fallback

### Bug fixes applied
- **Steam:** `_is_real_game()` filters promo/upgrade items
- **CheapShark:** `if sale == 0.0: continue` skips free giveaways
- **TransferMarkt:** tries 2 endpoints, graceful fallback to RSS

### Test results
```
tests/test_integration.py    8 passed (536s)
Channel        Rows   Reel
finance        36     1,453KB
music_europe   10     426KB
techai         8      334KB
news           8      891KB
games_deals    3      151KB
fixtures       0      skipped (rate limit)
transfer       0      skipped (no keywords)
sports legacy  0      skipped (no matches)
```

### Files changed
- `sports_daemon.py`
- `app.py`
- `config.json`
- `tests/test_integration.py`

---

## [Sprint 3] April 2026 — Transfer, News, Games
**Phase:** 3 | **Status:** ✅ Complete

### What was built
- `channels/transfer/transfer_fetcher.py`
  - TransferMarkt API (404 on current plan — fallback to RSS)
  - RSS feeds: Sky Sports, BBC Sport, Goal.com
  - Claude AI extraction (needs API key)
  - Reliability stars by source (⭐–⭐⭐⭐⭐⭐)
  
- `channels/news/news_fetcher.py`
  - BBC, Reuters, Guardian, TechCrunch RSS
  - Claude AI categorization (8 categories)
  - Wide row mode (score="")
  
- `channels/games/games_fetcher.py`
  - Steam Charts (top sellers API)
  - PandaScore esports (needs key)
  - RAWG new releases (needs key, sample fallback)
  - CheapShark deals (free, no key)

### Test results
```
test_transfer.py    4 passed, 2 skipped
test_news.py        6 passed
test_games.py       6 passed
```

### Known issues introduced
- TransferMarkt API 404 (needs plan upgrade or alternative)
- Transfer rumours need ANTHROPIC_API_KEY for proper extraction
- Steam returns promo items (fixed in Sprint 4)
- CheapShark returns $0 giveaways (fixed in Sprint 4)

### Files changed
- `channels/transfer/transfer_fetcher.py` (new)
- `channels/news/news_fetcher.py` (new)
- `channels/games/games_fetcher.py` (new)
- `tests/channels/test_transfer.py` (new)
- `tests/channels/test_news.py` (new)
- `tests/channels/test_games.py` (new)

---

## [Sprint 2] April 2026 — Finance, Music, TechAI
**Phase:** 2 | **Status:** ✅ Complete

### What was built
- `channels/finance/finance_fetcher.py`
  - yfinance: 36 stocks across DAX/BIST100/FTSE100/SP500/NASDAQ/BOVESPA/NIKKEI/KOSPI
  - CoinGecko: 5 crypto (SSL issue on some networks — works in prod)
  - Finance disclaimer in footer

- `channels/music/music_fetcher.py`
  - Apple Music RSS: 10 countries, 4 continents
  - Weighted aggregation per continent
  - Trend tracking (↑↓● NEW) via weekly cache

- `channels/techai/techai_fetcher.py`
  - RSS: TechCrunch, The Verge, VentureBeat, arXiv
  - Claude Haiku categorization (fallback to raw RSS)
  - Wide row mode

### Test results
```
test_finance.py    5 passed, 1 skipped (CoinGecko SSL)
test_music.py      5 passed (430KB reel)
test_techai.py     6 passed (335KB reel, fallback mode)
```

### Reel sizes
- Finance: 2.0MB (36 rows)
- Music: 430KB (10 rows)
- TechAI: 335KB (8 wide rows)

### Files changed
- `channels/finance/finance_fetcher.py` (new)
- `channels/music/music_fetcher.py` (new)
- `channels/techai/techai_fetcher.py` (new)
- `video_maker.py` — wide row mode added
- `tests/channels/test_finance.py` (new)
- `tests/channels/test_music.py` (new)
- `tests/channels/test_techai.py` (new)

---

## [Sprint 1] April 2026 — Scaffold + Fixtures
**Phase:** 1 | **Status:** ✅ Complete

### What was built
- Project scaffold: `channels/`, `tests/`, `cache/` directories
- `channels/base_fetcher.py` — abstract base class
- `channels/fixtures/fixtures_fetcher.py`
  - Same SportAPI as sports, filter reversed to upcoming
  - Groups by date: "MON · 07 Apr" format
- `video_maker.py` — 7 new themes added (additive)
- `config.json` — 7 new schedules added
- `sports_daemon.py` — `get_channel_rows()` router

### Test results
```
test_fixtures.py    5 passed (147KB reel)
```

### Files changed
- `channels/` — new directory
- `channels/base_fetcher.py` (new)
- `channels/fixtures/fixtures_fetcher.py` (new)
- `video_maker.py` — SPORT_IDENTITY + CONTINENT_COLORS extended
- `config.json` — 7 schedules added
- `sports_daemon.py` — get_channel_rows() added
- `tests/` — new directory structure

---

## [Sprint 0] Pre-project — @ayaz_sports (Legacy)
**Status:** ✅ Production

### What existed
- `fetcher.py` — SportAPI7 fetcher with cache
- `video_maker.py` — 1080×1920 MP4 generator
- `app.py` — Flask server
- `sports_daemon.py` — APScheduler daemon
- `config.json` — 4 sport schedules (europe/americas/asiapac/global)
- `static/index.html` — Studio UI (sports only)
- `static/scheduler.html` — Scheduler UI

### Known state
- All sports channels working in production
- RAPIDAPI_KEY hardcoded in fetcher.py (TODO: move to env)
- Roboto font URLs broken (fallback to system fonts)
