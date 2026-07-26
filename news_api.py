import os
import time
from datetime import datetime, timedelta
import requests

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

_cache = {}
CACHE_TTL_SECONDS = 300  # news changes slowly - cache 5 minutes


def _get_api_key():
    return os.environ.get("FINNHUB_API_KEY")


def _is_cache_fresh(ticker):
    entry = _cache.get(ticker)
    if not entry:
        return False
    return (time.time() - entry["timestamp"]) < CACHE_TTL_SECONDS


def get_news(ticker, limit=5):
    """
    Fetch recent company news headlines for a ticker from Finnhub.
    Returns a list of dicts: {"title": str, "source": str, "url": str, "published": str}
    Never raises - returns an empty list on any failure so the UI can show an empty state.
    """
    if _is_cache_fresh(ticker):
        return _cache[ticker]["data"]

    api_key = _get_api_key()
    if not api_key:
        return []

    try:
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)

        resp = requests.get(
            f"{FINNHUB_BASE_URL}/company-news",
            params={
                "symbol": ticker,
                "from": week_ago.isoformat(),
                "to": today.isoformat(),
                "token": api_key,
            },
            timeout=5,
        )
        resp.raise_for_status()
        articles = resp.json()

        if not isinstance(articles, list):
            _cache[ticker] = {"data": [], "timestamp": time.time()}
            return []

        results = []
        for article in articles[:limit]:
            published = ""
            if article.get("datetime"):
                published = datetime.utcfromtimestamp(article["datetime"]).strftime("%b %d, %Y")
            results.append({
                "title": article.get("headline", "Untitled"),
                "source": article.get("source", "Unknown source"),
                "url": article.get("url", "#"),
                "published": published,
            })

        _cache[ticker] = {"data": results, "timestamp": time.time()}
        return results

    except (requests.RequestException, ValueError):
        _cache[ticker] = {"data": [], "timestamp": time.time()}
        return []
