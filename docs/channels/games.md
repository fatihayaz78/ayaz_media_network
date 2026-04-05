# Games Channel
YouTube: @ayaz_gamezs | Theme: games | Continent split: NO (global)

## Data Sources
- Steam Charts: store.steampowered.com/api/featuredcategories/ → top 10
- CheapShark: cheapshark.com/api/1.0/deals → top 5 deals
- Esports: PandaScore API (needs PANDASCORE_KEY)
- Combined: fetch_combined() returns Steam + Deals (+ esports if key)

## Row Format
Steam: home="#1 Game Name" | score="150K" | away="players" | status="PEAK"
Deals: home="Game Name" | score="$11.99" | away="-80%" | status="SALE"

## Status
- Steam: WORKING (10 rows, relaxed filter)
- Deals: WORKING (3-5 rows)
- Esports: NOT WORKING (no PANDASCORE_KEY)
- Combined: WORKING (13 rows typical)
