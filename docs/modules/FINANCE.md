# modules/FINANCE.md — @ayaz_finance
> Updated: Sprint 2 (April 2026)

## Status: ✅ Built
Fetcher: channels/finance/finance_fetcher.py | Theme: finance (green)
APIs: yfinance (no key) + CoinGecko (no key)
Schedule: Daily 22:30 UTC (after US market close)
Tests: tests/channels/test_finance.py — 5 passed, 1 skipped ✅

## Markets
EUROPE:   DAX(SAP.DE,SIE.DE,BAS.DE,ALV.DE,BMW.DE), BIST100(GARAN.IS,AKBNK.IS,EREGL.IS,KCHOL.IS,THYAO.IS), FTSE100(AZN.L,SHEL.L,ULVR.L,BP.L,RIO.L)
AMERICAS: SP500(AAPL,NVDA,MSFT,AMZN,GOOGL), NASDAQ(META,TSLA,AVGO,ADBE,COST), BOVESPA(PETR4.SA,VALE3.SA,ITUB4.SA)
ASIA:     NIKKEI(7203.T,9984.T,6758.T,8306.T,9432.T), KOSPI(005930.KS,000660.KS,035420.KS)
CRYPTO:   bitcoin,ethereum,binancecoin,solana,ripple (CoinGecko)

## Column Mapping
home=company_name(18char), score=price($189.40), away=pct_change(+1.24%), status=▲/▼, time=ticker_symbol, league=market_name

## Currency by Suffix
.DE→€ | .IS→₺ | .L→£ | .PA→€ | .SA→R$ | .T→¥ | .KS→₩ | default→$

## Footer
"NOT FINANCIAL ADVICE · Educational purposes only" (required)

## Known Issues
- CoinGecko SSL error on some networks (proxy/firewall) — works in production
- yfinance fetch takes ~3.5min for all 36 tickers (0.3s delay between calls)
- CAC40 (France) not included — add: MC.PA,TTE.PA,SAN.PA,BNP.PA,OR.PA
