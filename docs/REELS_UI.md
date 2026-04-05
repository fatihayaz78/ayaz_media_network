# Reels UI Design Spec

## Channel Page (/channel)

### Layout
- Left sidebar (185px): channel list with row counts + pencil edit link
- Main area: header + continent tabs + date presets + data table + action bar

### Continent Tabs (finance/music/news/sports/fixtures)
```
[ All ] [ AMERICAS (N) ] [ EUROPE (N) ] [ ASIA (N) ] [ AFRICA (N) ]
```
- Click → client-side JS filter (no re-fetch)
- Right of tabs: pencil link to /channel-editor/{ch}/{continent}
- Global channels (techai/transfer/games): single "All" tab

### Date Presets
```
[ Today ] [ This Week ] [ This Month ] [ Custom ]
```
- Clicking preset updates datePreset state
- Must click "Fetch Data" to re-fetch with new dates
- Finance: Today=2d period, Week=5d, Month=1mo (yfinance)

### Data Table
- Rows grouped by continent → league
- Alternating row backgrounds (light/dark)
- Row toggle: checkbox to hide/show from reel
- League chip filters when >3 leagues

## Edit Reel Page (/channel-editor/{ch}/{continent})

### Layout
Two columns: 45% config | 55% data preview

### Left — Config Sections
- HEADER: title input, date format
- FOOTER: channel handle input
- STYLE: bg color + accent color pickers, speed select, frequency
- YOUTUBE: title template, description, tags, category, privacy, auto upload

### Right — Data Preview
- 4 continent tabs with row counts
- Today/Week/Month fetch buttons
- Scrollable row list

### Buttons
- Save Config → POST /api/reel-config/{ch}/{continent}
- Make Reel → POST /api/make-reel/{ch}/{continent}
- Make All 4 → POST /api/make-reel/{ch}/ALL

## Reel Video (1080x1920)

### Header (340px)
- Title: header_text, bold 82px, white, centered
- Accent bar: 74px wide, 4px height
- Date: "DD.MM.YYYY . Week NN", 48px

### Content Strip (scrolling at 60px/s default)
- Rows: 68px height, alternating bg
- Standard layout: [home left] [score center box] [away right]
- Wide row (score=""): [label small] [title bold] [subtitle dim]
- Section dividers: accent bar + pill label (STOCKS/FOREX/METALS/CRYPTO)
- % change colors: green (+) / red (-) / gray (neutral)

### Footer (220px)
- "SUBSCRIBE FOR MORE" — (210,210,225) visible
- @channel handle — accent+50 brightness
- "YOUTUBE" label — dim color
- Finance disclaimer if enabled

## Continent Themes
```
AMERICAS: bg=(10,5,5)   accent=(220,38,38)   red
EUROPE:   bg=(5,8,20)   accent=(59,130,246)  blue
ASIA:     bg=(12,10,3)  accent=(234,179,8)   gold
AFRICA:   bg=(3,10,5)   accent=(34,197,94)   green
```

## Scroll Speed
1.0x = 40 px/s | 1.5x = 60 px/s (default) | 2.0x = 80 px/s

## Thumbnail (1280x720)
- Top band: accent gradient + emoji/logo + date
- Center: header_title 86px + top 3 items 36px accent
- Bottom band: "AYAZ MEDIA NETWORK" + @handle
