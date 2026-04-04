# ARCHITECTURE.md — Ayaz Media Network v2.0
> Updated: April 2026 — All 8 channels complete

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AYAZ MEDIA NETWORK                       │
│                 8 Channels · 13 Schedules                   │
└─────────────────────────────────────────────────────────────┘

    External APIs           Claude AI           Config JSON
    ┌──────────┐           ┌─────────┐         ┌──────────┐
    │SportAPI7 │           │ Haiku   │         │schedules │
    │yfinance  │           │ 4.5     │         │league_   │
    │Apple RSS │           │         │         │display   │
    │CheapShark│           └────┬────┘         └────┬─────┘
    │Steam API │                │                   │
    │RSS Feeds │                │                   │
    └────┬─────┘                │                   │
         │                      ▼                   │
         │            ┌─────────────────┐           │
         └───────────►│ Channel Fetcher │◄──────────┘
                      │ BaseFetcher     │
                      │ subclass        │
                      └───────┬─────────┘
                              │ List[Row]
                              │ {home,score,away,league,category,...}
                              ▼
                      ┌───────────────┐
                      │ group_by_     │
                      │ continent()   │
                      └───────┬───────┘
                              │ continents[]
                              ▼
                      ┌───────────────┐
                      │ video_maker   │
                      │ make_reel()   │
                      │               │
                      │ HEADER(fixed) │
                      │ CONTENT(scroll│
                      │ FOOTER(fixed) │
                      └───────┬───────┘
                              │ 1080×1920 MP4
                              ▼
                    ┌─────────────────────┐
                    │    Output Handler   │
                    │  /output/{name}.mp4 │
                    │  YouTube upload     │
                    │  (if enabled)       │
                    └─────────────────────┘
```

---

## Universal Data Contract

**Every fetcher returns `List[Dict]` with these fields.**
`video_maker.py` reads only these fields — nothing else.

```python
Row = TypedDict("Row", {
    "id":       str,   # unique (prevents duplicates in dedup)
    "home":     str,   # LEFT column
    "score":    str,   # CENTER column ("" = wide row mode)
    "away":     str,   # RIGHT column ("" = wide row mode)
    "league":   str,   # group name → LEAGUE_COLORS lookup
    "category": str,   # continent/section → group_by_continent()
    "time":     str,   # small label (time, ticker, platform...)
    "status":   str,   # badge (FT, ▲, NEW, ✓ DONE, ⭐⭐⭐)
})
```

### Channel Mappings

```python
# @ayaz_sports / @ayaz_fixtures
home  = "Manchester City"    away  = "Arsenal"
score = "3 – 1"              status = "FT"

# @ayaz_fixtures (upcoming)
home  = "Real Madrid"        away  = "Bayern Munich"
score = "vs"                 status = "21:00"

# @ayaz_finance
home  = "Apple"              away  = "+1.24%"
score = "$189.40"            status = "▲"  (or "▼")

# @ayaz_musics
home  = "1 ↑"               away  = "Sabrina Carpenter"
score = "Espresso"           status = "3w"

# @ayaz_techai / @ayaz_news  (WIDE ROW MODE — score is empty)
home  = "🤖 Anthropic"      away  = "Sonnet 4.6 released"
score = ""                   status = "NEW"
# time = "Extended thinking · faster"  ← line2

# @ayaz_transfer
home  = "Kylian Mbappé"      away  = "PSG → Real Madrid"
score = "€180M"              status = "✓ DONE"

# @ayaz_gamezs (steam)
home  = "#1 Counter-Strike 2" away = "players"
score = "1.2M"               status = "PEAK"

# @ayaz_gamezs (deals)
home  = "Red Dead Redemption" away = "-80%"
score = "$11.99"             status = "SALE"
```

---

## Wide Row Mode

When `score == ""`, `video_maker.py` renders a 2-line full-width row:
```
🤖 Anthropic                    ← home (small, muted, left)
Claude Sonnet 4.6 released      ← away (bold, bright)
Extended thinking · faster      ← time (small, dim)
```

Used by: `@ayaz_techai`, `@ayaz_news`

---

## Fetcher Registry

| source value | Class | File |
|---|---|---|
| `"sportapi"` (default) | fetch_sport() | fetcher.py |
| `"fixtures"` | FixturesFetcher | channels/fixtures/ |
| `"finance"` | FinanceFetcher | channels/finance/ |
| `"music"` | MusicFetcher | channels/music/ |
| `"techai"` | TechAIFetcher | channels/techai/ |
| `"transfer"` | TransferFetcher | channels/transfer/ |
| `"news"` | NewsFetcher | channels/news/ |
| `"games"` | GamesFetcher | channels/games/ |

Routing via `get_channel_rows()` in `sports_daemon.py`.
Also via `/api/fetch/channel` in `app.py`.

---

## Scheduling

```
sports_daemon.py (APScheduler, timezone=UTC)

Schedule ID      Source      Cron              Enabled
─────────────────────────────────────────────────────
europe           sportapi    Daily 22:00        ✅
americas         sportapi    Daily 06:00        ✅
global           sportapi    Mon 10:00          ✅
asiapac          sportapi    Daily 14:00        ❌
fixtures         fixtures    Mon 07:00          ❌
finance          finance     Daily 22:30        ❌
music_europe     music       Fri 08:00          ❌
music_americas   music       Fri 09:00          ❌
music_asia       music       Fri 10:00          ❌
techai           techai      Mon 08:00          ❌
transfer         transfer    Daily 09:00        ❌
news             news        Daily 06:00        ❌
games_deals      games       Daily 12:00        ❌

Enable in config.json: "enabled": true
```

---

## Flask API Routes

```
GET  /                            → index.html (Studio UI)
GET  /channel                     → channel.html (Channel Manager)
GET  /scheduler                   → scheduler.html (Scheduler UI)

# Sports (legacy)
GET  /api/fetch
     ?sport_id=futbol
     &from=2026-04-01&to=2026-04-03

# All channels (new)
GET  /api/fetch/channel
     ?channel_id=finance          → FinanceFetcher
     ?channel_id=music
       &continent=EUROPE          → MusicFetcher(continent)
     ?channel_id=games
       &fmt=steam_charts          → GamesFetcher(fmt)
     ?channel_id=techai           → TechAIFetcher
     ?channel_id=news             → NewsFetcher
     ?channel_id=transfer         → TransferFetcher
     ?channel_id=fixtures         → FixturesFetcher

POST /api/channel/description     → Claude AI YouTube description
POST /api/make-reel               → Generate MP4 (supports custom_theme)
GET  /api/download/{filename}     → Download MP4
POST /api/upload-media            → Upload BG image/video
POST /api/music/upload            → Upload music file
GET  /api/music/tracks            → List Pixabay tracks
POST /api/music/download-pixabay  → Download track

GET  /api/scheduler/status        → All schedules + last runs
POST /api/scheduler/config        → Update config
POST /api/scheduler/run-now       → Trigger manually
GET  /api/scheduler/logs          → Last 100 log lines
POST /api/scheduler/daemon        → Start/stop
```

---

## Video Generation (ffmpeg)

```
Inputs:
  [0] background (color / image loop / video loop)
  [1] content_strip.png  (variable height, scrolls)
  [2] header.png         (1080 × 340, fixed)
  [3] footer.png         (1080 × 220, fixed)
  [4] music.mp3          (optional)

Filter graph:
  bg → scale 1080×1920
  [bg][content] overlay y='{scroll_expr}'  → v1
  [v1][header]  overlay 0:0               → v2
  [v2][footer]  overlay 0:1700            → out
  [music] volume + afade in/out           → aout

Scroll expr:
  if(t < pause_top,
    HEADER_H,
    max(HEADER_H - scroll_dist,
        HEADER_H - (t - pause_top) * scroll_speed))

Output: libx264, crf=22, preset=fast, yuv420p, aac 192k
```

---

## Caching Strategy

```
Rule:         Past dates → always cache (data won't change)
              Today      → never cache (incomplete data)
              Music      → weekly cache (chart data)
              TechAI     → weekly cache (news cycle)

Cache format: List[Dict] — standard row format
Cache paths:  cache/{channel_id}/{key}.json
TTL:          Infinite for past dates
```

---

## Dependencies

```bash
# Core
flask>=3.0
flask-cors
pillow>=10.0
requests
python-dotenv
apscheduler>=3.10

# Finance
yfinance>=0.2

# AI channels
anthropic>=0.25
feedparser>=6.0

# System (install separately)
ffmpeg>=6.0
```
