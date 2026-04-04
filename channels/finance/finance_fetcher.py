"""
@ayaz_finance — Stock & crypto market fetcher.
Uses yfinance for stocks, CoinGecko for crypto.
"""

import os
import sys
import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from channels.base_fetcher import BaseFetcher

try:
    import yfinance as yf
except ImportError:
    raise ImportError("Run: pip install yfinance")

MARKETS = {
    "EUROPE": {
        "DAX":     ["SAP.DE", "SIE.DE", "BAS.DE", "ALV.DE", "BMW.DE"],
        "BIST100": ["GARAN.IS", "AKBNK.IS", "EREGL.IS", "KCHOL.IS", "THYAO.IS"],
        "FTSE100": ["AZN.L", "SHEL.L", "ULVR.L", "BP.L", "RIO.L"],
    },
    "AMERICAS": {
        "SP500":   ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"],
        "NASDAQ":  ["META", "TSLA", "AVGO", "ADBE", "COST"],
        "BOVESPA": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    },
    "ASIA": {
        "NIKKEI":  ["7203.T", "9984.T", "6758.T", "8306.T", "9432.T"],
        "KOSPI":   ["005930.KS", "000660.KS", "035420.KS"],
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
    ".DE": "€", ".IS": "₺", ".L": "£", ".PA": "€",
    ".SA": "R$", ".T": "¥", ".KS": "₩",
}

CONTINENT_ORDER = ["EUROPE", "AMERICAS", "ASIA", "CRYPTO"]


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
        cache_key = f"finance_{date_from}"
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if date_from < today:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        rows: List[Dict] = []
        rows.extend(self._fetch_stocks())
        rows.extend(self._fetch_crypto())

        if date_from < today:
            self._save_cache(cache_key, rows)
        return rows

    def _fetch_stocks(self) -> List[Dict]:
        rows = []
        for continent, markets in MARKETS.items():
            for market, symbols in markets.items():
                for symbol in symbols:
                    try:
                        time.sleep(0.3)
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="2d")
                        if len(hist) < 2:
                            continue
                        prev  = float(hist["Close"].iloc[-2])
                        curr  = float(hist["Close"].iloc[-1])
                        change_pct = (curr - prev) / prev * 100

                        info = ticker.info
                        name = (info.get("shortName") or
                                info.get("longName") or symbol)[:18]

                        rows.append({
                            "id":       f"fin-{symbol}",
                            "home":     name,
                            "score":    _format_price(curr, symbol),
                            "away":     _format_change(change_pct),
                            "league":   market,
                            "category": continent,
                            "time":     symbol,
                            "status":   "▲" if change_pct >= 0 else "▼",
                        })
                    except Exception as e:
                        print(f"[finance] {symbol} error: {e}")
        return rows

    def _fetch_crypto(self) -> List[Dict]:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": ",".join(CRYPTO_IDS),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[finance] crypto error: {e}")
            return []

        rows = []
        for coin_id in CRYPTO_IDS:
            d = data.get(coin_id, {})
            price  = d.get("usd", 0)
            change = d.get("usd_24h_change", 0)
            rows.append({
                "id":       f"fin-crypto-{coin_id}",
                "home":     CRYPTO_NAMES[coin_id],
                "score":    f"${price:,.0f}" if price >= 1000 else f"${price:.2f}",
                "away":     _format_change(change),
                "league":   "CRYPTO",
                "category": "CRYPTO",
                "time":     CRYPTO_SYMBOLS[coin_id],
                "status":   "▲" if change >= 0 else "▼",
            })
        return rows

    def to_reel_groups(self, items: List[Dict]) -> List[Dict]:
        cat_map: dict = {}
        for item in items:
            cat = item["category"]
            mkt = item["league"]
            cat_map.setdefault(cat, {}).setdefault(mkt, []).append(item)

        groups = []
        for continent in CONTINENT_ORDER:
            if continent not in cat_map:
                continue
            for market, matches in cat_map[continent].items():
                groups.append({
                    "league":       market,
                    "display_name": market,
                    "matches":      matches,
                })
        return groups
