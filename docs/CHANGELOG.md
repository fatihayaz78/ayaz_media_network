# CHANGELOG.md — Ayaz Media Network
> Updated after every sprint/session.
> Format: ## [Sprint N] Date — Title

---

## [Sprint 17] April 2026 — Thumbnail Generation + Channel Branding
**Phase:** 17 | **Status:** ✅ Complete

### What was built
- thumbnail_maker.py: 1280x720 JPEG, 3-zone layout
  - Top band: accent gradient + channel emoji/logo + date
  - Center: header title (86px bold) + top 3 items (36px accent)
  - Bottom band: "AYAZ MEDIA NETWORK" + @channel handle
  - Logo fallback chain: channels/{ch}/logo.png > static/logos/ > emoji
- Auto-thumbnail generated after every make_reel() call
- GET /thumbnail/<channel> route: serves latest thumbnail JPEG
- youtube.py: thumbnail_path param + thumbnails().set() after upload
- Test thumbnails generated: 13 channels, 73-103KB each

### Test results
```
tests/test_app_routes.py        21/21 passed (3 new: thumbnail_generation, route_exists, route_404)
tests/channels/test_fixtures.py  5/5 passed
Total: 26/26 passed
```

### Files changed
- thumbnail_maker.py — new file (thumbnail generator)
- video_maker.py — auto-thumbnail at end of make_reel()
- youtube.py — thumbnail_path param, thumbnails().set() upload
- app.py — GET /thumbnail/<channel> route
- tests/test_app_routes.py — 3 new tests
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 16] April 2026 — YouTube Upload + Scheduling
**Phase:** 16 | **Status:** ✅ Complete

### What was built
- youtube.py audit: OAuth2 flow, token refresh, resumable upload all working
  - Added `category_id` parameter (was hardcoded to "17")
  - Per-channel category IDs: Sports(17), News(25), Music(10), Gaming(20), SciTech(28)
- SPORT_IDENTITY: added `yt_tags` and `yt_category` to all 15 channel entries
- /reel-config: added YouTube fields (title template, description, tags, category, privacy, auto_upload)
- /upload page: manual upload UI with channel select, reel file picker, metadata editor
  - Upload history table (data/upload_log.json)
  - Per-channel description templates with hashtags
- Upload API: POST /api/upload/youtube → calls youtube.py upload_video()
  - Logs all uploads (success/failed) to upload_log.json
  - GET /api/upload/list-reels lists available MP4 files
  - GET /api/upload/log returns upload history

### Test results
```
tests/test_app_routes.py        18/18 passed (3 new: upload_page, list_reels, upload_log)
tests/channels/test_fixtures.py  5/5 passed
Total: 23/23 passed
```

### Files changed
- youtube.py — category_id parameter
- video_maker.py — yt_tags + yt_category in all SPORT_IDENTITY entries
- app.py — /upload route, upload APIs, upload log
- static/upload.html — new file (YouTube upload UI)
- static/reel_config.html — YouTube fields (title, desc, tags, category, privacy, auto_upload)
- tests/test_app_routes.py — 3 new tests
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 15C] April 2026 — Techai Manual Editor UI
**Phase:** 15C | **Status:** ✅ Complete

### What was built
- New route: /techai-editor — add/edit/delete/feature AI & Tech news items
- Storage: channels/techai/items.json (max 20 items, newest first)
- Editor UI: title/summary/source/category/date/featured form + items list
- Delete/feature toggle per item, Generate Reel button
- Techai fetcher reads items.json when available (priority over RSS)
- Manual items converted to standard row format with category emoji + grouping
- Featured items: star prefix, sorted to top
- Category emoji: LLM=robot, Hardware=laptop, Policy=building, Robotics=arm, Other=bulb
- Seeded 8 sample items, test reel: output/phase15c/techai.mp4 (8 rows, 61KB, 11.7s)

### Test results
```
tests/test_app_routes.py        15/15 passed (2 new: techai_editor_page, techai_items_api)
tests/channels/test_fixtures.py  5/5 passed
Total: 20/20 passed
```

### Files changed
- app.py — /techai-editor route, /api/techai/items CRUD, _techai_items_to_rows()
- static/techai_editor.html — new file (editor UI)
- channels/techai/items.json — seeded 8 sample items
- tests/test_app_routes.py — 2 new tests
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 15B] April 2026 — News Overhaul + Transfer Fix + Sport Mocks
**Phase:** 15B | **Status:** ✅ Complete

### What was built
- News: complete RSS overhaul — per-country feeds for 10 regions
  - USA, UK, Turkey, China, India, Saudi Arabia, Germany, Brazil, Japan, France
  - Top 5 headlines per country, flag+country grouping
  - BBC regional RSS feeds (free, reliable)
- Transfer: sample data fallback when RSS+Claude yields < 3 rows
  - 8 realistic sample transfers (Wirtz, Williams, Isak, Gyokeres, etc.)
  - Confirmed deals + rumours with proper layout
- Sports: MOCK_DATA=1 environment variable for all 7 sport channels
  - Skips API entirely when set — instant mock data
  - Realistic mock data: futbol(7), basket(4), tenis(3), motor(3), dovus(2), amerikan(2), voley(2)
- All 13 channels generate reels: output/phase15b/*.mp4

### Test results
```
tests/test_app_routes.py        13/13 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 18/18 passed
```

### Reel outputs (output/phase15b/)
```
finance     2023KB   78.3s     music       2528KB   87.0s
news        2576KB   59.4s     games        465KB   26.6s
techai       285KB   18.0s     transfer     330KB   20.9s
futbol       373KB   26.0s     basket       181KB   16.4s
tenis        141KB   13.6s     motor        152KB   13.6s
dovus         98KB   11.7s     amerikan     109KB   11.7s
voley        117KB   14.1s
```

### Files changed
- channels/news/news_fetcher.py — complete rewrite (per-country RSS)
- channels/transfer/transfer_fetcher.py — sample data fallback
- fetcher.py — MOCK_DATA dict + skip-API-when-set logic
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 15A] April 2026 — Bug Fixes + Reel Config UI
**Phase:** 15A | **Status:** ✅ Complete

### What was built
- Fixed: header accent underline artifact — removed draw_text_shadow, explicit bar positioning
- Fixed: footer channel name dark overlay — brighter accent (+50), no shadow calls
- Added: /reel-config UI — per-channel header, footer, colors, speed, frequency
  - Config saved to channels/{channel}/reel_config.json
  - make_reel() auto-reads config overrides (header_text, footer_text, colors, speed)
  - reel_speed multiplier: 1.0x=40px/s, 1.5x=60px/s, 2.0x=80px/s
- Music: renamed to WEEKLY WORLD TOP 5, "NEW" label replaced with star symbol
- Text truncation: score/song titles auto-truncated with "..." if too wide
- Added truncate_text() helper to video_maker.py

### Test results
```
tests/test_app_routes.py        13/13 passed (2 new: reel_config_page, reel_config_api)
tests/channels/test_fixtures.py  5/5 passed
Total: 18/18 passed
```

### Files changed
- video_maker.py — header/footer fixes, reel_config override, truncate_text, json import
- app.py — /reel-config route, GET/POST /api/reel-config/{channel}
- static/reel_config.html — new file (Reel Config UI)
- channels/music/music_fetcher.py — NEW→star symbol
- tests/test_app_routes.py — 2 new tests
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 14] April 2026 — Visual QA Fixes + Sport Reels
**Phase:** 14 | **Status:** ✅ Complete

### What was built
- 1.5x scroll speed (40 → 60 px/s) — finance 115s→78s, music 128s→87s
- Header: removed sport name second line, enlarged date/week text (36→48px)
- Footer: fixed visibility — Subscribe text brighter, channel handle brighter accent
- Finance disclaimer: larger font (18→22px), brighter color
- Row backgrounds: alternating light/dark contrast (both even+odd now draw)
- Font brightness increased: team/item names 195→225 across all channels
- Wide-row mode text also brightened for techai/news
- Per-channel header_title updates:
  - finance→WEEKLY MARKETS, games→WEEKLY GAME NEWS
  - music→WEEKLY WORLD BILLBOARD, news→WEEKLY WORLD NEWS
  - transfer→WEEKLY TRANSFER NEWS
- Test reels in output/phase14/ (sport channels: 0 rows due to API quota)
- Delisted ticker fixes: TAVHL.IS, TOTS3.SA

### Test results
```
tests/test_app_routes.py        11/11 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 16/16 passed
```

### Reel outputs
```
finance     2022KB   78.3s
music       2551KB   87.0s
games        464KB   26.6s
techai       285KB   18.0s
news         162KB   14.1s
transfer      95KB   11.7s
```

### Files changed
- video_maker.py — scroll speed, header, footer, row bg, font brightness
- channels/finance/finance_fetcher.py — ticker fixes
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 13] April 2026 — Header Titles + Visual QA Reels
**Phase:** 13 | **Status:** ✅ Complete

### What was built
- Per-channel header titles in video_maker.py SPORT_IDENTITY:
  - Sports/basket/tenis/motor/dovus/amerikan/voley/diger: "WEEKLY SCORES"
  - fixtures: "UPCOMING FIXTURES" | transfer: "TRANSFERS"
  - finance: "WEEKLY MARKETS" | music: "WEEKLY CHARTS"
  - techai: "AI & TECH WEEKLY" | news: "WORLD NEWS" | games: "GAMING WEEKLY"
- generate_header() reads header_title dynamically via ident.get()
- Fixed delisted tickers: KOZAA.IS -> TAVHL.IS, CPLE6.SA -> TOTS3.SA
- Test reels generated in output/phase13/:
  - finance:  47 rows, 2521KB, 115.0s
  - music:    55 rows, 3231KB, 128.0s
  - techai:    8 rows,  330KB,  24.6s
  - news:      8 rows,  351KB,  25.8s
  - games:    13 rows,  560KB,  37.4s
  - transfer:  1 row,   105KB,  15.0s

### Test results
```
tests/test_app_routes.py        11/11 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 16/16 passed
```

### Files changed
- video_maker.py — header_title in all 15 SPORT_IDENTITY entries, generate_header() dynamic
- channels/finance/finance_fetcher.py — TAVHL.IS, TOTS3.SA ticker fixes
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 12] April 2026 — Channel Manager Overhaul
**Phase:** 12 | **Status:** ✅ Complete

### What was built
- 12.1: Old Studio UI (index.html) replaced with redirect to /channel
- 12.2: Date range fetch fix — presets read fresh at click time
- 12.3: Music all-continents fetch + 18 countries (was 11)
  - fetch_all() returns all continents in one call
  - Added: Italy, Netherlands, Sweden, Argentina, Chile, Philippines, Indonesia
  - Removed continent tabs — single Fetch Data button
- 12.4: Delisted finance tickers replaced
  - DPW.DE → DHL.DE, STM.PA → STM (NYSE), KOZAL.IS → KOZAA.IS
  - BOVESPA: removed BRFS3/NTCO3/JBSS3, added UGPA3/CPLE6/VIVT3
- 12.5: Finance/league filter chips in channel.html
- 12.6: News continent/country geo + highlights
  - SOURCE_GEO mapping (BBC→UK, TechCrunch→USA, etc.)
  - Highlights in time field (80 chars of summary)
  - to_reel_groups includes continent field
- 12.7: Games combined fetch (Steam+Deals in one call)
  - fetch_combined() method, relaxed Steam filter (10 games now)
  - Removed games format tabs — single Fetch Data button
- 12.8: Transfer RSS expanded + more fallback keywords
  - Added The Athletic RSS feed
  - 18 transfer keywords (was 7)

### Test results
```
tests/test_app_routes.py        11/11 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 16/16 passed
```

### Verified outputs
- Music fetch_all: 45 rows, 8 countries
- Games combined: 13 rows (10 Steam + 3 Deals)
- News: 8 rows with continent geo
- Finance: delisted tickers replaced

### Files changed
- static/index.html — redirect to /channel
- static/channel.html — date fix, removed tabs, combined fetches
- channels/music/music_fetcher.py — fetch_all(), 18 countries
- channels/finance/finance_fetcher.py — ticker replacements
- channels/news/news_fetcher.py — SOURCE_GEO, highlights, continent
- channels/games/games_fetcher.py — fetch_combined(), relaxed filter
- channels/transfer/transfer_fetcher.py — +1 RSS, +11 keywords
- app.py — music fetch_all, games combined routing
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status

---

## [Sprint 11] April 2026 — Channel Manager Bug Fixes
**Phase:** 11 | **Status:** ✅ Complete

### What was fixed
- Bug 1: Stock names showing ticker codes instead of company names
  - Added TICKER_NAMES dict with 180 entries (NIKKEI, KOSPI, BIST100, BOVESPA, DAX, FTSE100, CAC40)
  - "6501.T" now shows "Hitachi", "005930.KS" shows "Samsung Elec", "GARAN.IS" shows "Garanti BBVA"

- Bug 2: Crypto not showing in Finance
  - Enhanced _fetch_crypto() with detailed logging (status code, data keys, per-coin checks)
  - Fixed change=None crash with `or 0` fallback
  - Changed price format: `$price:,.2f` for consistent decimal display
  - Note: CoinGecko still fails on SSL-restricted networks (known infra issue)

- Bug 3: Toggle on/off rendering + AI description
  - Fixed row toggle onclick: uses JSON.stringify for safe ID escaping
  - Fixed CSS: `.hidden-row` class with opacity+strikethrough on `.row-home`
  - AI description button always visible, shows inline error on failure
  - Added descError state for clear error display

- Bug 4: Data lost when switching channels
  - Added CHANNEL_DATA object: persists fetched rows across channel switches
  - Added sessionStorage backup: survives page refresh within session
  - Cache badge shows fetch timestamp per channel
  - Sidebar shows row counts for all channels with data

- Bug 5: Date range presets
  - Added preset buttons: Today, This Week, This Month, Custom
  - Fixtures gets "Next 7 Days" preset
  - Smart defaults per channel: finance→Today, music→Week, fixtures→Next7
  - Custom mode shows from/to date inputs

- Improvement: Channel-specific AI description prompts
  - 8 tailored prompts (finance=market analyst, music=journalist, etc.)
  - Prompts include role, tone, and specific instructions per channel

### Test results
```
tests/test_app_routes.py        11/11 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 16/16 passed
```

### Files changed
- channels/finance/finance_fetcher.py — TICKER_NAMES dict, name lookup, crypto logging
- static/channel.html — data persistence, date presets, toggle fixes, description errors
- app.py — DESCRIPTION_PROMPTS dict, channel-specific prompts
- docs/CHANGELOG.md — this entry
- docs/CLAUDE.md — phase status updated

---

## [Sprint 10] April 2026 — Channel Manager UI
**Phase:** 10 | **Status:** ✅ Complete

### What was built
- Task 10.1: GET /channel route serving channel.html
- Task 10.2: POST /api/channel/description — Claude AI description generator
  - Uses Claude Haiku 4.5 to generate YouTube Shorts descriptions
  - Sends visible row data as context, returns 1 paragraph + hashtags
- Task 10.3: static/channel.html — complete single-page Channel Manager
  - Left sidebar: 8 channels (finance, music, techai, news, transfer, games, sports, fixtures)
  - 5 collapsible sections: Theme, Music, Data, Description, Action
  - **Theme**: 16 color palettes (Dark Blue through Rose Gold), per-channel selection
  - **Music**: upload custom MP3, browse Pixabay free tracks, volume slider
  - **Data**: fetch + preview with continent→country grouping, row toggles (show/hide),
    league filter chips, music continent tabs, games format tabs
  - **Description**: AI generation with lock/unlock, editable textarea
  - **Action**: Reel Üret button with download link, summary bar
  - All settings persist in localStorage per channel
- Task 10.4: video_maker.py custom_theme support
  - make_reel() accepts custom_theme={bg,accent,dim} to override SPORT_IDENTITY
  - Temp injection pattern: custom theme injected/cleaned per call
- Task 10.5: auto_text_colors() helper in video_maker.py
  - Calculates luminance-based text colors for any accent

### Test results
```
tests/test_app_routes.py        11/11 passed
tests/channels/test_fixtures.py  5/5 passed
Total: 16/16 passed
```

### Files changed
- app.py                    — /channel route, /api/channel/description, custom_theme in make-reel
- static/channel.html       — new file (Channel Manager UI)
- video_maker.py            — custom_theme param, auto_text_colors()
- tests/test_app_routes.py  — 2 new tests (channel page, description API)
- docs/CHANGELOG.md         — this entry
- docs/CLAUDE.md            — phase status updated
- docs/ARCHITECTURE.md      — new routes added

---

## [Sprint 9] April 2026 — Finance Redesign + Music Country Level + Scroll Fix
**Phase:** 9 | **Status:** ✅ Complete

### What was built
- Task 9.1: Scroll fix in video_maker.py
  - Removed 180s duration cap — reel now ends when last row scrolls off screen
  - Added 2s PAUSE_BOTTOM after last row exits (no abrupt cut)
  - 50-row test: 96s duration (was capped at 180s before, now unbounded)

- Task 9.2: Finance redesign in finance_fetcher.py
  - Expanded MARKETS: 9 exchanges, 20 tickers each (was 8 exchanges, 3-5 tickers)
  - Added CAC40 (France) — 4 European markets now
  - Batch download via yfinance.download() (was 1-by-1 with 0.3s sleep)
  - Top 3 gainers + top 2 losers per market (smart selection)
  - Country-level grouping: category="🇩🇪 Germany", continent="EUROPE"
  - New commodities: Gold (XAU) + Silver (XAG) via batch download
  - Schedule changed: Weekly Friday 18:00 UTC (was daily 22:30 UTC)
  - Updated to_reel_groups() for continent→country hierarchy

- Task 9.3: Music country-level in music_fetcher.py
  - Per-country top 5 (was merged continent top 10)
  - COUNTRIES dict with flags: 🇬🇧🇩🇪🇫🇷🇪🇸🇹🇷🇺🇸🇧🇷🇲🇽🇯🇵🇰🇷🇮🇳
  - ~25 rows per continent (5 countries × 5 songs for Europe)
  - category="🇬🇧 UK", continent="EUROPE" — same pattern as finance

- Task 9.4: group_by_continent() fixed in sports_daemon.py
  - Now uses row.get("continent") before row.get("category") for grouping
  - display_name shows "🇩🇪 Germany · DAX" for country-level channels
  - CONTINENT_ORDER expanded: ASIA, COMMODITIES added
  - CONTINENT_COLORS in video_maker.py: ASIA, COMMODITIES, CRYPTO added
  - cron_day_of_week support added to scheduler

### Test results
```
tests/test_app_routes.py        9/9 passed
tests/channels/test_fixtures.py 5/5 passed
Total: 14/14 passed
```

### Files changed
- video_maker.py                        — scroll fix (no 180s cap, PAUSE_BOTTOM)
- channels/finance/finance_fetcher.py   — full redesign (batch, country, commodities)
- channels/music/music_fetcher.py       — country-level top 5
- sports_daemon.py                      — continent field, cron_day_of_week
- config.json                           — finance schedule weekly Friday
- docs/modules/FINANCE.md              — redesigned doc
- docs/modules/MUSIC.md               — country-level doc
- docs/CHANGELOG.md                    — this entry
- docs/CLAUDE.md                       — phase status updated

---

## [Sprint 8] April 2026 — Fixtures Rate Limit Fix
**Phase:** 8 | **Status:** ✅ Complete

### What was built
- Task 8.1: Diagnosed SportAPI rate limit — 429 MONTHLY quota (50 req/month BASIC plan)
  Not per-minute — retries/backoff alone won't help
- Task 8.2: Implemented 3-layer fix in fixtures_fetcher.py:
  1. Range-level cache with 6h TTL (avoids redundant API calls)
  2. Stale cache fallback when API fails
  3. Monthly quota detection — stops immediately on "MONTHLY" in 429 response
  4. FIXTURES_CACHE_ONLY env var for tests/quota protection
  5. Increased sleep to 2s between requests (conserve 50/month)
- Task 8.3: Verified graceful degradation — 0 rows, no crash
- Task 8.4: Added _cache_age_hours() to BaseFetcher (available to all channels)
- Updated SPORTS.md with correct quota info (50/month, not 100/day)

### Test results
```
tests/test_app_routes.py        9/9 passed
tests/channels/test_fixtures.py 5/5 passed
Total: 14/14 passed
```

### Files changed
- channels/fixtures/fixtures_fetcher.py — 6h cache, retry, quota detection
- channels/base_fetcher.py             — _cache_age_hours() added
- docs/modules/SPORTS.md               — rate limit info corrected
- docs/CHANGELOG.md                    — this entry
- docs/CLAUDE.md                       — phase status updated

---

## [Sprint 7] April 2026 — Production Go-Live
**Phase:** 7 | **Status:** ✅ Complete

### What was built
- Task 7.1: datetime.utcnow() deprecation fixed — 10 files, 13 occurrences
  (utcnow + utcfromtimestamp → datetime.now(timezone.utc))
- Task 7.2: All schedules enabled — 12/13 (asiapac paused)
- Task 7.3: Production smoke test passed — 6/7 channels, 0 crashes
  finance 1,416KB · music 406KB · techai 328KB · news 282KB ·
  games 145KB · transfer 118KB · fixtures ⚠️ (SportAPI rate limit)
- Task 7.4: AI channels verified with live ANTHROPIC_API_KEY
  techai → BIG TECH categories ✅ | news → POLITICS categories ✅
- Task 7.5: scripts/start_daemon.sh finalized (venv + .env + key checks)

### Test results
tests/test_app_routes.py    9/9 passed (0 deprecation warnings)

### Files changed
- channels/*/  — datetime.utcnow() fixed (10 files)
- config.json  — 12/13 schedules enabled
- scripts/start_daemon.sh — production-ready version
- CHANGELOG.md — this entry
- CLAUDE.md    — phase status updated

### Pending (Phase 8)
- YouTube credentials.json → automated uploads (Fatih to configure)
- PANDASCORE_KEY → esports live data
- RAWG_KEY → game releases
- fixtures channel → SportAPI rate limit issue
- Visual QA of generated reels (open MP4s, check layout)

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
