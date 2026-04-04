# modules/FINANCE.md — @ayaz_finance
> Updated: Sprint 9 (April 2026)

## Status: ✅ Built (Redesigned)
Fetcher: channels/finance/finance_fetcher.py | Theme: finance (green)
APIs: yfinance batch download (no key) + CoinGecko (no key)
Schedule: Weekly Friday 18:00 UTC (after EU market close)
Tests: tests/test_app_routes.py — finance route passing ✅

## Markets (9 exchanges, 20 tickers each)

### EUROPE
- **DAX** 🇩🇪 Germany: SAP.DE, SIE.DE, ALV.DE, MRK.DE, DTE.DE, MBG.DE, BMW.DE, BAS.DE, BAYN.DE, ADS.DE, RWE.DE, VOW3.DE, IFX.DE, ENR.DE, HEN3.DE, SHL.DE, DPW.DE, BEI.DE, ZAL.DE, CON.DE
- **FTSE100** 🇬🇧 UK: AZN.L, SHEL.L, HSBA.L, ULVR.L, BP.L, RIO.L, GSK.L, REL.L, DGE.L, VOD.L, BATS.L, LLOY.L, BARC.L, NWG.L, PRU.L, BHP.L, GLEN.L, AAL.L, IMB.L, MKS.L
- **CAC40** 🇫🇷 France: MC.PA, TTE.PA, SAN.PA, BNP.PA, OR.PA, AIR.PA, RI.PA, CS.PA, SU.PA, SGO.PA, ACA.PA, GLE.PA, BN.PA, KER.PA, CAP.PA, PUB.PA, STM.PA, VIE.PA, LR.PA, RNO.PA
- **BIST100** 🇹🇷 Turkey: GARAN.IS, AKBNK.IS, EREGL.IS, KCHOL.IS, THYAO.IS, ASELS.IS, BIMAS.IS, FROTO.IS, SAHOL.IS, SISE.IS, ARCLK.IS, ENKAI.IS, ISCTR.IS, TUPRS.IS, VAKBN.IS, YKBNK.IS, PETKM.IS, TCELL.IS, KOZAL.IS, DOHOL.IS

### AMERICAS
- **SP500** 🇺🇸 USA: AAPL, NVDA, MSFT, AMZN, GOOGL, META, TSLA, BRK-B, AVGO, JPM, LLY, UNH, V, XOM, MA, HD, COST, PG, ABBV, JNJ
- **NASDAQ** 🇺🇸 USA: ADBE, NFLX, CSCO, AMD, INTC, QCOM, TXN, INTU, AMAT, MU, PANW, LRCX, KLAC, SNPS, CDNS, MRVL, ASML, ON, MPWR, ENPH
- **BOVESPA** 🇧🇷 Brazil: PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA, BBAS3.SA, ABEV3.SA, WEGE3.SA, RENT3.SA, MGLU3.SA, SUZB3.SA, JBSS3.SA, LREN3.SA, RADL3.SA, NTCO3.SA, BRFS3.SA, HAPV3.SA, RAIL3.SA, CSAN3.SA, GGBR4.SA, KLBN11.SA

### ASIA
- **NIKKEI** 🇯🇵 Japan: 7203.T, 9984.T, 6758.T, 8306.T, 9432.T, 6861.T, 7974.T, 9433.T, 4063.T, 8035.T, 6501.T, 7267.T, 4519.T, 9983.T, 6902.T, 8604.T, 6367.T, 4568.T, 2914.T, 9022.T
- **KOSPI** 🇰🇷 South Korea: 005930.KS, 000660.KS, 035420.KS, 005490.KS, 051910.KS, 035720.KS, 006400.KS, 028260.KS, 207940.KS, 003550.KS, 105560.KS, 055550.KS, 012330.KS, 066570.KS, 034730.KS, 009150.KS, 032830.KS, 018260.KS, 003490.KS, 010130.KS

### COMMODITIES 🌍 Global
- Gold (GC=F) — XAU $/oz
- Silver (SI=F) — XAG $/oz

### CRYPTO 💰
- Bitcoin, Ethereum, BNB, Solana, XRP (CoinGecko)

## Fetch Method
- **Batch download**: yfinance.download() — all 20 tickers per market in ONE API call
- Per market: top 3 gainers + top 2 losers shown (5 per market)
- Total rows: ~45 stocks + 2 commodities + 5 crypto = ~52 rows

## Column Mapping
home=ticker_name(18char), score=price($189.40), away=pct_change(+1.24%), status=▲/▼, time=ticker_symbol, league=market_name, category=flag+country, continent=EUROPE/AMERICAS/ASIA/COMMODITIES/CRYPTO

## Currency by Suffix
.DE→€ | .IS→₺ | .L→£ | .PA→€ | .SA→R$ | .T→¥ | .KS→₩ | default→$

## Footer
"NOT FINANCIAL ADVICE · Educational purposes only" (required)

## Known Issues
- CoinGecko SSL error on some networks (proxy/firewall) — works in production
