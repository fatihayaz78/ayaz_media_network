# Ayaz Media Network — Master Doc
> Version: 6.0 | April 2026

## SESSION START CHECKLIST
```bash
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network
source amn/bin/activate
pytest tests/test_app_routes.py tests/channels/test_fixtures.py -v --tb=short 2>&1 | tail -5
git log --oneline -3
git status --short
```
Report: `Tests: N/N | Git: [hash] | Port: 5052`

## DOCUMENTATION MAP
| File | Purpose | Read when |
|------|---------|-----------|
| CLAUDE.md | Master index, session rules | Every session |
| docs/ARCHITECTURE.md | Routes, data flow, file map | New feature/bug |
| docs/REELS_UI.md | Approved UI/UX + reel specs | UI work |
| docs/CHANGELOG.md | Sprint history | Context needed |
| docs/channels/finance.md | Finance channel | Finance work |
| docs/channels/music.md | Music channel | Music work |
| docs/channels/news.md | News channel | News work |
| docs/channels/sports.md | Sports channels | Sports work |
| docs/channels/techai.md | Techai channel | Techai work |
| docs/channels/transfer.md | Transfer channel | Transfer work |
| docs/channels/games.md | Games channel | Games work |
| docs/channels/fixtures.md | Fixtures channel | Fixtures work |

## CURRENT STATE
Build: Post-Audit | Tests: 31/31 | Git: e4ec3a2 | Port: 5052 | Venv: amn

## WHAT WORKS
- 36 Flask routes, all return 200
- Finance: 16 exchanges, 209 tickers, 17 forex, 6 metals, 5 crypto
- Music: 18 countries, 3 continents (Apple Music RSS)
- News: 10 BBC RSS regions
- Games: Steam Charts + CheapShark deals
- Techai: manual editor (items.json)
- Transfer: 4 RSS feeds + sample fallback
- Sports: MOCK_DATA=1 for 7 sports (API quota)
- Continent split: finance/music/news into 4 buckets
- Reel generation: MP4 via ffmpeg, auto-thumbnail
- Channel editor: /channel-editor/{ch}/{continent}
- YouTube upload: upload_video() with OAuth2

## WHAT IS NOT IMPLEMENTED
- Section dividers in reel video (STOCKS/FOREX/METALS/CRYPTO headers)
- Green/red % change colors in reel rows
- YouTube credentials.json (not configured)
- AFRICA music data sources
- CoinGecko live (SSL blocked, static fallback active)

## SPRINT PROTOCOL (mandatory)
BEFORE: Run checklist, read ARCHITECTURE.md, read relevant channel .md
DURING: Max 3 tasks, verify each with curl/python, paste raw output
AFTER: Update docs, run pytest, git commit+push, report with hash
RULE: Never mark done without pasted verification output
