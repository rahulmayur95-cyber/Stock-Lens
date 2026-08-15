"""
Live quote fetching for Indian (NSE) stocks via yfinance.

Finnhub's free tier doesn't reliably cover NSE/BSE tickers, so Indian stocks
use yfinance instead (free, no API key required, pulls from Yahoo Finance).
This mirrors stock_api.py's shape/caching so app.py can treat both the same way.
"""

import sys
import time
import yfinance as yf
from curl_cffi import requests as curl_requests

# yfinance's default requests session gets silently blocked by Yahoo Finance on
# many cloud/datacenter IPs (Render, AWS, etc.) even though it works fine from
# a home connection. Impersonating a real browser's TLS/HTTP fingerprint via
# curl_cffi is yfinance's own documented workaround for this.
_session = curl_requests.Session(impersonate="chrome")

# Simple in-memory cache: { ticker: {"data": {...}, "timestamp": epoch_seconds} }
_cache = {}
CACHE_TTL_SECONDS = 60
NEGATIVE_CACHE_TTL_SECONDS = 15


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


def _fetch_quote_once(ticker):
    """Single attempt at fetching an Indian stock quote via yfinance. May raise exceptions."""
    tk = yf.Ticker(ticker, session=_session)

    # Last 5 trading days of daily closes is enough to get latest price + % change
    # without the heavier/slower full "info" scrape.
    hist = tk.history(period="5d", interval="1d")

    if hist is None or hist.empty or "Close" not in hist:
        return {"price": None, "change_percent": None, "pe_ratio": None, "available": False}

    closes = hist["Close"].dropna()
    if len(closes) == 0:
        return {"price": None, "change_percent": None, "pe_ratio": None, "available": False}

    price = float(closes.iloc[-1])
    prev_close = float(closes.iloc[-2]) if len(closes) > 1 else price
    change_percent = ((price - prev_close) / prev_close) * 100 if prev_close else None

    pe_ratio = None
    try:
        info = tk.get_info()
        pe_ratio = info.get("trailingPE")
    except Exception:
        pe_ratio = None  # fundamentals are optional - quote can still succeed

    return {
        "price": round(price, 2),
        "change_percent": round(change_percent, 2) if change_percent is not None else None,
        "pe_ratio": round(pe_ratio, 2) if isinstance(pe_ratio, (int, float)) else None,
        "available": True,
    }


def get_quote_indian(ticker):
    """
    Fetch price, % change, and P/E ratio for an Indian (NSE) ticker via yfinance.
    Returns a dict: {"price": float, "change_percent": float, "pe_ratio": float or None, "available": bool}
    Never raises - on any failure, returns available=False so the UI can show a fallback.
    Retries once on transient errors before giving up.
    """
    cached = _get_cached(ticker)
    if cached is not None:
        return cached

    for attempt in range(2):  # try once, retry once on failure
        try:
            result = _fetch_quote_once(ticker)
            return _store(ticker, result)
        except Exception as e:
            print(f"[indian_stock_api] get_quote_indian({ticker}) attempt {attempt} failed: {e!r}", file=sys.stderr, flush=True)
            if attempt == 0:
                time.sleep(0.3)
            continue

    return _store(ticker, {"price": None, "change_percent": None, "pe_ratio": None, "available": False})
