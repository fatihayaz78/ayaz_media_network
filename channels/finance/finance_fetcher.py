"""
@ayaz_finance — Stock & crypto market fetcher.
Uses yfinance for stocks (batch download), CoinGecko for crypto.
Redesigned Phase 9: country-level grouping, 20 tickers per market, commodities.
"""

import os
import sys
import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

try:
    import yfinance as yf
except ImportError:
    raise ImportError("Run: pip install yfinance")

MARKETS = {
    "EUROPE": {
        "DAX": {
            "country": "Germany", "flag": "\U0001f1e9\U0001f1ea",
            "tickers": ["SAP.DE","SIE.DE","ALV.DE","MRK.DE","DTE.DE",
                        "MBG.DE","BMW.DE","BAS.DE","BAYN.DE","ADS.DE",
                        "RWE.DE","VOW3.DE","IFX.DE","ENR.DE","HEN3.DE",
                        "SHL.DE","DHL.DE","BEI.DE","ZAL.DE","CON.DE"],
        },
        "FTSE100": {
            "country": "UK", "flag": "\U0001f1ec\U0001f1e7",
            "tickers": ["AZN.L","SHEL.L","HSBA.L","ULVR.L","BP.L",
                        "RIO.L","GSK.L","REL.L","DGE.L","VOD.L",
                        "BATS.L","LLOY.L","BARC.L","NWG.L","PRU.L",
                        "BHP.L","GLEN.L","AAL.L","IMB.L","MKS.L"],
        },
        "CAC40": {
            "country": "France", "flag": "\U0001f1eb\U0001f1f7",
            "tickers": ["MC.PA","TTE.PA","SAN.PA","BNP.PA","OR.PA",
                        "AIR.PA","RI.PA","CS.PA","SU.PA","SGO.PA",
                        "ACA.PA","GLE.PA","BN.PA","KER.PA","CAP.PA",
                        "PUB.PA","STM","VIE.PA","LR.PA","RNO.PA"],
        },
        "BIST100": {
            "country": "Turkey", "flag": "\U0001f1f9\U0001f1f7",
            "tickers": ["GARAN.IS","AKBNK.IS","EREGL.IS","KCHOL.IS","THYAO.IS",
                        "ASELS.IS","BIMAS.IS","FROTO.IS","SAHOL.IS","SISE.IS",
                        "ARCLK.IS","ENKAI.IS","ISCTR.IS","TUPRS.IS","VAKBN.IS",
                        "YKBNK.IS","PETKM.IS","TCELL.IS","TAVHL.IS","DOHOL.IS"],
        },
    },
    "AMERICAS": {
        "SP500": {
            "country": "USA", "flag": "\U0001f1fa\U0001f1f8",
            "tickers": ["AAPL","NVDA","MSFT","AMZN","GOOGL",
                        "META","TSLA","BRK-B","AVGO","JPM",
                        "LLY","UNH","V","XOM","MA",
                        "HD","COST","PG","ABBV","JNJ"],
        },
        "NASDAQ": {
            "country": "USA", "flag": "\U0001f1fa\U0001f1f8",
            "tickers": ["ADBE","NFLX","CSCO","AMD","INTC",
                        "QCOM","TXN","INTU","AMAT","MU",
                        "PANW","LRCX","KLAC","SNPS","CDNS",
                        "MRVL","ASML","ON","MPWR","ENPH"],
        },
        "BOVESPA": {
            "country": "Brazil", "flag": "\U0001f1e7\U0001f1f7",
            "tickers": ["PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","BBAS3.SA",
                        "ABEV3.SA","WEGE3.SA","RENT3.SA","MGLU3.SA","SUZB3.SA",
                        "UGPA3.SA","LREN3.SA","RADL3.SA","TOTS3.SA","VIVT3.SA",
                        "HAPV3.SA","RAIL3.SA","CSAN3.SA","GGBR4.SA","KLBN11.SA"],
        },
    },
    "ASIA": {
        "NIKKEI": {
            "country": "Japan", "flag": "\U0001f1ef\U0001f1f5",
            "tickers": ["7203.T","9984.T","6758.T","8306.T","9432.T",
                        "6861.T","7974.T","9433.T","4063.T","8035.T",
                        "6501.T","7267.T","4519.T","9983.T","6902.T",
                        "8604.T","6367.T","4568.T","2914.T","9022.T"],
        },
        "KOSPI": {
            "country": "South Korea", "flag": "\U0001f1f0\U0001f1f7",
            "tickers": ["005930.KS","000660.KS","035420.KS","005490.KS","051910.KS",
                        "035720.KS","006400.KS","028260.KS","207940.KS","003550.KS",
                        "105560.KS","055550.KS","012330.KS","066570.KS","034730.KS",
                        "009150.KS","032830.KS","018260.KS","003490.KS","010130.KS"],
        },
    },
}

CRYPTO_IDS = ["bitcoin", "ethereum", "binancecoin", "solana", "ripple"]
CRYPTO_SYMBOLS = {
    "bitcoin": "BTC", "ethereum": "ETH", "binancecoin": "BNB",
    "solana": "SOL", "ripple": "XRP",
}
CRYPTO_NAMES = {
    "bitcoin": "Bitcoin", "ethereum": "Ethereum",
    "binancecoin": "BNB", "solana": "Solana", "ripple": "XRP",
}

CURRENCY_MAP = {
    ".DE": "\u20ac", ".IS": "\u20ba", ".L": "\u00a3", ".PA": "\u20ac",
    ".SA": "R$", ".T": "\u00a5", ".KS": "\u20a9",
}

TICKER_NAMES = {
    # Japan NIKKEI
    "7203.T":  "Toyota",          "9984.T":  "SoftBank",
    "6758.T":  "Sony",            "8306.T":  "Mitsubishi UFJ",
    "9432.T":  "NTT",             "6861.T":  "Keyence",
    "7974.T":  "Nintendo",        "9433.T":  "KDDI",
    "4063.T":  "Shin-Etsu Chem",  "8035.T":  "Tokyo Electron",
    "6501.T":  "Hitachi",         "7267.T":  "Honda",
    "4519.T":  "Chugai Pharma",   "9983.T":  "Fast Retailing",
    "6902.T":  "Denso",           "8604.T":  "Nomura",
    "6367.T":  "Daikin",          "4568.T":  "Daiichi Sankyo",
    "2914.T":  "Japan Tobacco",   "9022.T":  "JR Central",
    # South Korea KOSPI
    "005930.KS": "Samsung Elec",  "000660.KS": "SK Hynix",
    "035420.KS": "Naver",         "005490.KS": "POSCO",
    "051910.KS": "LG Chem",       "035720.KS": "Kakao",
    "006400.KS": "Samsung SDI",   "028260.KS": "Samsung C&T",
    "207940.KS": "Samsung Bio",   "003550.KS": "LG Corp",
    "105560.KS": "KB Financial",  "055550.KS": "Shinhan Fin",
    "012330.KS": "Hyundai Mobis", "066570.KS": "LG Electronics",
    "034730.KS": "SK Inc",        "009150.KS": "Samsung EM",
    "032830.KS": "Samsung Life",  "018260.KS": "Samsung SDS",
    "003490.KS": "Korean Air",    "010130.KS": "Korea Zinc",
    # Turkey BIST100
    "GARAN.IS":  "Garanti BBVA",  "AKBNK.IS":  "Akbank",
    "EREGL.IS":  "Eregli Demir",  "KCHOL.IS":  "Koc Holding",
    "THYAO.IS":  "Turk Hava Yol", "ASELS.IS":  "Aselsan",
    "BIMAS.IS":  "BIM",           "FROTO.IS":  "Ford Otosan",
    "SAHOL.IS":  "Sabanci Hold",  "SISE.IS":   "Sise Cam",
    "ARCLK.IS":  "Arcelik",       "ENKAI.IS":  "Enka Insaat",
    "ISCTR.IS":  "Is Bankasi",    "TUPRS.IS":  "Tupras",
    "VAKBN.IS":  "Vakifbank",     "YKBNK.IS":  "Yapi Kredi",
    "PETKM.IS":  "Petkim",        "TCELL.IS":  "Turkcell",
    "TAVHL.IS":  "TAV Airports",  "DOHOL.IS":  "Dogan Hold",
    # Brazil BOVESPA
    "PETR4.SA":  "Petrobras",     "VALE3.SA":  "Vale",
    "ITUB4.SA":  "Itau Unibanco", "BBDC4.SA":  "Bradesco",
    "BBAS3.SA":  "Banco do Brasil","ABEV3.SA": "Ambev",
    "WEGE3.SA":  "WEG",           "RENT3.SA":  "Localiza",
    "MGLU3.SA":  "Magalu",        "SUZB3.SA":  "Suzano",
    "UGPA3.SA":  "Ultrapar",      "LREN3.SA":  "Lojas Renner",
    "RADL3.SA":  "Raia Drogasil", "TOTS3.SA":  "Totvs",
    "VIVT3.SA":  "Vivo/Telefonica","HAPV3.SA": "Hapvida",
    "RAIL3.SA":  "Rumo",          "CSAN3.SA":  "Cosan",
    "GGBR4.SA":  "Gerdau",        "KLBN11.SA": "Klabin",
    # Germany DAX
    "SAP.DE":    "SAP",           "SIE.DE":    "Siemens",
    "ALV.DE":    "Allianz",       "MRK.DE":    "Merck",
    "DTE.DE":    "Deutsche Telekom","MBG.DE":  "Mercedes-Benz",
    "BMW.DE":    "BMW",           "BAS.DE":    "BASF",
    "BAYN.DE":   "Bayer",         "ADS.DE":    "Adidas",
    "RWE.DE":    "RWE",           "VOW3.DE":   "Volkswagen",
    "IFX.DE":    "Infineon",      "ENR.DE":    "Siemens Energy",
    "HEN3.DE":   "Henkel",        "SHL.DE":    "Siemens Health",
    "DHL.DE":    "DHL Group",     "BEI.DE":    "Beiersdorf",
    "ZAL.DE":    "Zalando",       "CON.DE":    "Continental",
    # UK FTSE100
    "AZN.L":     "AstraZeneca",   "SHEL.L":    "Shell",
    "HSBA.L":    "HSBC",          "ULVR.L":    "Unilever",
    "BP.L":      "BP",            "RIO.L":     "Rio Tinto",
    "GSK.L":     "GSK",           "REL.L":     "RELX",
    "DGE.L":     "Diageo",        "VOD.L":     "Vodafone",
    "BATS.L":    "BAT",           "LLOY.L":    "Lloyds",
    "BARC.L":    "Barclays",      "NWG.L":     "NatWest",
    "PRU.L":     "Prudential",    "BHP.L":     "BHP",
    "GLEN.L":    "Glencore",      "AAL.L":     "Anglo American",
    "IMB.L":     "Imperial Brands","MKS.L":    "M&S",
    # France CAC40
    "MC.PA":     "LVMH",          "TTE.PA":    "TotalEnergies",
    "SAN.PA":    "Sanofi",        "BNP.PA":    "BNP Paribas",
    "OR.PA":     "L'Oreal",       "AIR.PA":    "Airbus",
    "RI.PA":     "Pernod Ricard", "CS.PA":     "AXA",
    "SU.PA":     "Schneider Elec","SGO.PA":    "Saint-Gobain",
    "ACA.PA":    "Credit Agricole","GLE.PA":   "Societe Generale",
    "BN.PA":     "Danone",        "KER.PA":    "Kering",
    "CAP.PA":    "Capgemini",     "PUB.PA":    "Publicis",
    "STM":       "STMicro",       "VIE.PA":    "Veolia",
    "LR.PA":     "Legrand",       "RNO.PA":    "Renault",
}

CONTINENT_ORDER = ["EUROPE", "AMERICAS", "ASIA", "COMMODITIES", "CRYPTO"]


def _currency(symbol: str) -> str:
    for ext, cur in CURRENCY_MAP.items():
        if symbol.endswith(ext):
            return cur
    return "$"


def _format_price(price: float, symbol: str) -> str:
    cur = _currency(symbol)
    if price >= 1000:
        return f"{cur}{price:,.0f}"
    elif price >= 100:
        return f"{cur}{price:.1f}"
    else:
        return f"{cur}{price:.2f}"


def _format_change(pct: float) -> str:
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


class FinanceFetcher(BaseFetcher):
    channel_id = "finance"
    sport_id   = "finance"

    def fetch(self, date_from: str, date_to: str) -> List[Dict]:
        cache_key = f"finance_{date_from}_{date_to}"
        today = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d")
        if date_from < today and date_to < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        # Determine yfinance period from date range
        try:
            from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            delta = (to_dt - from_dt).days
        except Exception:
            delta = 0

        if delta <= 1:
            yf_period = "5d"      # "Today" — need ≥2 days for % change
        elif delta <= 7:
            yf_period = "5d"      # "This Week"
        else:
            yf_period = "1mo"     # "This Month"

        rows: List[Dict] = []
        rows.extend(self._fetch_stocks(yf_period))
        rows.extend(self._fetch_commodities(yf_period))
        rows.extend(self._fetch_crypto())

        if date_from < today and date_to < today:
            self._save_cache(cache_key, rows)
        return rows

    def _fetch_stocks(self, yf_period: str = "5d") -> List[Dict]:
        rows = []
        for continent, markets in MARKETS.items():
            for market_name, market_info in markets.items():
                tickers = market_info["tickers"]
                country = market_info["country"]
                flag    = market_info["flag"]

                # Batch download: all tickers in ONE API call
                try:
                    data = yf.download(
                        tickers,
                        period=yf_period,
                        interval="1d",
                        auto_adjust=True,
                        progress=False,
                        threads=True,
                    )
                    close = data["Close"]
                except Exception as e:
                    print(f"[finance] Batch download failed {market_name}: {e}")
                    continue

                # Calculate daily % change for each ticker
                ticker_changes = []
                for ticker in tickers:
                    try:
                        series = close[ticker].dropna()
                        if len(series) < 2:
                            continue
                        prev = float(series.iloc[-2])
                        curr = float(series.iloc[-1])
                        if prev == 0:
                            continue
                        change_pct = (curr - prev) / prev * 100
                        ticker_changes.append({
                            "ticker": ticker,
                            "price":  curr,
                            "change": change_pct,
                        })
                    except Exception:
                        continue

                if not ticker_changes:
                    continue

                # Sort by abs(change), take top 3 gainers + top 2 losers
                gainers = sorted(
                    [t for t in ticker_changes if t["change"] >= 0],
                    key=lambda x: x["change"], reverse=True
                )[:3]
                losers = sorted(
                    [t for t in ticker_changes if t["change"] < 0],
                    key=lambda x: x["change"]
                )[:2]
                top5 = gainers + losers

                for item in top5:
                    ticker  = item["ticker"]
                    price   = item["price"]
                    change  = item["change"]
                    name = TICKER_NAMES.get(ticker) or ticker.split(".")[0]

                    rows.append({
                        "id":        f"fin-{market_name}-{ticker}",
                        "home":      name[:18],
                        "score":     _format_price(price, ticker),
                        "away":      _format_change(change),
                        "league":    market_name,
                        "category":  f"{flag} {country}",
                        "continent": continent,
                        "time":      ticker,
                        "status":    "\u25b2" if change >= 0 else "\u25bc",
                    })
        return rows

    def _fetch_commodities(self, yf_period: str = "5d") -> List[Dict]:
        commodities = {
            "GC=F": ("Gold",   "XAU", "$"),
            "SI=F": ("Silver", "XAG", "$"),
        }
        rows = []
        try:
            symbols = list(commodities.keys())
            data = yf.download(symbols, period=yf_period, interval="1d",
                              auto_adjust=True, progress=False)
            close = data["Close"]
            for symbol, (name, ticker_display, cur) in commodities.items():
                try:
                    series = close[symbol].dropna()
                    if len(series) < 2:
                        continue
                    prev   = float(series.iloc[-2])
                    curr   = float(series.iloc[-1])
                    change = (curr - prev) / prev * 100
                    rows.append({
                        "id":        f"fin-commodity-{symbol}",
                        "home":      name,
                        "score":     f"${curr:,.2f}/oz",
                        "away":      _format_change(change),
                        "league":    "COMMODITIES",
                        "category":  "\U0001f30d Global",
                        "continent": "COMMODITIES",
                        "time":      ticker_display,
                        "status":    "\u25b2" if change >= 0 else "\u25bc",
                    })
                except Exception as e:
                    print(f"[finance] Commodity {symbol}: {e}")
        except Exception as e:
            print(f"[finance] Commodities fetch failed: {e}")
        return rows

    def _fetch_crypto(self) -> List[Dict]:
        print("[finance] Fetching crypto from CoinGecko...")
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(CRYPTO_IDS),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            print(f"[finance] CoinGecko status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"[finance] CoinGecko error: {resp.text[:200]}")
                return []
            data = resp.json()
            print(f"[finance] CoinGecko data keys: {list(data.keys())}")
        except Exception as e:
            print(f"[finance] CoinGecko exception: {e}")
            return []

        rows = []
        for coin_id in CRYPTO_IDS:
            if coin_id not in data:
                print(f"[finance] Missing: {coin_id}")
                continue
            price  = data[coin_id].get("usd", 0)
            change = data[coin_id].get("usd_24h_change", 0) or 0
            name   = CRYPTO_NAMES.get(coin_id, coin_id)
            symbol = CRYPTO_SYMBOLS.get(coin_id, coin_id)
            rows.append({
                "id":        f"fin-crypto-{coin_id}",
                "home":      name,
                "score":     f"${price:,.2f}" if price >= 1 else f"${price:.4f}",
                "away":      _format_change(change),
                "league":    "CRYPTO",
                "category":  "\U0001f310 Global",
                "continent": "CRYPTO",
                "time":      symbol,
                "status":    "\u25b2" if change >= 0 else "\u25bc",
            })
        print(f"[finance] Crypto rows: {len(rows)}")
        return rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        # Order: EUROPE -> AMERICAS -> ASIA -> COMMODITIES -> CRYPTO
        by_continent = defaultdict(list)
        for item in items:
            cont = item.get("continent", item.get("category", "OTHER"))
            by_continent[cont].append(item)

        groups = []
        for cont in CONTINENT_ORDER:
            if cont not in by_continent:
                continue
            # Sub-group by league within continent
            by_league = defaultdict(list)
            for item in by_continent[cont]:
                by_league[item["league"]].append(item)

            for league, league_items in by_league.items():
                country_label = league_items[0].get("category", cont)
                groups.append({
                    "league":       league,
                    "display_name": f"{country_label} \u00b7 {league}",
                    "continent":    cont,
                    "matches":      league_items,
                })
        return groups
