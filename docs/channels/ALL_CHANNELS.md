# FINANCE.md — @ayaz_finance
**Status:** 🔨 Building  
**File:** `channels/finance/finance_fetcher.py`  
**Theme:** `finance` in SPORT_IDENTITY

## Data Sources
| Source | Package | Key Required | Rate Limit |
|---|---|---|---|
| yfinance | `pip install yfinance` | No | Soft (1 req/2s) |
| CoinGecko | requests | No | 30 req/min |

## Markets
```python
MARKETS = {
    "EUROPE": {
        "DAX":     ["SAP.DE","SIE.DE","BAS.DE","ALV.DE","BMW.DE"],
        "BIST100": ["GARAN.IS","AKBNK.IS","EREGL.IS","KCHOL.IS","THYAO.IS"],
        "FTSE100": ["AZN.L","SHEL.L","ULVR.L","BP.L","RIO.L"],
        "CAC40":   ["MC.PA","TTE.PA","SAN.PA","BNP.PA","OR.PA"],
    },
    "AMERICAS": {
        "SP500":   ["AAPL","NVDA","MSFT","AMZN","GOOGL"],
        "NASDAQ":  ["META","TSLA","AVGO","ADBE","COST"],
        "BOVESPA": ["PETR4.SA","VALE3.SA","ITUB4.SA"],
    },
    "ASIA": {
        "NIKKEI":  ["7203.T","9984.T","6758.T","8306.T"],
        "KOSPI":   ["005930.KS","000660.KS","035420.KS"],
    }
}
CRYPTO = ["bitcoin","ethereum","binancecoin","solana","ripple"]
```

## Column Mapping
- `home` → Company short name (e.g. "Apple")
- `score` → Current price (e.g. "$189.40")
- `away` → % change (e.g. "+1.24%")
- `status` → "▲" (green) or "▼" (red)
- `time` → Volume (e.g. "2.3B")

## Special: Finance Footer
Add disclaimer to footer text:
> "NOT FINANCIAL ADVICE · Educational purposes only"

## Schedule
- Daily 22:30 UTC (after US market close)

---

# MUSIC.md — @ayaz_musics
**Status:** 🔨 Building  
**File:** `channels/music/music_fetcher.py`  
**Theme:** `music` in SPORT_IDENTITY

## Data Sources
| Source | URL Pattern | Key Required |
|---|---|---|
| Apple Music RSS | `rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json` | No |
| Spotify Charts | `api.spotify.com` (optional) | Yes (free) |

## Countries
```python
COUNTRIES = {
    "EUROPE":   {"gb":30, "de":20, "fr":20, "es":15, "tr":15},  # weights
    "AMERICAS": {"us":50, "br":30, "mx":20},
    "ASIA":     {"jp":50, "kr":50},
    "TURKEY":   {"tr":100},  # Turkey gets its own reel
}
```

## Trend Tracking
Save `cache/music/prev_{continent}_{week}.json` each week.
Compare this week vs last week for ↑ ↓ ● arrows.

## Column Mapping
- `home` → Rank + trend (e.g. "1 ↑")
- `score` → Song title (e.g. "Espresso")
- `away` → Artist (e.g. "Sabrina Carpenter")
- `status` → Weeks on chart (e.g. "3w")

## Schedule
- Every Friday: 4 reels at 08:00 / 09:00 / 10:00 / 11:00 UTC

---

# TECHAI.md — @ayaz_techai
**Status:** 🔨 Building  
**File:** `channels/techai/techai_fetcher.py`  
**Theme:** `techai` in SPORT_IDENTITY  
**Requires:** `ANTHROPIC_API_KEY`

## Data Sources
```python
RSS_SOURCES = {
    "model_news": [
        "https://www.anthropic.com/rss.xml",
        "https://openai.com/blog/rss",
        "https://blog.google/technology/ai/rss",
        "https://ai.meta.com/blog/rss",
    ],
    "tech_news": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://venturebeat.com/ai/feed/",
    ],
    "research": [
        "https://export.arxiv.org/rss/cs.AI",
        "https://export.arxiv.org/rss/cs.LG",
    ]
}
```

## AI Summarization
Uses `claude-haiku-4-5-20251001` (cheapest) for:
1. Categorizing news items
2. Summarizing to 50-char lines
3. Selecting top 8 from 50+ items

See `docs/prompts/TECHAI_PROMPTS.md` for full prompt library.

## Column Mapping (Wide Row Mode)
- `home` → "emoji + company" (e.g. "🤖 Anthropic")
- `score` → "" (empty — wide row mode)
- `away` → "line2 detail text"
- `status` → "NEW" / "UPDATE" / "FUNDING"

## Group Names (Categories)
MODEL UPDATES · BIG TECH · TOOLS · FUNDING · RESEARCH · REGULATION

## Schedule
- Monday, Wednesday, Friday 08:00 UTC

---

# TRANSFER.md — @ayaz_transfer
**Status:** ⏳ Planned  
**File:** `channels/transfer/transfer_fetcher.py`  
**Theme:** `transfer` in SPORT_IDENTITY  
**Requires:** `ANTHROPIC_API_KEY`

## Data Sources
| Source | Type | Key |
|---|---|---|
| TransferMarkt (RapidAPI) | Confirmed transfers | RAPIDAPI_KEY |
| Sky Sports RSS | Rumours | No |
| BBC Sport RSS | Rumours | No |
| Goal.com RSS | Rumours | No |

## Two-Section Reel
```
[DONE DEALS ✓]  — confirmed transfers only
  Player Name
  Club A → Club B
  €XXXm · X years

[HOT RUMOURS 🔥]  — with reliability stars
  Player Name
  Rumour text
  ⭐⭐⭐⭐⭐ Source Name
```

## Column Mapping
- `home` → Player name (full row span in wide mode)
- `score` → Transfer fee (e.g. "€180M")
- `away` → "Club A → Club B"
- `status` → "✓ DONE" or "🔥 RUMOUR"

## Reliability Rating
Stars (1–5) based on source:
- ⭐⭐⭐⭐⭐ Fabrizio Romano "Here we go"
- ⭐⭐⭐⭐ Sky Sports/BBC confirmed
- ⭐⭐⭐ Major outlet reporting
- ⭐⭐ Single source
- ⭐ Speculation

---

# NEWS.md — @ayaz_news
**Status:** ⏳ Planned  
**File:** `channels/news/news_fetcher.py`  
**Theme:** `news` in SPORT_IDENTITY  
**Requires:** `ANTHROPIC_API_KEY`, `NEWS_API_KEY`

## Data Sources
```python
RSS_SOURCES = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]
# + NewsAPI.org for additional coverage
```

## AI Processing
Claude categorizes and summarizes 50+ daily news items to top 8.
See `docs/prompts/NEWS_PROMPTS.md`.

## Categories
POLITICS · TECHNOLOGY · ECONOMY · SCIENCE · HEALTH · CLIMATE · CONFLICT

## Column Mapping (Wide Row Mode)
- `home` → "emoji + 2-word category label"
- `score` → "" (empty)
- `away` → "2-line news summary"
- `status` → "BREAKING" / "LATEST" / "TODAY"

---

# GAMES.md — @ayaz_gamezs
**Status:** ⏳ Planned  
**File:** `channels/games/games_fetcher.py`  
**Theme:** `games` in SPORT_IDENTITY

## Sub-formats (4 reel types)

### 1. Steam Charts (Thursday)
- Source: `store.steampowered.com/api` (no key)
- Content: Top 10 games by concurrent players
- home: rank + game name, score: player count, away: bar indicator

### 2. Esports Results (Daily)
- Source: PandaScore API (`PANDASCORE_KEY`)
- Content: CS2, LoL, Valorant results
- Same format as @ayaz_sports (home/score/away = team/score/team)

### 3. New Releases (Tuesday)
- Source: IGDB API (Twitch credentials)
- Content: Games released this week + Metacritic score
- home: game name, score: Metacritic, away: platform

### 4. Game Deals (Daily)
- Source: CheapShark API (no key) `cheapshark.com/api/1.0/deals`
- Content: Top 5 Steam discounts
- home: game name, score: sale price, away: % discount
