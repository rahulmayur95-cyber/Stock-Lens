import os
import time
import requests

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Simple in-memory cache: { ticker: {"data": {...}, "timestamp": epoch_seconds} }
_cache = {}
CACHE_TTL_SECONDS = 60


def _get_api_key():
    return os.environ.get("FINNHUB_API_KEY")


def _is_cache_fresh(ticker):
    entry = _cache.get(ticker)
    if not entry:
        return False
    return (time.time() - entry["timestamp"]) < CACHE_TTL_SECONDS


def get_quote(ticker):
    """
    Fetch price, % change, and P/E ratio for a ticker from Finnhub.
    Returns a dict: {"price": float, "change_percent": float, "pe_ratio": float or None, "available": bool}
    Never raises — on any failure, returns available=False so the UI can show a fallback.
    """
    if _is_cache_fresh(ticker):
        return _cache[ticker]["data"]

    api_key = _get_api_key()
    if not api_key:
        return {"price": None, "change_percent": None, "pe_ratio": None, "available": False}

    try:
        # /quote endpoint: current price + % change
        quote_resp = requests.get(
            f"{FINNHUB_BASE_URL}/quote",
            params={"symbol": ticker, "token": api_key},
            timeout=5,
        )
        quote_resp.raise_for_status()
        quote_data = quote_resp.json()

        price = quote_data.get("c")  # current price
        change_percent = quote_data.get("dp")  # percent change

        # Finnhub returns 0/None for unknown symbols instead of an error - treat as unavailable
        if price is None or price == 0:
            result = {"price": None, "change_percent": None, "pe_ratio": None, "available": False}
            _cache[ticker] = {"data": result, "timestamp": time.time()}
            return result

        # /stock/metric endpoint: fundamentals including P/E
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

        result = {
            "price": round(price, 2),
            "change_percent": round(change_percent, 2) if change_percent is not None else None,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio is not None else None,
            "available": True,
        }
        _cache[ticker] = {"data": result, "timestamp": time.time()}
        return result

    except (requests.RequestException, ValueError):
        # Network error, timeout, bad JSON, etc. - fail gracefully
        result = {"price": None, "change_percent": None, "pe_ratio": None, "available": False}
        _cache[ticker] = {"data": result, "timestamp": time.time()}
        return result
