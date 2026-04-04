# Ayaz Media Network

Automated YouTube Shorts/Reels generator for 13 content channels.
Fetches live data from APIs and RSS feeds, generates 1080x1920 MP4 reels, and uploads to YouTube.

## Channels

| Channel  | Type      | Data Source              | Header Title           |
|----------|-----------|--------------------------|------------------------|
| futbol   | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| basket   | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| tenis    | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| motor    | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| dovus    | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| amerikan | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| voley    | Sport     | SportAPI / Mock          | WEEKLY SCORES          |
| finance  | Markets   | yfinance (180 tickers)   | WEEKLY MARKETS         |
| music    | Charts    | Apple Music RSS (18 countries) | WEEKLY WORLD TOP 5 |
| news     | News      | BBC RSS (10 regions)     | WEEKLY WORLD NEWS      |
| games    | Gaming    | Steam + CheapShark       | WEEKLY GAME NEWS       |
| techai   | Tech/AI   | Manual editor / RSS      | AI & TECH WEEKLY       |
| transfer | Transfers | RSS + Claude AI + samples| WEEKLY TRANSFER NEWS   |

## Setup

```bash
git clone https://github.com/fatihayaz78/ayaz_media_network
cd ayaz_media_network
python -m venv amn && source amn/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys
python app.py          # starts on port 5052
```

### Required system dependencies
- Python 3.12+
- ffmpeg 6.0+

### Optional API keys (.env)
- `ANTHROPIC_API_KEY` — Claude AI for news/transfer curation
- `RAPIDAPI_KEY` — SportAPI for live sports data
- `PANDASCORE_KEY` — esports data
- `RAWG_KEY` — game releases

## Web UI (port 5052)

| Route            | Page                                    |
|------------------|-----------------------------------------|
| `/channel`       | Channel Manager (fetch, preview, reel)  |
| `/techai-editor` | Techai manual news editor               |
| `/upload`        | YouTube upload + history                |
| `/reel-config`   | Per-channel reel + YouTube config       |
| `/scheduler`     | APScheduler status + manual triggers    |

## Architecture

```
Data Sources (APIs/RSS)
        |
        v
Channel Fetchers (channels/*.py)
        |
        v
group_by_continent() (sports_daemon.py)
        |
        v
video_maker.py -> 3-layer reel: Header + Scrolling Content + Footer
        |
        v
Output: 1080x1920 MP4 (ffmpeg, libx264)
        |
        v
youtube.py -> YouTube Data API v3 upload
```

## Tests

```bash
pytest tests/test_app_routes.py tests/channels/test_fixtures.py -v
# 23/23 passing
```

## Phase History

- Phase 1-5: Core scaffold, 8 channels, Studio UI, Scheduler
- Phase 6-8: Production readiness, fonts, env, rate limit fixes
- Phase 9: Finance redesign (180 tickers), music country level, scroll fix
- Phase 10: Channel Manager UI, 16 color palettes, AI descriptions
- Phase 11: Bug fixes (tickers, toggles, persistence, date presets)
- Phase 12: Music all-continents, news geo, games combined fetch
- Phase 13-14: Per-channel headers, visual QA, 1.5x scroll speed
- Phase 15A-C: Reel config UI, news RSS overhaul, techai editor
- Phase 16: YouTube upload integration + upload UI

## License

Private project. All rights reserved.
