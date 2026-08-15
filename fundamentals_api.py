"""
Key fundamental/valuation metrics for the stock detail page (Market Cap,
ROE, Dividend Yield, EPS, Book Value, 52-week range, Debt-to-Equity).

Uses yfinance for both US and Indian tickers, since Finnhub's free tier
doesn't expose most of these fields (especially not for NSE/BSE tickers).
"""

import sys
import time
import yfinance as yf
from curl_cffi import requests as curl_requests

# See indian_stock_api.py for why this session exists.
_session = curl_requests.Session(impersonate="chrome")

_cache = {}
CACHE_TTL_SECONDS = 3600  # fundamentals change slowly - cache 1 hour
NEGATIVE_CACHE_TTL_SECONDS = 120

EMPTY_RESULT = {
    "available": False,
    "market_cap": None,
    "roe": None,
    "dividend_yield": None,
    "eps": None,
    "book_value": None,
    "week52_high": None,
    "week52_low": None,
    "debt_to_equity": None,
    "profit_margin": None,
}


def _get_cached(ticker):
    entry = _cache.get(ticker)
    if not entry:
        return None
    ttl = CACHE_TTL_SECONDS if entry["data"]["available"] else NEGATIVE_CACHE_TTL_SECONDS
    if (time.time() - entry["timestamp"]) < ttl:
        return entry["data"]
    return None


def _store(ticker, data):
    _cache[ticker] = {"data": data, "timestamp": time.time()}
    return data


def _round(value, digits=2):
    return round(value, digits) if isinstance(value, (int, float)) else None


def _fetch_once(ticker):
    tk = yf.Ticker(ticker, session=_session)
    info = tk.get_info() or {}

    if not info:
        return dict(EMPTY_RESULT)

    roe = info.get("returnOnEquity")
    dividend_yield = info.get("dividendYield")
    profit_margin = info.get("profitMargins")

    return {
        "available": True,
        "market_cap": info.get("marketCap"),
        # yfinance returns these as decimals (0.15 = 15%) - convert to percent for display
        "roe": _round(roe * 100, 1) if isinstance(roe, (int, float)) else None,
        "dividend_yield": _round(dividend_yield * 100, 2) if isinstance(dividend_yield, (int, float)) else None,
        "eps": _round(info.get("trailingEps"), 2),
        "book_value": _round(info.get("bookValue"), 2),
        "week52_high": _round(info.get("fiftyTwoWeekHigh"), 2),
        "week52_low": _round(info.get("fiftyTwoWeekLow"), 2),
        "debt_to_equity": _round(info.get("debtToEquity"), 2),
        "profit_margin": _round(profit_margin * 100, 1) if isinstance(profit_margin, (int, float)) else None,
    }


def get_fundamentals(ticker):
    """
    Fetch key valuation/fundamental metrics for a ticker.
    Never raises - on any failure, returns an "unavailable" result so the UI
    can show a fallback instead of erroring. Retries once on transient errors.
    """
    cached = _get_cached(ticker)
    if cached is not None:
        return cached

    for attempt in range(2):
        try:
            result = _fetch_once(ticker)
            return _store(ticker, result)
        except Exception as e:
            print(f"[fundamentals_api] get_fundamentals({ticker}) attempt {attempt} failed: {e!r}", file=sys.stderr, flush=True)
            if attempt == 0:
                time.sleep(0.3)
            continue

    return _store(ticker, dict(EMPTY_RESULT))


def format_market_cap(value, currency_symbol):
    """Format a raw market cap number into a readable string, e.g. $2.95T or ₹18.2L Cr."""
    if value is None:
        return "N/A"

    if currency_symbol == "\u20b9":
        # Indian convention: Lakh Crore (1 Lakh Cr = 1 trillion rupees)
        lakh_cr = value / 1_00_00_00_00_000  # 1 Lakh Crore = 10^12
        if lakh_cr >= 1:
            return f"\u20b9{lakh_cr:.2f}L Cr"
        cr = value / 1_00_00_000  # 1 Crore = 10^7
        return f"\u20b9{cr:.0f} Cr"

    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"
