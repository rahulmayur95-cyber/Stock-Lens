import os
import time
import requests

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Simple in-memory cache: { ticker: {"data": {...}, "timestamp": epoch_seconds} }
_cache = {}
CACHE_TTL_SECONDS = 60
NEGATIVE_CACHE_TTL_SECONDS = 15  # cache failures briefly too, so one bad ticker
                                   # doesn't hammer Finnhub on every page load


def _get_api_key():
    return os.environ.get("FINNHUB_API_KEY")


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


def _fetch_quote_once(ticker, api_key):
    """Single attempt at fetching quote + fundamentals. May raise requests exceptions."""
    quote_resp = requests.get(
        f"{FINNHUB_BASE_URL}/quote",
        params={"symbol": ticker, "token": api_key},
        timeout=5,
    )
    quote_resp.raise_for_status()
    quote_data = quote_resp.json()

    price = quote_data.get("c")
    change_percent = quote_data.get("dp")

    if price is None or price == 0:
        return {"price": None, "change_percent": None, "pe_ratio": None, "available": False}

    pe_ratio = None
    try:
        metric_resp = requests.get(
            f"{FINNHUB_BASE_URL}/stock/metric",
            params={"symbol": ticker, "metric": "all", "token": api_key},
            timeout=5,
        )
        metric_resp.raise_for_status()
        metric_data = metric_resp.json()
        pe_ratio = metric_data.get("metric", {}).get("peNormalizedAnnual")
    except (requests.RequestException, ValueError):
        pe_ratio = None  # fundamentals are optional - quote can still succeed

    return {
        "price": round(price, 2),
        "change_percent": round(change_percent, 2) if change_percent is not None else None,
        "pe_ratio": round(pe_ratio, 2) if pe_ratio is not None else None,
        "available": True,
    }


def get_quote(ticker):
    """
    Fetch price, % change, and P/E ratio for a ticker from Finnhub.
    Returns a dict: {"price": float, "change_percent": float, "pe_ratio": float or None, "available": bool}
    Never raises - on any failure, returns available=False so the UI can show a fallback.
    Retries once on transient network errors before giving up.
    """
    cached = _get_cached(ticker)
    if cached is not None:
        return cached

    api_key = _get_api_key()
    if not api_key:
        return _store(ticker, {"price": None, "change_percent": None, "pe_ratio": None, "available": False})

    last_error = None
    for attempt in range(2):  # try once, retry once on failure
        try:
            result = _fetch_quote_once(ticker, api_key)
            return _store(ticker, result)
        except (requests.RequestException, ValueError) as e:
            last_error = e
            if attempt == 0:
                time.sleep(0.3)  # brief pause before retry
            continue

    # Both attempts failed
    return _store(ticker, {"price": None, "change_percent": None, "pe_ratio": None, "available": False})
