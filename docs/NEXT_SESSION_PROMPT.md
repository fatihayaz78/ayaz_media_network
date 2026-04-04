# NEXT_SESSION_PROMPT.md — Phase 6
> Version: 2.0 | Workflow: Claude.ai (PM) ↔ Claude Code (Dev)
> Paste the STEP 1 block into Claude Code first.

---

## ⚡ STEP 1 — Paste into Claude Code (READ & REPORT)

```
You are the developer on Ayaz Media Network.
Before any work, read the project state and report to Claude.ai (the PM).

Project path: /Users/fatihayaz/Documents/Projects/ayaz_media_network

Run this startup sequence:

# 1. Read core docs
cat CLAUDE.md
echo "---CHANGELOG TAIL---"
tail -50 CHANGELOG.md

# 2. Run smoke test
python -m pytest tests/test_app_routes.py -v --tb=short 2>&1 | tail -25

# 3. Check known issue files
echo "--- Font check ---"
python -c "
from video_maker import FONTS
import os
for k,p in FONTS.items():
    print(k, '✅' if os.path.exists(p) else '❌ MISSING', p)
"

echo "--- API keys ---"
python -c "
import os
keys = ['ANTHROPIC_API_KEY','PANDASCORE_KEY','RAWG_KEY','FOOTBALL_DATA_KEY']
for k in keys:
    val = os.environ.get(k,'')
    print(k, '✅ SET' if val else '❌ NOT SET')
"

echo "--- YouTube ---"
python -c "
import os
print('credentials.json:', '✅' if os.path.exists('credentials.json') else '❌ MISSING')
print('token.json:', '✅' if os.path.exists('token.json') else '❌ MISSING')
"

echo "--- Git ---"
git status --short
git log --oneline -5

# 4. Report format — paste this back to Claude.ai:
echo ""
echo "=== REPORT FOR CLAUDE.AI ==="
echo "Tests: [X/9 passing]"
echo "Fonts: [status]"
echo "API keys set: [list]"
echo "YouTube: [configured/not configured]"
echo "Git: [clean/X modified files]"
echo "Blocking issues: [list from CHANGELOG Known Issues]"
echo "Ready for: Phase 6"
```

**Wait for Claude.ai response before doing any work.**

---

## ⚡ STEP 2 — Claude.ai reads the report, then gives this prompt

*(Claude.ai sends this after reading Claude Code's report)*

```
Based on your report, proceed with Phase 6 in this priority order.
Read the relevant module MD before each task. Update CHANGELOG after each task.

---

## TASK 6.1 — Fix Roboto Fonts

Read: docs/UI.md (font section)

Current state: GOOGLE_FONTS URLs in video_maker.py return 404.
Falling back to system fonts (Helvetica/DejaVu) — works but not ideal.

Try these replacement URLs in order until one works:

Option 1 (Google Fonts CDN):
```python
GOOGLE_FONTS = {
    "regular": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5WhmBKs.woff",
    "bold":    "https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmWUlfBBc9.woff",
    "italic":  "https://fonts.gstatic.com/s/roboto/v30/KFOkCnqEu92Fr1Mu51xGIzIX.woff",
}
```

Option 2 (Noto Sans — reliable GitHub raw):
```python
FONTS = {
    "regular": os.path.join(FONT_DIR, "NotoSans-Regular.ttf"),
    "bold":    os.path.join(FONT_DIR, "NotoSans-Bold.ttf"),
    "italic":  os.path.join(FONT_DIR, "NotoSans-Italic.ttf"),
}
GOOGLE_FONTS = {
    "regular": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "bold":    "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    "italic":  "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Italic.ttf",
}
```

Option 3 (manual install script):
```bash
mkdir -p fonts
pip install requests
python -c "
import requests, os
fonts = {
    'Roboto-Regular.ttf': 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf',
    'Roboto-Bold.ttf':    'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf',
    'Roboto-Italic.ttf':  'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Italic.ttf',
}
for name, url in fonts.items():
    r = requests.get(url, timeout=30)
    open(f'fonts/{name}', 'wb').write(r.content)
    print(f'{name}: {len(r.content)//1024}KB')
"
```

Test after each option:
```bash
python -c "
from video_maker import ensure_fonts, FONTS
import os
ensure_fonts()
for k,p in FONTS.items():
    exists = os.path.exists(p)
    size = os.path.getsize(p)//1024 if exists else 0
    print(k, '✅' if exists else '❌', f'{size}KB' if size else '')
"
```

Generate test reel to visually verify font quality:
```bash
python -c "
from video_maker import make_reel
make_reel({
    'channel_name': 'FontTest',
    'date': '$(date +%d.%m.%Y)',
    'continents': [{'name':'EUROPE','groups':[{
        'league':'Premier League',
        'display_name':'Premier League (England)',
        'matches':[
            {'id':'t1','home':'Manchester City','score':'3 – 1','away':'Arsenal','status':'FT','time':'20:45'},
            {'id':'t2','home':'Liverpool','score':'2 – 0','away':'Chelsea','status':'FT','time':'17:30'},
        ]
    }]}]
}, 'output/font_test.mp4', sport_id='futbol')
print('Open output/font_test.mp4 and check font rendering')
"
```

After fix:
- Update docs/UI.md font section with working URLs
- Update CHANGELOG.md: add entry under new "## [Sprint 6]" section

---

## TASK 6.2 — Fix TransferMarkt API

Read: docs/modules/TRANSFER.md

Current state: /v1/transfers/list and /v1/transfers/search both return 404.

Try football-data.org as replacement (free tier):
1. Register at https://www.football-data.org/client/register → get free API key
2. Add to .env: FOOTBALL_DATA_KEY=your_key
3. Update _fetch_confirmed() in channels/transfer/transfer_fetcher.py:

```python
FOOTBALL_DATA_KEY = os.environ.get("FOOTBALL_DATA_KEY", "")

def _fetch_confirmed(self, date_from: str, date_to: str) -> List[Dict]:
    if not FOOTBALL_DATA_KEY:
        print("[transfer] FOOTBALL_DATA_KEY not set")
        return []
    try:
        url = "https://api.football-data.org/v4/transfers"
        resp = requests.get(url,
            headers={"X-Auth-Token": FOOTBALL_DATA_KEY},
            params={"dateFrom": date_from, "dateTo": date_to},
            timeout=10)
        resp.raise_for_status()
        data = resp.json()
        transfers = data.get("transfers", [])
        rows = []
        for i, t in enumerate(transfers[:8]):
            player  = t.get("player", {}).get("name", "Unknown")[:22]
            from_cl = t.get("fromTeam", {}).get("name", "?")[:12]
            to_cl   = t.get("toTeam",   {}).get("name", "?")[:12]
            fee     = t.get("fee") or "Undisclosed"
            rows.append({
                "id":       f"tx-done-{i}",
                "home":     player,
                "score":    str(fee)[:12],
                "away":     f"{from_cl} → {to_cl}",
                "league":   "DONE DEALS",
                "category": "CONFIRMED",
                "time":     "",
                "status":   "✓ DONE",
            })
        return rows
    except Exception as e:
        print(f"[transfer] football-data.org error: {e}")
        return []
```

Test:
```bash
python -c "
from channels.transfer.transfer_fetcher import TransferFetcher
f = TransferFetcher()
rows = f._fetch_confirmed('2026-04-01', '2026-04-07')
print(f'Confirmed: {len(rows)}')
for r in rows[:3]: print(f'  {r[\"home\"]} | {r[\"score\"]} | {r[\"away\"]}')
"
```

Run tests: python -m pytest tests/channels/test_transfer.py -v

After fix:
- Update docs/modules/TRANSFER.md
- Update CHANGELOG.md

---

## TASK 6.3 — Set ANTHROPIC_API_KEY + Verify AI Channels

Read: docs/modules/TECHAI.md, docs/modules/NEWS.md, docs/modules/TRANSFER.md

If ANTHROPIC_API_KEY is set in .env, verify all 3 AI channels work with real Claude:

```bash
# Test each AI channel
python -c "
from channels.techai.techai_fetcher import TechAIFetcher
f = TechAIFetcher()
rows = f.fetch('2026-03-27', '2026-04-03')
cats = set(r['league'] for r in rows)
print(f'TechAI: {len(rows)} rows')
print(f'Categories: {cats}')
# Should show MODEL UPDATES, BIG TECH, TOOLS etc (not all BIG TECH)
"

python -c "
from channels.news.news_fetcher import NewsFetcher
f = NewsFetcher()
rows = f.fetch('2026-04-03', '2026-04-03')
cats = set(r['league'] for r in rows)
print(f'News: {len(rows)} rows')
print(f'Categories: {cats}')
# Should show POLITICS, ECONOMY, SCIENCE etc
"

python -c "
from channels.transfer.transfer_fetcher import TransferFetcher
f = TransferFetcher()
rows = f._fetch_rumours()
print(f'Rumours: {len(rows)}')
for r in rows[:3]:
    print(f'  {r[\"home\"]} | {r[\"away\"]} | {r[\"status\"]}')
# Should show player names and club arrows
"
```

If ANTHROPIC_API_KEY is NOT set: skip this task, note in report.

---

## TASK 6.4 — YouTube OAuth2 Setup Guide

Read: youtube.py (check what it expects)

Create docs/YOUTUBE_SETUP.md with exact steps:

```markdown
# YOUTUBE_SETUP.md
1. Go to console.cloud.google.com
2. Create project "ayaz-media-network"
3. Enable "YouTube Data API v3"
4. Credentials → Create → OAuth 2.0 Client ID → Desktop app
5. Download as credentials.json → place in project root
6. First auth: python youtube.py --auth
   (opens browser, sign in, grant permission)
7. token.json created automatically
8. Test: python -c "from youtube import build_title; print(build_title('{title}','Sports','ayaz'))"
9. Enable in config.json: "youtube_enabled": true
```

Also add test:
```python
# tests/test_youtube_auth.py
def test_youtube_credentials_documented():
    import os
    if not os.path.exists("credentials.json"):
        # Not configured — check docs exist
        assert os.path.exists("docs/YOUTUBE_SETUP.md"), \
            "YouTube not configured and docs/YOUTUBE_SETUP.md missing"
    # If credentials exist, verify format
    else:
        import json
        with open("credentials.json") as f:
            creds = json.load(f)
        assert "installed" in creds or "web" in creds
```

---

## TASK 6.5 — Production Reels Visual Check

Generate one MP4 per channel. Open each and verify visually.

```bash
mkdir -p output/phase6_test

python -c "
import os
from datetime import date, timedelta
from video_maker import make_reel

TODAY = date.today().strftime('%d.%m.%Y')
OUT   = 'output/phase6_test'

# finance
from channels.finance.finance_fetcher import FinanceFetcher
f = FinanceFetcher()
rows = f.fetch(date.today().strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d'))
groups = f.to_reel_groups(rows)
make_reel({'channel_name':'ayaz_finance','date':TODAY,'continents':[{'name':'MARKETS','groups':groups}]}, f'{OUT}/finance.mp4', sport_id='finance')
print(f'finance: {os.path.getsize(OUT+\"/finance.mp4\")//1024}KB')

# music
from channels.music.music_fetcher import MusicFetcher
f = MusicFetcher()
rows = f.fetch(continent='EUROPE')
groups = f.to_reel_groups(rows)
make_reel({'channel_name':'ayaz_musics','date':TODAY,'continents':[{'name':'CHARTS','groups':groups}]}, f'{OUT}/music.mp4', sport_id='music')
print(f'music: {os.path.getsize(OUT+\"/music.mp4\")//1024}KB')

# news
from channels.news.news_fetcher import NewsFetcher
f = NewsFetcher()
rows = f.fetch(date.today().strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d'))
groups = f.to_reel_groups(rows)
make_reel({'channel_name':'ayaz_news','date':TODAY,'continents':[{'name':'NEWS','groups':groups}]}, f'{OUT}/news.mp4', sport_id='news')
print(f'news: {os.path.getsize(OUT+\"/news.mp4\")//1024}KB')

print('Open output/phase6_test/ and check visually:')
print('  - Header: channel name, date, week number')
print('  - Content: readable text (not pixelated)')
print('  - Scroll: smooth animation')
print('  - Footer: @channel + SUBSCRIBE')
"
```

---

## AFTER ALL TASKS — Update Docs

```bash
# Update CHANGELOG with Sprint 6 entry
# Update relevant module docs
# Commit everything

git add -A
git commit -m "Phase 6: fonts fix, transfer API, AI channels verified, YouTube docs"
```

---

## FINAL REPORT TO CLAUDE.AI

```
Phase 6 Report:

Task 6.1 Fonts:    ✅/❌  [option used, KB size]
Task 6.2 Transfer: ✅/❌  [X confirmed deals found]
Task 6.3 Claude:   ✅/❌  [API key set? categories working?]
Task 6.4 YouTube:  ✅/❌  [credentials.json exists?]
Task 6.5 Reels:    ✅/❌  [finance XKB, music XKB, news XKB]

Remaining issues: [list]
Next phase suggestion: [what to build next]
```
```
