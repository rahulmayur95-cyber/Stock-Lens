import os
import sys
import time
from datetime import datetime, timedelta
import requests
import yfinance as yf
from yf_session import get_session

from tickers import is_indian_ticker

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


def _get_news_yfinance(ticker, limit):
    """
    Fetch news via yfinance. Used for Indian tickers (Finnhub's free tier
    doesn't cover NSE/BSE company news) and as a fallback for anything
    Finnhub returns nothing for.
    """
    try:
        tk = yf.Ticker(ticker, session=get_session())
        items = tk.get_news(count=limit) or []
    except Exception as e:
        print(f"[news_api] yfinance news for {ticker} failed: {e!r}", file=sys.stderr, flush=True)
        return []

    results = []
    for item in items[:limit]:
        # yfinance news items nest most fields under "content" as of recent versions
        content = item.get("content", item)
        title = content.get("title", "Untitled")
        source = (content.get("provider") or {}).get("displayName", "Yahoo Finance")
        url = ((content.get("canonicalUrl") or {}).get("url")
               or (content.get("clickThroughUrl") or {}).get("url")
               or "#")
        published = ""
        pub_date = content.get("pubDate")
        if pub_date:
            try:
                published = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
            except ValueError:
                published = pub_date[:10]

        results.append({"title": title, "source": source, "url": url, "published": published})

    return results


def _get_news_finnhub(ticker, limit):
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
        return results

    except (requests.RequestException, ValueError):
        return []


def get_news(ticker, limit=5):
    """
    Fetch recent company news headlines for a ticker.
    Indian (.NS/.BO) tickers go straight to yfinance (Finnhub doesn't cover
    NSE/BSE news); other tickers try Finnhub first and fall back to yfinance
    if Finnhub has nothing.
    Returns a list of dicts: {"title": str, "source": str, "url": str, "published": str}
    Never raises - returns an empty list on any failure so the UI can show an empty state.
    """
    if _is_cache_fresh(ticker):
        return _cache[ticker]["data"]

    if is_indian_ticker(ticker):
        results = _get_news_yfinance(ticker, limit)
    else:
        results = _get_news_finnhub(ticker, limit)
        if not results:
            results = _get_news_yfinance(ticker, limit)

    _cache[ticker] = {"data": results, "timestamp": time.time()}
    return results
