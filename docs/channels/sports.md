# Sports Channels
7 sport types: futbol, basket, tenis, motor, dovus, amerikan, voley
YouTube: @ayaz_sports | Continent split: YES (continent field on rows)

## Data Source
SportAPI7 (RapidAPI) — QUOTA LIMITED (50 req/month BASIC plan)
Fallback: MOCK_DATA=1 env var → 23 realistic mock rows across 7 sports

## Mock Data (fetcher.py)
- futbol: 7 rows (PL, LaLiga, Bundesliga, Ligue 1, Serie A, Super Lig, Brasileirao)
- basket: 4 rows (NBA, EuroLeague)
- tenis: 3 rows (ATP, WTA)
- motor: 3 rows (F1, MotoGP)
- dovus: 2 rows (UFC)
- amerikan: 2 rows (NFL)
- voley: 2 rows (VNL)

## Status
- Real API: QUOTA BLOCKED (use mock)
- Mock: WORKING (MOCK_DATA=1)
- Reel: WORKING with mock data
