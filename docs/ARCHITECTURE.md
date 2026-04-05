# Architecture

## Stack
Python 3.14.3, Flask 3.1.3, Pillow 12.2.0, ffmpeg, APScheduler 3.11.2, yfinance 1.2.0, feedparser 6.0.12, anthropic 0.89.0, google-api-python-client 2.193.0

## File Map
| File | Role |
|------|------|
| app.py | Flask app, 36 routes |
| video_maker.py | Reel engine: SPORT_IDENTITY (15 themes), CONTINENT_THEMES (4), header/content/footer |
| sports_daemon.py | Data routing, group_by_continent(), split_by_continent(), APScheduler |
| fetcher.py | SportAPI fetch + MOCK_DATA (7 sports, 23 rows) |
| youtube.py | YouTube Data API v3: OAuth2, upload_video(), thumbnail upload |
| thumbnail_maker.py | 1280x720 JPEG: 3-zone (gradient top + title center + branding bottom) |
| channels/base_fetcher.py | Abstract base: cache, deduplicate |
| channels/finance/finance_fetcher.py | yfinance: 16 exchanges, 209 tickers, 17 forex, 6 metals, 5 crypto |
| channels/music/music_fetcher.py | Apple Music RSS: 18 countries, 3 continents |
| channels/news/news_fetcher.py | BBC RSS: 10 regions, top 5 per region |
| channels/games/games_fetcher.py | Steam Charts + CheapShark deals |
| channels/techai/techai_fetcher.py | RSS or manual items.json |
| channels/transfer/transfer_fetcher.py | 4 RSS feeds + Claude AI + sample fallback |
| channels/fixtures/fixtures_fetcher.py | SportAPI upcoming fixtures |

## All Routes (36 total, all verified 200)

### Pages (8)
```
GET /                              → redirect to /channel
GET /channel                       → Channel Manager (continent tabs)
GET /channel-editor/<ch>           → Reel editor (base)
GET /channel-editor/<ch>/<cont>    → Reel editor (continent)
GET /upload                        → YouTube upload UI
GET /reel-config                   → Config editor (legacy)
GET /techai-editor                 → Manual AI news editor
GET /scheduler                     → APScheduler status
```

### Data APIs (4)
```
GET  /api/fetch                    → Sports fetch (legacy)
GET  /api/fetch/channel            → Unified fetch (all channels)
POST /api/channel/description      → AI description (Claude Haiku)
POST /api/make-reel                → Generate MP4 (legacy)
POST /api/make-reel/<ch>/<cont>    → Generate continent reel
GET  /api/download/<filename>      → Download MP4
GET  /api/download/<ch>/<file>     → Download continent MP4
```

### Config APIs (4)
```
GET/POST /api/reel-config/<ch>              → Base config
GET/POST /api/reel-config/<ch>/<cont>       → Continent config
```

### Upload APIs (7)
```
POST /api/upload-media             → Background image/video
GET  /api/music/tracks             → Pixabay tracks
POST /api/music/upload             → Custom music
POST /api/music/download-pixabay   → Download Pixabay track
POST /api/upload/youtube           → Upload to YouTube
GET  /api/upload/list-reels        → List MP4 files
GET  /api/upload/log               → Upload history
GET  /thumbnail/<channel>          → Latest thumbnail
```

### Techai APIs (4)
```
GET    /api/techai/items           → List items
POST   /api/techai/items           → Add item
DELETE /api/techai/items/<id>      → Delete
POST   /api/techai/items/<id>/feature → Toggle featured
```

### Scheduler APIs (5)
```
GET  /api/scheduler/status         → Schedules + runs
POST /api/scheduler/config         → Update config
POST /api/scheduler/run-now        → Manual trigger
GET  /api/scheduler/logs           → Last 100 lines
POST /api/scheduler/daemon         → Start/stop
```

## Data Flow: Finance
```
User → Fetch Data (This Week) → JS doFetch()
  → GET /api/fetch/channel?channel_id=finance&from=2026-03-28&to=2026-04-05
  → app.py → FinanceFetcher().fetch(date_from, date_to)
  → yf_period = "5d" (delta <=7)
  → _fetch_stocks(5d): batch yf.download per exchange → top 3 gainers + 2 losers
  → _fetch_forex(5d): batch yf.download 17 pairs
  → _fetch_metals(5d): batch yf.download 6 commodities
  → _fetch_crypto(): CoinGecko → SSL fallback → static
  → returns 91 rows
  → JS renders in table, grouped by continent/league
```

## Data Flow: Music
```
User → Fetch Data → JS doFetch()
  → GET /api/fetch/channel?channel_id=music
  → MusicFetcher().fetch_all()
  → for each continent: for each country: Apple Music RSS top 5
  → 18 countries × 5 songs = ~55 rows (some timeouts)
  → continent field set per row
```

## Continent System
```
CONTINENT_THEMES (video_maker.py):
  AMERICAS: accent=(220,38,38) red     bg=(10,5,5)
  EUROPE:   accent=(59,130,246) blue   bg=(5,8,20)
  ASIA:     accent=(234,179,8) gold    bg=(12,10,3)
  AFRICA:   accent=(34,197,94) green   bg=(3,10,5)

EXCHANGE_CONTINENT (sports_daemon.py):
  DAX/FTSE100/CAC40/BIST100 → EUROPE
  SP500/NASDAQ/BOVESPA/TSX → AMERICAS
  NIKKEI/KOSPI/SSE/BSE/HSI/TWSE/Tadawul → ASIA
  JSE/EGX30 → AFRICA
  FOREX/METALS/CRYPTO → GLOBAL

split_by_continent(rows):
  - Stocks: mapped by EXCHANGE_CONTINENT
  - Forex: mapped by row's continent field
  - Metals/Crypto (GLOBAL): copied to ALL 4 buckets
```

## Reel Generation
```
make_reel(config, output, sport_id, continent=None, custom_theme=None):
  1. Load reel_config.json overrides (header_text, footer_text, colors, speed)
  2. generate_header(sport_id, date, ident_override) → RGBA 1080×340
  3. generate_content_strip(config, sport_id) → RGBA 1080×variable
  4. generate_footer(sport_id, channel, ident_override) → RGBA 1080×220
  5. ffmpeg: overlay 3 layers, scroll content, encode MP4
  6. generate_thumbnail() → JPEG 1280×720
```

## Config Files
```
channels/{ch}/reel_config.json           → base channel config
channels/{ch}_{CONT}/reel_config.json    → continent override
channels/techai/items.json               → manual techai items
config.json                              → global schedules
data/upload_log.json                     → YouTube upload history
.env                                     → API keys (not committed)
```
