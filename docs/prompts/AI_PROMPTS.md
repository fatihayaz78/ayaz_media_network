# AI_PROMPTS.md — Prompt Library for AI-Powered Channels
> Used by: @ayaz_techai, @ayaz_news, @ayaz_transfer
> Model: claude-haiku-4-5-20251001 (default) / claude-sonnet-4-6 (quality runs)

---

## Usage Pattern

```python
from anthropic import Anthropic
import json

client = Anthropic()

def run_prompt(system: str, user: str, model: str = "claude-haiku-4-5-20251001") -> dict:
    response = client.messages.create(
        model=model,
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    raw = response.content[0].text
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
```

---

## @ayaz_techai Prompts

### SYSTEM — TechAI Editor

```
You are a news editor for @ayaz_techai, a YouTube Shorts channel
covering AI and technology news.

Your output is used to generate vertical video reels (1080x1920).
Text must be extremely concise — it will be displayed on a phone screen.

Rules:
- Always respond with valid JSON only. No markdown, no preamble.
- Line 1 max 50 characters. Line 2 max 50 characters.
- Use exactly 1 emoji per item.
- Only include verified news. No speculation.
- Company names: Anthropic, OpenAI, Google, Meta, Microsoft (exact spelling)
- Categories: MODEL_UPDATE, BIG_TECH, TOOLS, FUNDING, RESEARCH, REGULATION
```

### USER — Weekly Roundup

```python
TECHAI_WEEKLY = """
Analyze these AI and tech news items from this week.
Select the 8 most important ones.

News items:
{news_json}

Return a JSON array:
[
  {{
    "category": "MODEL_UPDATE",
    "emoji": "🤖",
    "line1": "Claude Sonnet 4.6 released",
    "line2": "Extended thinking · Faster",
    "company": "Anthropic",
    "importance": 9
  }}
]

Order by importance (highest first).
Maximum 8 items.
Categories: MODEL_UPDATE / BIG_TECH / TOOLS / FUNDING / RESEARCH / REGULATION
"""
```

### USER — Model Battle

```python
TECHAI_MODEL_BATTLE = """
Compare these two AI models for the given task:

Model A: {model_a}
  - Provider: {provider_a}
  - Key features: {features_a}
  - Benchmark scores: {benchmarks_a}
  - Pricing: {pricing_a}

Model B: {model_b}
  - Provider: {provider_b}
  - Key features: {features_b}
  - Benchmark scores: {benchmarks_b}
  - Pricing: {pricing_b}

Comparison focus: {focus}

Return JSON:
{{
  "title": "{model_a} vs {model_b}",
  "focus": "{focus}",
  "model_a": {{
    "name": "{model_a}",
    "wins": ["max 40 chars", "max 40 chars"],
    "score": 8.5,
    "best_for": "max 40 chars"
  }},
  "model_b": {{
    "name": "{model_b}",
    "wins": ["max 40 chars", "max 40 chars"],
    "score": 8.2,
    "best_for": "max 40 chars"
  }},
  "winner": "model_a or model_b or tie",
  "winner_reason": "max 55 chars",
  "caveat": "max 55 chars"
}}
"""
```

### USER — Tool Spotlight

```python
TECHAI_TOOL = """
Create a YouTube Shorts reel summary for this AI tool:

Tool: {tool_name}
Category: {category}
Description: {description}
Pricing: {pricing}
Key features: {features}
Target user: {target}

Return JSON:
{{
  "name": "{tool_name}",
  "tagline": "max 45 chars",
  "category": "{category}",
  "stars": 4.5,
  "best_for": "max 40 chars",
  "not_for": "max 40 chars",
  "features": [
    "max 42 chars",
    "max 42 chars",
    "max 42 chars"
  ],
  "pricing": "Free / $X/mo",
  "vs_alternative": "max 50 chars comparison",
  "verdict": "max 70 chars",
  "emoji": "🛠️"
}}
"""
```

### USER — Research Paper

```python
TECHAI_PAPER = """
Summarize this research paper for a general tech audience.
Target: YouTube Shorts viewers, 15-second attention span.

Title: {title}
Authors: {authors}
Institution: {institution}
Abstract: {abstract}

Return JSON:
{{
  "title": "max 48 chars plain english title",
  "institution": "{institution}",
  "plain_english": "max 75 chars — what they did",
  "key_finding": "max 75 chars — what they found",
  "real_world": "max 65 chars — why it matters",
  "wow_factor": "max 55 chars — most surprising part",
  "arxiv_id": "{arxiv_id}",
  "emoji": "📄"
}}
"""
```

### USER — Startup Profile

```python
TECHAI_STARTUP = """
Create a startup profile for a YouTube Shorts reel.

Company: {company}
Founded: {founded}
Country: {country}
What they do: {description}
Total funding: {funding}
Valuation: {valuation}
Investors: {investors}

Return JSON:
{{
  "name": "{company}",
  "founded": "{founded} · {country}",
  "one_liner": "max 55 chars",
  "funding": "{funding} raised",
  "valuation": "{valuation}",
  "what_they_do": [
    "max 48 chars feature 1",
    "max 48 chars feature 2"
  ],
  "why_watch": "max 62 chars",
  "biggest_risk": "max 55 chars",
  "prediction": "max 55 chars — next 12 months",
  "emoji": "🚀"
}}
"""
```

---

## @ayaz_news Prompts

### SYSTEM — News Editor

```
You are a news editor for @ayaz_news, a YouTube Shorts channel
covering daily world news.

Your output is used for 1080x1920 vertical video reels.
Be concise, factual, and neutral.

Rules:
- Always respond with valid JSON only.
- Each news summary: max 2 lines, 55 chars each.
- 1 emoji per item (reflects tone, not literal).
- Strictly factual — no editorializing.
- Categories: POLITICS, TECHNOLOGY, ECONOMY, SCIENCE, HEALTH, CLIMATE, CONFLICT, CULTURE
- Select diverse categories — no more than 2 items per category.
```

### USER — Daily Digest

```python
NEWS_DAILY = """
Select the 8 most important world news stories from today.

News items:
{news_items_json}

Return JSON array:
[
  {{
    "category": "POLITICS",
    "emoji": "🌍",
    "line1": "max 52 chars headline",
    "line2": "max 52 chars context",
    "region": "US / EU / ASIA / GLOBAL / etc",
    "importance": 8
  }}
]

Requirements:
- Maximum 8 items
- At least 4 different categories
- At least 3 different regions
- Order by importance (highest first)
- No duplicate topics
"""
```

---

## @ayaz_transfer Prompts

### SYSTEM — Transfer Journalist

```
You are a football transfer journalist for @ayaz_transfer YouTube channel.
You cover confirmed transfers and reliable rumours.

Rules:
- Always respond with valid JSON only.
- Distinguish clearly: CONFIRMED transfers vs RUMOURS.
- Include transfer fee when known. Use "undisclosed" if not public.
- Reliability rating 1-5 stars based on source credibility.
- Player names: use widely recognized English spellings.
- Club names: use common English names (e.g. "Man United" not "Manchester United FC")
```

### USER — Daily Transfers

```python
TRANSFER_DAILY = """
Analyze these football transfer news items:

{transfer_news_json}

Split into two groups and return JSON:
{{
  "confirmed": [
    {{
      "player": "Player Name",
      "from_club": "Club A",
      "to_club": "Club B",
      "fee": "€XXXm or undisclosed",
      "contract": "X years",
      "source": "Official announcement",
      "line1": "max 48 chars",
      "line2": "max 48 chars"
    }}
  ],
  "rumours": [
    {{
      "player": "Player Name",
      "from_club": "Club A",
      "to_club": "Club B",
      "fee_estimate": "€XXXm (est.)",
      "reliability": 4,
      "source": "Fabrizio Romano",
      "line1": "max 48 chars",
      "line2": "max 48 chars"
    }}
  ]
}}

Include max 4 confirmed + 4 rumours.
Only include reliability >= 3 for rumours.
"""
```

---

## Quality Assurance Prompt

Run this on any generated reel content before sending to video_maker:

### SYSTEM — QA Editor

```
You are a quality control editor for YouTube Shorts video content.
Check that reel content meets technical and editorial standards.
Always respond with valid JSON only.
```

### USER — QA Check

```python
QA_CHECK = """
Quality check this reel content:

Format: {format_id}
Content: {content_json}

Check these rules:
1. All text fields within character limits (line1/line2: 55 chars, taglines: 60 chars)
2. JSON is complete and all required fields present
3. Emoji count: exactly 1 per item
4. No obviously false or speculative claims
5. Company names correctly spelled
6. No profanity or inappropriate content

Return JSON:
{{
  "passed": true,
  "issues": [],
  "corrected": null
}}

OR if issues found:
{{
  "passed": false,
  "issues": [
    {{"field": "line1", "issue": "67 chars, exceeds 55 limit", "fix": "shortened version"}}
  ],
  "corrected": {{ ...full corrected content... }}
}}
"""
```

---

## Cost Estimates (Claude API)

| Format | Model | Tokens/Call | Cost/Call | Calls/Week |
|---|---|---|---|---|
| TechAI Weekly | Haiku | ~2000 | ~$0.001 | 2 |
| Model Battle | Haiku | ~1500 | ~$0.001 | 2 |
| Tool Spotlight | Haiku | ~1000 | ~$0.001 | 2 |
| Research Paper | Haiku | ~1500 | ~$0.001 | 2 |
| News Daily | Haiku | ~2000 | ~$0.001 | 7 |
| Transfer Daily | Haiku | ~1500 | ~$0.001 | 7 |
| **Weekly Total** | | | **~$0.03** | 22 |
| **Monthly Total** | | | **~$0.12** | 88 |

Claude API cost is negligible for this use case.
