# NEXT_SESSION_PROMPT.md — Phase 8
> Version: 3.0 | Workflow: Claude.ai (PM) <-> Claude Code (Dev)
> Paste the STEP 1 block into Claude Code first.

---

## STEP 1 — Paste into Claude Code (READ & REPORT)

```
You are the developer on Ayaz Media Network.
Before any work, read the project state and report to Claude.ai (the PM).

Project path: /Users/fatihayaz/Documents/Projects/ayaz_media_network

Run this startup sequence:

# 1. Read core docs
cat docs/CLAUDE.md | head -60
echo "---CHANGELOG TAIL---"
tail -50 docs/CHANGELOG.md

# 2. Activate venv and run smoke test
source amn/bin/activate
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
from dotenv import load_dotenv
load_dotenv()
keys = ['ANTHROPIC_API_KEY','RAPIDAPI_KEY','PANDASCORE_KEY','RAWG_KEY']
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

echo "--- Schedules ---"
python -c "
import json
c = json.load(open('config.json'))
for s in c['schedules']:
    print(s['id'], '✅' if s['enabled'] else '⏸ ')
"

echo "--- Git ---"
git status --short
git log --oneline -5

# 4. Report format:
echo ""
echo "=== REPORT FOR CLAUDE.AI ==="
echo "Tests: [X/9 passing]"
echo "Fonts: [status]"
echo "API keys set: [list]"
echo "YouTube: [configured/not configured]"
echo "Schedules: [X/13 enabled]"
echo "Git: [clean/X modified files]"
echo "Ready for: Phase 8"
```

**Wait for Claude.ai response before doing any work.**

---

## Phase 8 Focus Areas

1. **YouTube Upload Pipeline** — credentials.json setup + first test upload
2. **SportAPI Rate Limits** — caching strategy or plan upgrade
3. **Optional API Keys** — PANDASCORE_KEY (esports), RAWG_KEY (game releases)
4. **CoinGecko SSL** — investigate and fix SSL error on crypto fetcher
5. **Asia-Pacific Schedule** — re-enable when rate limits resolved
6. **Monitoring** — daemon health checks, log rotation, error alerts
