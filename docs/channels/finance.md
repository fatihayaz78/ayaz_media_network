# Finance Channel
YouTube: @ayaz_finance | Theme: finance | Continent split: YES (4 reels)

## Data Sources
| Type | Source | Count | Period Param |
|------|--------|-------|-------------|
| Stocks | yfinance batch | 16 exchanges, 209 tickers | 2d/5d/1mo |
| Forex | yfinance batch | 17 currency pairs | 2d/5d/1mo |
| Metals | yfinance batch | 6 commodities | 2d/5d/1mo |
| Crypto | CoinGecko / static | 5 coins | N/A |

## Exchanges by Continent
- EUROPE: DAX(DE), FTSE100(UK), CAC40(FR), BIST100(TR)
- AMERICAS: SP500(US), NASDAQ(US), BOVESPA(BR)
- ASIA: NIKKEI(JP), KOSPI(KR), SSE(CN), BSE(IN), HSI(HK), TWSE(TW), Tadawul(SA)
- AFRICA: JSE(ZA), EGX30(EG)

## % Change Calculation
- Today (delta<=1): yf period="2d", first open vs last close
- Week (delta<=7): yf period="5d", Mon open vs Fri close
- Month (delta>7): yf period="1mo", month-start open vs today close

## Output
output/finance/{CONTINENT}_{date}.mp4 + output/thumbnails/finance_{date}.jpg

## Status
- Fetch: WORKING (91 rows typical)
- Split: WORKING (AMERICAS 29, EUROPE 37, ASIA 40, AFRICA 18)
- Reel: WORKING
- Section dividers: NOT YET
- Green/red colors: NOT YET
