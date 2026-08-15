"""
Live stock search across the whole market (NSE, BSE, and US exchanges),
not just StockLens's curated ~90-ticker list.

Uses yfinance's Search (Yahoo Finance's own search/autocomplete API) so users
can find and add ANY publicly listed Indian or US stock, not only the
hand-picked ones in tickers.py. The curated list is still used as a fast,
reliable first pass and as a fallback if the live search fails.
"""

import sys
import time
import yfinance as yf
from yf_session import get_session

from tickers import search_tickers as search_curated

_cache = {}
CACHE_TTL_SECONDS = 300  # search results don't need to be second-fresh


def _get_cached(query):
    entry = _cache.get(query)
    if entry and (time.time() - entry["timestamp"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _store(query, data):
    _cache[query] = {"data": data, "timestamp": time.time()}
    return data


def _display_name(quote):
    return quote.get("longname") or quote.get("shortname") or quote.get("symbol", "")


def _search_live(query, limit):
    try:
        results = yf.Search(query, max_results=limit, session=get_session()).quotes
    except Exception as e:
        print(f"[stock_search_api] live search for {query!r} failed: {e!r}", file=sys.stderr, flush=True)
        return []

    matches = []
    for quote in results:
        if quote.get("quoteType") != "EQUITY":
            continue  # skip ETFs, indices, options, crypto, etc.
        symbol = quote.get("symbol")
        if not symbol:
            continue
        exchange = quote.get("exchDisp", "")
        name = _display_name(quote)
        if exchange in ("NSE", "BSE"):
            name = f"{name} ({exchange})"
        matches.append({"ticker": symbol, "name": name})

    return matches


def search_stocks(query, limit=12):
    """
    Search for stocks by ticker or company name across the whole market.
    Combines the curated list (fast, always available) with live results
    from Yahoo Finance's search API (covers the full NSE/BSE and US markets).
    Never raises - falls back to curated-only results if the live search fails.
    """
    query = query.strip()
    if not query:
        return []

    cached = _get_cached(query.lower())
    if cached is not None:
        return cached[:limit]

    curated_matches = search_curated(query)
    seen_tickers = {m["ticker"] for m in curated_matches}

    live_matches = _search_live(query, limit)
    for match in live_matches:
        if match["ticker"] not in seen_tickers:
            curated_matches.append(match)
            seen_tickers.add(match["ticker"])

    return _store(query.lower(), curated_matches)[:limit]
