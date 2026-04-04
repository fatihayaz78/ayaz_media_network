# CLAUDE_CODE_MASTER_PROMPT.md
> Copy this entire prompt into Claude Code to start development.
> This is the single source of truth for all development sessions.

---

## PASTE INTO CLAUDE CODE — TAB 1 (MASTER)

```
You are a senior Python developer building "Ayaz Media Network" —
an automated YouTube Shorts production pipeline with 8 channels.

## FIRST: Read these files in order
1. CLAUDE.md          → Project rules and conventions
2. ARCHITECTURE.md    → Data flow and contracts  
3. UI.md              → Visual design spec
4. docs/channels/ALL_CHANNELS.md → All channel specs
5. docs/prompts/AI_PROMPTS.md    → Claude API prompts

## EXISTING PRODUCTION CODE (do not break)
- fetcher.py           → @ayaz_sports data fetcher
- video_maker.py       → MP4 generator (approved design)
- app.py               → Flask server
- sports_daemon.py     → APScheduler daemon
- config.json          → Master config

## PHASE 1 TASK: Project Scaffold

### 1. Create folder structure
```
channels/
├── __init__.py
├── base_fetcher.py
├── fixtures/
│   ├── __init__.py
│   └── fixtures_fetcher.py
├── finance/
│   ├── __init__.py
│   └── finance_fetcher.py
├── music/
│   ├── __init__.py
│   └── music_fetcher.py
├── techai/
│   ├── __init__.py
│   └── techai_fetcher.py
├── transfer/
│   ├── __init__.py
│   └── transfer_fetcher.py
├── news/
│   ├── __init__.py
│   └── news_fetcher.py
└── games/
    ├── __init__.py
    └── games_fetcher.py

tests/
├── __init__.py
├── test_video_maker.py
└── channels/
    ├── __init__.py
    ├── test_fixtures.py
    ├── test_finance.py
    ├── test_music.py
    └── test_techai.py

cache/
├── sports/     (existing)
├── fixtures/
├── finance/
├── music/
├── techai/
├── transfer/
├── news/
└── games/
```

### 2. Implement base_fetcher.py
```python
# channels/base_fetcher.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import os, json

class BaseFetcher(ABC):
    channel_id: str = ""
    sport_id: str = ""       # maps to SPORT_IDENTITY in video_maker.py
    
    @property
    def cache_dir(self) -> str:
        path = os.path.join(os.path.dirname(__file__), "..", "cache", self.channel_id)
        os.makedirs(path, exist_ok=True)
        return path

    @abstractmethod
    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        """Returns list of standard row dicts."""
        pass

    @abstractmethod  
    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        """
        Returns:
        [{"league": str, "display_name": str, "matches": [Row]}]
        
        Where Row = {home, score, away, status, time, league, id}
        """
        pass

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def _load_cache(self, key: str) -> Optional[List[Dict]]:
        path = self._cache_path(key)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_cache(self, key: str, data: List[Dict]):
        with open(self._cache_path(key), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
```

### 3. Implement fixtures_fetcher.py FIRST

Start with fixtures — it reuses the existing SportAPI credentials
and only needs a status filter change.

Key difference from fetcher.py:
```python
# sports fetcher: keep finished matches
is_finished = status_type in {"finished", "ended", "after extra time", ...}
if not is_finished: continue

# fixtures fetcher: keep upcoming matches  
is_upcoming = status_type in {"not_started", "scheduled", "tbd"}
if not is_upcoming: continue
```

Group by date (not by league):
```python
# Output format for fixtures:
[
  {
    "league": "MON · 07 Apr",      # date as group header
    "display_name": "Monday · April 7",
    "matches": [
      {
        "id": "sapi-12345",
        "home": "Real Madrid",
        "score": "vs",
        "away": "Bayern Munich",
        "league": "MON · 07 Apr",
        "status": "21:00",         # kickoff time as status
        "time": "UCL"              # competition as time label
      }
    ]
  }
]
```

### 4. Add new themes to video_maker.py

Add to SPORT_IDENTITY dict (additive only, never remove existing):
```python
"fixtures": {
    "name":   "UPCOMING FIXTURES",
    "bg":     (6, 16, 8),
    "accent": (64, 200, 112),
    "dim":    (18, 44, 24),
},
"transfer": {
    "name":   "TRANSFERS",
    "bg":     (18, 8, 0),
    "accent": (255, 140, 0),
    "dim":    (46, 26, 4),
},
"finance": {
    "name":   "MARKETS",
    "bg":     (4, 12, 4),
    "accent": (0, 200, 83),
    "dim":    (10, 38, 16),
},
"news": {
    "name":   "WORLD NEWS",
    "bg":     (6, 6, 14),
    "accent": (129, 140, 248),
    "dim":    (22, 22, 52),
},
"games": {
    "name":   "GAMING",
    "bg":     (8, 4, 20),
    "accent": (168, 85, 247),
    "dim":    (28, 14, 58),
},
"music": {
    "name":   "MUSIC CHARTS",
    "bg":     (14, 4, 18),
    "accent": (224, 64, 251),
    "dim":    (40, 14, 52),
},
"techai": {
    "name":   "AI & TECH",
    "bg":     (4, 8, 20),
    "accent": (96, 165, 250),
    "dim":    (14, 26, 58),
},
```

Also add wide_row support to generate_content_strip():
```python
# In _draw_match_row equivalent, detect wide mode:
def _is_wide_row(match: dict) -> bool:
    return not match.get("score") and not match.get("away")

# Wide row: home spans full width, away is line2 below
```

### 5. Update config.json

Add 7 new schedule entries after existing ones:
```json
{
  "id": "fixtures",
  "label": "Upcoming Fixtures",
  "emoji": "📅",
  "cron_hour_utc": 7,
  "cron_minute_utc": 0,
  "cron_day_of_week": "mon",
  "enabled": false,
  "source": "fixtures",
  "sports": ["futbol"],
  "leagues_filter": ["Premier League", "LaLiga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League, Knockout stage", "Trendyol Süper Lig"],
  "youtube_title": "📅 Upcoming Fixtures | {date} | {channel}",
  "youtube_description": "This week's biggest matches.\n#{channel}",
  "youtube_tags": ["fixtures", "upcoming matches", "football schedule"]
},
{
  "id": "finance",
  "label": "Finance Daily",
  "emoji": "📈",
  "cron_hour_utc": 22,
  "cron_minute_utc": 30,
  "enabled": false,
  "source": "finance",
  "sports": ["finance"],
  "sport_labels": {"finance": "Markets"},
  "youtube_title": "📈 Market Close | {date} | {channel}",
  "youtube_description": "Daily stock & crypto summary.\nNot financial advice.\n#{channel}",
  "youtube_tags": ["stocks", "crypto", "markets", "finance"]
},
{
  "id": "music_europe",
  "label": "Music Europe",
  "emoji": "🎵",
  "cron_hour_utc": 8,
  "cron_minute_utc": 0,
  "cron_day_of_week": "fri",
  "enabled": false,
  "source": "music",
  "continent": "EUROPE",
  "sports": ["music"],
  "youtube_title": "🎵 Europe Top 10 | Week {week} | {channel}",
  "youtube_description": "Weekly European music charts.\n#{channel}",
  "youtube_tags": ["music charts", "top 10", "europe"]
},
{
  "id": "techai",
  "label": "AI & Tech Weekly",
  "emoji": "🤖",
  "cron_hour_utc": 8,
  "cron_minute_utc": 0,
  "cron_day_of_week": "mon",
  "enabled": false,
  "source": "techai",
  "sports": ["techai"],
  "youtube_title": "🤖 AI Weekly | Week {week} | {channel}",
  "youtube_description": "This week in AI & tech.\n#{channel}",
  "youtube_tags": ["AI news", "tech news", "ChatGPT", "Claude AI"]
}
```

### 6. Test everything

```bash
# Test fixtures fetcher
python -c "
from channels.fixtures.fixtures_fetcher import FixturesFetcher
f = FixturesFetcher()
items = f.fetch('2026-04-07', '2026-04-13')
groups = f.to_reel_groups(items)
print(f'{len(items)} fixtures, {len(groups)} date groups')
for g in groups[:2]:
    print(f'  {g[\"league\"]}: {len(g[\"matches\"])} matches')
"

# Test video_maker new themes  
python -c "
from video_maker import make_reel
make_reel(
    config={
        'channel_name': 'TestChannel',
        'date': '07.04.2026',
        'continents': [{
            'name': 'UPCOMING',
            'groups': [{
                'league': 'MON · 07 Apr',
                'display_name': 'Monday April 7',
                'matches': [
                    {'id':'t1','home':'Real Madrid','score':'vs','away':'Bayern Munich','status':'21:00','time':'UCL'},
                    {'id':'t2','home':'Arsenal','score':'vs','away':'Man City','status':'19:45','time':'EPL'},
                ]
            }]
        }]
    },
    output_path='test_fixtures.mp4',
    sport_id='fixtures'
)
print('fixtures reel generated OK')
"
```

## DELIVERABLES

Report when complete:
1. ✅ Folder structure created
2. ✅ base_fetcher.py — abstract base
3. ✅ fixtures_fetcher.py — tested with live API
4. ✅ video_maker.py — 7 new themes added
5. ✅ Wide row mode — implemented
6. ✅ config.json — 7 new schedules added
7. ⏳ Next: finance_fetcher.py (Tab 2)
8. ⏳ Next: music_fetcher.py (Tab 3)
9. ⏳ Next: techai_fetcher.py (Tab 4)

If you hit any error, show the full traceback and your proposed fix.
Do not guess — if uncertain about an API response format, 
print the raw response first.
```

---

## TAB 2 — @ayaz_finance

```
Continue Ayaz Media Network. Phase 1 done (scaffold + fixtures).
Now: implement finance_fetcher.py

Read: docs/channels/ALL_CHANNELS.md → FINANCE section

Install: pip install yfinance python-dotenv

File: channels/finance/finance_fetcher.py

Implement FinanceFetcher(BaseFetcher):
- channel_id = "finance"
- sport_id = "finance"

fetch() method:
1. yfinance: fetch top 5 stocks per market (see MARKETS dict in channel doc)
2. CoinGecko: fetch top 5 crypto prices
   GET https://api.coingecko.com/api/v3/simple/price
   ?ids=bitcoin,ethereum,binancecoin,solana,ripple
   &vs_currencies=usd&include_24hr_change=true
3. Combine into standard row format
4. Cache by date

to_reel_groups():
- Group by continent (EUROPE, AMERICAS, ASIA)
- Within each continent, group by market (DAX, SP500, etc.)
- CRYPTO gets its own group at the end

Column mapping:
  home   = short company name (ticker.info["shortName"][:20])
  score  = formatted price ("$189.40" or "€187.40")  
  away   = change percentage ("+1.24%" or "-0.89%")
  status = "▲" if positive else "▼"
  league = market name (DAX, SP500, etc.)

Special: when status == "▼", color the away column red in video_maker.
Add finance_disclaimer to footer: "NOT FINANCIAL ADVICE"

Test:
python -c "
from channels.finance.finance_fetcher import FinanceFetcher
f = FinanceFetcher()
items = f.fetch('2026-04-03', '2026-04-03')
print(f'{len(items)} stocks/crypto')
groups = f.to_reel_groups(items)
for g in groups:
    print(f'  {g[\"league\"]}: {len(g[\"matches\"])} items')
"
```

---

## TAB 3 — @ayaz_musics

```
Continue Ayaz Media Network. 
Now: implement music_fetcher.py

Read: docs/channels/ALL_CHANNELS.md → MUSIC section

File: channels/music/music_fetcher.py

Apple Music RSS URL pattern:
https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json

Country codes: gb, de, fr, es, tr, us, br, mx, jp, kr

Implement MusicFetcher(BaseFetcher):

fetch(continent: str) method:
1. Fetch each country for the continent
2. Apply weighted scoring (see channel doc)
3. Merge into Top 10 per continent
4. Save to cache (weekly, not daily)

Trend tracking:
- Load prev week from cache/music/prev_{continent}.json
- Compare ranks: ↑ ↓ ● NEW
- Save current as prev at end of run

to_reel_groups() for one continent:
Returns single group with 10 "match" rows:
[{
  "league": "EUROPE TOP 10",
  "display_name": "Europe Charts · Week 14",
  "matches": [
    {"id":"m1","home":"1 ↑","score":"Espresso","away":"Sabrina Carpenter","status":"3w","time":""}
  ]
}]

Test all 4 continents:
python -c "
from channels.music.music_fetcher import MusicFetcher
f = MusicFetcher()
for continent in ['EUROPE','AMERICAS','ASIA','TURKEY']:
    items = f.fetch(continent)
    print(f'{continent}: {len(items)} songs')
    if items:
        print(f'  #1: {items[0][\"score\"]} by {items[0][\"away\"]}')
"
```

---

## TAB 4 — @ayaz_techai

```
Continue Ayaz Media Network.
Now: implement techai_fetcher.py

Read: 
- docs/channels/ALL_CHANNELS.md → TECHAI section
- docs/prompts/AI_PROMPTS.md → TECHAI prompts

Requires: ANTHROPIC_API_KEY in .env

pip install anthropic feedparser python-dotenv

File: channels/techai/techai_fetcher.py

RSS_SOURCES = {
    "model_news": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://venturebeat.com/ai/feed/",
    ],
    "research": [
        "https://export.arxiv.org/rss/cs.AI",
    ]
}

Implement TechAIFetcher(BaseFetcher):

fetch() method:
1. Parse all RSS feeds with feedparser
2. Collect last 7 days of items (check entry.published)
3. Deduplicate by title similarity
4. Pass to Claude for categorization (use TECHAI_WEEKLY prompt)
5. Return categorized items as standard rows

to_reel_groups():
Group by category:
  MODEL_UPDATE → league = "MODEL UPDATES"
  BIG_TECH     → league = "BIG TECH"  
  TOOLS        → league = "TOOLS"
  FUNDING      → league = "FUNDING"
  RESEARCH     → league = "RESEARCH"
  REGULATION   → league = "REGULATION"

Wide row format (score="" away="" triggers wide mode):
  home  = "emoji + company" (e.g. "🤖 Anthropic")
  score = ""
  away  = line2 text (e.g. "Sonnet 4.6 · faster inference")
  status = "NEW" or "UPDATE" or "FUNDING"
  league = category name

Claude API call:
  model = "claude-haiku-4-5-20251001"
  max_tokens = 1500
  Use exact system+user prompts from AI_PROMPTS.md

Test:
python -c "
from channels.techai.techai_fetcher import TechAIFetcher
f = TechAIFetcher()
items = f.fetch('2026-03-27', '2026-04-03')
print(f'{len(items)} AI news items')
groups = f.to_reel_groups(items)
for g in groups:
    print(f'  {g[\"league\"]}: {len(g[\"matches\"])} items')
    if g[\"matches\"]:
        m = g[\"matches\"][0]
        print(f'    {m[\"home\"]} — {m[\"away\"]}')
"
```
