# NEXT_SESSION_PROMPT.md — Phase 8
> Phase 7 complete. Next: YouTube upload + visual QA + content quality.

## Phase 8 Focus Areas

### 8.1 YouTube Upload (HIGH)
- Fatih places credentials.json in project root
- Run: python youtube.py --auth
- Run: python youtube.py --test-upload
- If success: set youtube_enabled: true in config.json
- Test scheduler auto-upload with one real channel

### 8.2 Visual QA (HIGH)
- Open all 6 output/phase7/*.mp4 files
- Check: header readable, text not truncated, scroll smooth, footer correct
- Report any layout issues (text overflow, wrong colors, wrong theme)
- Fix issues in video_maker.py

### 8.3 Fixtures Channel Fix (MEDIUM)
- SportAPI rate limit causes fixtures to return 0 rows
- Options:
  A) Add longer delay between API calls (time.sleep)
  B) Use cache more aggressively (cache fixtures for 24h)
  C) Switch to football-data.org free fixtures endpoint

### 8.4 Stack Update (LOW)
- CLAUDE.md shows Python 3.11 but actual is 3.14.3 — update doc
- APScheduler 3.11.2 installed — verify no breaking changes
- venv name: amn — document in CLAUDE.md
