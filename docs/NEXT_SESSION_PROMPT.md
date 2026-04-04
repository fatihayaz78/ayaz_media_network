# NEXT_SESSION_PROMPT.md — Phase 13
> Phase 12 complete. Next: manual testing + UI visual QA + reel design.

## Context
Channel Manager UI is at http://localhost:5052/channel
Start app: cd /Users/fatihayaz/Documents/Projects/ayaz_media_network && source amn/bin/activate && python app.py

## Phase 13 Focus

### 13.1 Sports + Fixtures Manual Test
- Sports: test when API quota resets (not blocked by tests)
- Fixtures: test when monthly quota resets (~28 days)
- Verify continent/country grouping in channel.html

### 13.2 Reel UI Visual QA
Fatih will test each channel:
  1. Fetch Data -> pick color -> Reel Uret -> open MP4
  2. Check: header readable, scroll smooth, footer correct
  3. Report layout issues

Known items to check per channel:
  Finance:  continent->country hierarchy visible? gainers green, losers red?
  Music:    per-country top 5 visible? trend arrows correct?
  TechAI:   wide-row mode readable? categories correct?
  News:     highlights showing? category chips work?
  Transfer: player->club->fee columns readable?
  Games:    Steam+Deals in one reel?

### 13.3 Reel Design Decisions (Fatih to approve)
  - Header title text: "WEEKLY SCORES" -- change per channel?
    Finance -> "WEEKLY MARKETS"
    Music   -> "WEEKLY CHARTS"
    TechAI  -> "AI & TECH WEEKLY"
    News    -> "WORLD NEWS"
  - Font size: current 82px bold -- too large/small?
  - Content row height: current ~60px -- enough padding?
  - Scroll speed: 40px/s -- too fast/slow?

### 13.4 Bug Fixes from visual QA
Based on Fatih's feedback, fix layout issues.

## Session Startup (Claude Code)
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network
source amn/bin/activate
cat docs/CLAUDE.md
tail -40 docs/CHANGELOG.md
python -m pytest tests/test_app_routes.py -v --tb=short 2>&1 | tail -5
git log --oneline -3
git status --short
