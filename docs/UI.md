# UI.md — Ayaz Media Network Visual Specification

## Reel Format (Approved Design)

All channels use the **exact same 1080×1920 layout**.
Only colors, content, and channel identity change.

```
Canvas: 1080 × 1920 px  (9:16 vertical)
FPS:    30
Codec:  H.264 (libx264)
Audio:  AAC 192kbps (optional)
```

---

## Layout Zones

### Zone 1 — HEADER (y: 0 to 340px, fixed)

```
┌──────────────────────────────────────────┐
│                                          │
│   [52px top padding]                     │
│                                          │
│   "WEEKLY SCORES"       ← 82px Bold      │
│   White (#FFFFFF)                        │
│                                          │
│   "CHANNEL TYPE"        ← 82px Bold      │
│   Accent color                           │
│                                          │
│   ────────────                           │
│   74px accent bar                        │
│                                          │
│   "01.04.2026  ·  Week 14"               │
│   36px Regular, dim color                │
│                                          │
│   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─               │
│   Bottom separator line (accent, α0.15)  │
└──────────────────────────────────────────┘
```

**Fonts:** Roboto Bold / Roboto Regular (auto-downloaded)  
**Fallback:** Helvetica → DejaVu Sans → Default

---

### Zone 2 — CONTENT STRIP (y: 340 to 1700px, scrolling)

Content scrolls from bottom to top. Items are rendered on a
single tall PNG that scrolls past the 1360px visible window.

#### Continent/Category Header Row

```
  ─────────────  EUROPE  ─────────────
                 34px Bold
                 Continent color, α0.78
```

#### League/Group Header Row (52px tall)

```
  ║  Premier League (England)         X matches
  3px accent bar   28px Bold           10px muted
```

#### Match/Content Row (68px tall, alternating backgrounds)

```
  ┌─────────────────────────────────────────────┐
  │  Manchester City  │   3 – 1   │  Arsenal    │
  │  LEFT COLUMN      │  CENTER   │ RIGHT COL   │
  │  32px Regular     │  38px Bold│  32px Reg   │
  │  195,195,210 α0.86│ league col│  same       │
  └─────────────────────────────────────────────┘

  Score box:
    Background: league_color α0.15
    Border:     league_color α0.39, 2px
    Border-radius: 6px
    Padding:    14px horizontal, 6px vertical
```

**Column widths (approximate):**
- Left (home):  box_x - MARGIN - 16px gap → right-aligned text
- Center (score): dynamic width based on text + 28px padding
- Right (away):  from score_box right + 16px gap → left-aligned text

---

### Zone 3 — FOOTER (y: 1700 to 1920px, fixed)

```
┌──────────────────────────────────────────┐
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─                │
│  Top separator line (accent, α0.12)      │
│                                          │
│  ▶  SUBSCRIBE FOR MORE                  │
│     @channel_name                        │
│     YOUTUBE                              │
│                                          │
│  ▶ = Filled triangle, accent color      │
│  @channel = 44px Bold, accent color     │
│  YOUTUBE  = 26px Bold, dim color        │
└──────────────────────────────────────────┘
```

---

## Color Themes (SPORT_IDENTITY)

Each channel has a unique dark color theme.

```python
SPORT_IDENTITY = {

    # ── Existing channels ──────────────────────────────────────

    "futbol": {
        "name":   "FOOTBALL",
        "bg":     (13, 15, 26),      # Deep navy
        "accent": (79, 150, 255),    # Blue
        "dim":    (30, 42, 74),
    },
    "basket": {
        "name":   "BASKETBALL",
        "bg":     (18, 8, 8),        # Deep crimson
        "accent": (224, 64, 48),     # Red-orange
        "dim":    (50, 20, 18),
    },
    "motor": {
        "name":   "MOTORSPORT",
        "bg":     (18, 9, 0),        # Deep amber
        "accent": (240, 120, 32),    # Orange
        "dim":    (48, 28, 10),
    },
    "amerikan": {
        "name":   "AMERICAN FOOTBALL",
        "bg":     (6, 12, 22),
        "accent": (56, 112, 224),
        "dim":    (18, 30, 58),
    },

    # ── New channels ───────────────────────────────────────────

    "fixtures": {
        "name":   "UPCOMING FIXTURES",
        "bg":     (6, 16, 8),        # Deep forest green
        "accent": (64, 200, 112),    # Green
        "dim":    (18, 44, 24),
    },
    "transfer": {
        "name":   "TRANSFERS",
        "bg":     (18, 8, 0),        # Deep amber-black
        "accent": (255, 140, 0),     # Orange
        "dim":    (46, 26, 4),
    },
    "finance": {
        "name":   "MARKETS",
        "bg":     (4, 12, 4),        # Deep green-black
        "accent": (0, 200, 83),      # Market green
        "dim":    (10, 38, 16),
        "accent_negative": (239, 68, 68),  # Red for losses
    },
    "news": {
        "name":   "WORLD NEWS",
        "bg":     (6, 6, 14),        # Near black indigo
        "accent": (129, 140, 248),   # Indigo
        "dim":    (22, 22, 52),
    },
    "games": {
        "name":   "GAMING",
        "bg":     (8, 4, 20),        # Deep purple-black
        "accent": (168, 85, 247),    # Purple
        "dim":    (28, 14, 58),
    },
    "music": {
        "name":   "MUSIC CHARTS",
        "bg":     (14, 4, 18),       # Deep violet-black
        "accent": (224, 64, 251),    # Violet-pink
        "dim":    (40, 14, 52),
    },
    "techai": {
        "name":   "AI & TECH",
        "bg":     (4, 8, 20),        # Deep blue-black
        "accent": (96, 165, 250),    # Sky blue
        "dim":    (14, 26, 58),
    },
}
```

---

## League/Group Colors

```python
LEAGUE_COLORS = {
    # Sports
    "Premier League":    (111, 45,  189),  # Purple
    "Trendyol Süper Lig":(232, 64,   64),  # Red
    "LaLiga":            (255, 107,  53),  # Orange
    "Serie A":           (0,   87,  168),  # Blue
    "Bundesliga":        (227,  6,   19),  # Red
    "Ligue 1":           (0,   63,  135),  # Navy
    "NBA":               (201,  8,   42),  # Crimson
    "NFL":               (1,   51,  105),  # Dark blue
    "Formula 1":         (232,  0,   45),  # F1 Red

    # Finance groups (auto-assigned by market)
    "DAX":               (0,   100, 200),  # German blue
    "BIST100":           (220,  40,  40),  # Turkish red
    "SP500":             (0,   120, 210),  # US blue
    "CRYPTO":            (247, 147,  26),  # Bitcoin orange

    # Music (continent colors)
    "EUROPE CHARTS":     (58,  122, 239),  # Blue
    "AMERICAS CHARTS":   (239,  80,  80),  # Red
    "ASIA CHARTS":       (168,  85, 247),  # Purple
    "TURKEY CHARTS":     (249, 115,  22),  # Orange

    # AI/Tech categories
    "MODEL UPDATES":     (96,  165, 250),  # Sky blue
    "BIG TECH":          (251, 191,  36),  # Amber
    "TOOLS":             (52,  211, 153),  # Teal
    "FUNDING":           (249, 115,  22),  # Orange
    "RESEARCH":          (167, 139, 250),  # Violet
    "REGULATION":        (248, 113, 113),  # Red
}
```

---

## Wide Row Mode (News & TechAI)

For channels where center/right columns are empty,
use full-width rows instead of the 3-column layout.

```
Normal row (3 columns):
  Manchester City │  3 – 1  │  Arsenal

Wide row (news/tech):
  🤖 Claude Sonnet 4.6 released              ← line1 (bold)
     Extended thinking · Faster inference    ← line2 (muted, 26px)
```

**Activation:** Set `row_mode = "wide"` in reel config or 
detect automatically when `score == "" and away == ""`.

Implementation in `video_maker.py`:
```python
def _draw_row(self, draw, img, row, y):
    if not row.get("score") and not row.get("away"):
        self._draw_wide_row(draw, img, row, y)
    else:
        self._draw_match_row(draw, img, row, y)
```

---

## Continent Colors (Section Dividers)

```python
CONTINENT_COLORS = {
    "EUROPE":       (79,  150, 255),  # Blue
    "AMERICAS":     (220,  64,  64),  # Red
    "ASIA-PACIFIC": (88,  192,  48),  # Green
    "MOTORSPORT":   (240, 120,  32),  # Orange
    "GLOBAL":       (200, 160, 255),  # Lavender
    "MARKETS":      (0,   200,  83),  # Market green
    "CHARTS":       (224,  64, 251),  # Violet
    "AI & TECH":    (96,  165, 250),  # Sky blue
    "GAMING":       (168,  85, 247),  # Purple
    "OTHER":        (150, 150, 180),  # Gray
}
```

---

## Scroll Behavior

```
pause_top  = 3.0 seconds   (content stationary at top)
scroll_spd = 40.0 px/sec   (smooth upward scroll)
scroll_dist = content_height pixels
duration   = pause_top + (scroll_dist / scroll_spd)
duration   = clamp(8.0, 180.0, duration)
```

For short content (< 8s): pad with blank space at bottom.  
For very long content (> 180s): increase scroll speed.

---

## Typography Scale

```
Header title (WEEKLY SCORES):  82px  Roboto Bold   White
Header channel (FOOTBALL):      82px  Roboto Bold   Accent
Header subtitle (date/week):    36px  Roboto Regular Dim
Continent label:                34px  Roboto Bold   Continent color
League label:                   28px  Roboto Bold   Muted (155,155,182)
Team/content (home/away):       32px  Roboto Regular Light (195,195,210)
Score:                          38px  Roboto Bold   League color (bright)
Footer subscribe text:          28px  Roboto Regular Dim
Footer channel name:            44px  Roboto Bold   Accent
Footer YOUTUBE:                 26px  Roboto Bold   Dim
Wide row line1:                 32px  Roboto Bold   Light
Wide row line2:                 26px  Roboto Regular Muted
```

---

## Background Options

| Type | Source | Effect |
|---|---|---|
| Solid color | `bg_rgb` from SPORT_IDENTITY | Default, always available |
| Static image | JPEG/PNG upload | Scaled to 1080×1920 |
| GIF | Animated GIF | Looped as background |
| Video | MP4 upload | `-stream_loop -1` ffmpeg flag |

All backgrounds have content layers composited on top.
Recommended: Dark backgrounds (< 40% brightness) for readability.

---

## Output Specifications

```
Resolution:   1080 × 1920  (9:16 vertical)
Frame rate:   30 fps
Video codec:  libx264
CRF:          22  (high quality)
Preset:       fast
Pixel format: yuv420p  (required for wide compatibility)
Audio codec:  AAC (if music present)
Audio bitrate:192 kbps
Sample rate:  44100 Hz
Container:    MP4 (H.264)

Typical file sizes:
  30s reel, no music:  8–15 MB
  60s reel, with music: 20–35 MB
  120s reel:           40–65 MB
```

---

## Background Media Guidelines

Recommended for best visual results:

```
Aspect ratio:  9:16  (portrait vertical)
Resolution:    1080 × 1920 minimum
File format:   MP4 (video bg), JPEG (static), GIF (animated)
Max file size: 50 MB
Duration:      Min 15s for video backgrounds (will be looped)
Brightness:    Keep below 40% — content must be readable
```

Per-channel recommended aesthetics:
- sports/fixtures → stadium crowd, grass, action footage
- finance        → city skyline at night, trading floor
- music          → concert lights, vinyl records, waveforms
- techai         → circuit boards, data streams, glowing code
- games          → game footage, controller, neon lights
- transfer       → empty stadium, transfer rumor newspaper
- news           → globe, newspaper, world map
