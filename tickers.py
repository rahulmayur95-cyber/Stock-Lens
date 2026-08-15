"""
Curated list of popular stock tickers for StockLens v1.0.
This is a fixed reference list (not a database table) used as a fast,
reliable first pass for search, plus a fallback if live lookups fail.
For anything outside this list, StockLens validates/looks up tickers live
via Yahoo Finance (see stock_search_api.py for search, and the live lookups
below for validation and company names) so any real NSE/BSE or US stock can
be added, not just the ones curated here.
See ARCHITECTURE.md and SCHEMA.md for rationale.
"""

import re
import sys
import time
import yfinance as yf
from yf_session import get_session

TICKERS = [
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Class A)"},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation"},
    {"ticker": "META", "name": "Meta Platforms Inc."},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc."},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "PG", "name": "Procter & Gamble Co."},
    {"ticker": "MA", "name": "Mastercard Inc."},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "DIS", "name": "Walt Disney Co."},
    {"ticker": "BAC", "name": "Bank of America Corp."},
    {"ticker": "ADBE", "name": "Adobe Inc."},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "KO", "name": "Coca-Cola Co."},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "INTC", "name": "Intel Corporation"},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "MCD", "name": "McDonald's Corp."},
    {"ticker": "COST", "name": "Costco Wholesale Corp."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "TXN", "name": "Texas Instruments Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "IBM", "name": "International Business Machines Corp."},
    {"ticker": "GE", "name": "General Electric Co."},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "BA", "name": "Boeing Co."},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "SBUX", "name": "Starbucks Corp."},
    {"ticker": "UBER", "name": "Uber Technologies Inc."},
    {"ticker": "PYPL", "name": "PayPal Holdings Inc."},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "ABNB", "name": "Airbnb Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
    {"ticker": "SPOT", "name": "Spotify Technology SA"},
    {"ticker": "COIN", "name": "Coinbase Global Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc."},
    {"ticker": "SQ", "name": "Block Inc."},
    {"ticker": "F", "name": "Ford Motor Co."},
    {"ticker": "GM", "name": "General Motors Co."},
    {"ticker": "DELL", "name": "Dell Technologies Inc."},
    {"ticker": "HPQ", "name": "HP Inc."},
    {"ticker": "MU", "name": "Micron Technology Inc."},
    {"ticker": "NOW", "name": "ServiceNow Inc."},
]

# Curated list of popular Indian (NSE-listed) tickers for StockLens.
# Ticker symbols use the ".NS" suffix, matching Yahoo Finance's NSE convention
# (StockLens fetches Indian quotes/history via yfinance - see indian_stock_api.py).
INDIAN_TICKERS = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd. (NSE)"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd. (NSE)"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd. (NSE)"},
    {"ticker": "INFY.NS", "name": "Infosys Ltd. (NSE)"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd. (NSE)"},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd. (NSE)"},
    {"ticker": "SBIN.NS", "name": "State Bank of India (NSE)"},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd. (NSE)"},
    {"ticker": "ITC.NS", "name": "ITC Ltd. (NSE)"},
    {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd. (NSE)"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd. (NSE)"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd. (NSE)"},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd. (NSE)"},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd. (NSE)"},
    {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd. (NSE)"},
    {"ticker": "TITAN.NS", "name": "Titan Company Ltd. (NSE)"},
    {"ticker": "ASIANPAINT.NS", "name": "Asian Paints Ltd. (NSE)"},
    {"ticker": "WIPRO.NS", "name": "Wipro Ltd. (NSE)"},
    {"ticker": "ADANIENT.NS", "name": "Adani Enterprises Ltd. (NSE)"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd. (NSE)"},
    {"ticker": "TATASTEEL.NS", "name": "Tata Steel Ltd. (NSE)"},
    {"ticker": "NTPC.NS", "name": "NTPC Ltd. (NSE)"},
    {"ticker": "ONGC.NS", "name": "Oil & Natural Gas Corporation Ltd. (NSE)"},
    {"ticker": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd. (NSE)"},
    {"ticker": "HCLTECH.NS", "name": "HCL Technologies Ltd. (NSE)"},
    {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd. (NSE)"},
    {"ticker": "NESTLEIND.NS", "name": "Nestle India Ltd. (NSE)"},
    {"ticker": "JSWSTEEL.NS", "name": "JSW Steel Ltd. (NSE)"},
    {"ticker": "ZOMATO.NS", "name": "Eternal Ltd. (Zomato) (NSE)"},
    {"ticker": "IRFC.NS", "name": "Indian Railway Finance Corporation Ltd. (NSE)"},
]

# Combined list used everywhere in the app (search, validation, lookups).
TICKERS = TICKERS + INDIAN_TICKERS


def is_indian_ticker(ticker: str) -> bool:
    """Indian (NSE/BSE) tickers use the .NS or .BO suffix, per Yahoo Finance convention."""
    return ticker.upper().endswith((".NS", ".BO"))


def get_currency_symbol(ticker: str) -> str:
    """Return the display currency symbol for a ticker."""
    return "\u20b9" if is_indian_ticker(ticker) else "$"


def search_tickers(query: str):
    """Return curated tickers matching a query by symbol or company name (case-insensitive).
    This only searches the small curated list - see stock_search_api.py for full-market search."""
    if not query:
        return TICKERS
    q = query.strip().lower()
    return [t for t in TICKERS if q in t["ticker"].lower() or q in t["name"].lower()]


# --- Live validation/lookup for tickers outside the curated list -----------
# StockLens's watchlist accepts any real NSE/BSE or US stock, not just the
# ~90 curated above. For anything not in the curated list, we confirm it's a
# real ticker (and later, its display name) via a live Yahoo Finance lookup,
# caching results so repeat visits don't re-hit the network every time.

_TICKER_FORMAT = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,14}$")

_validity_cache = {}  # ticker -> {"valid": bool, "name": str or None, "timestamp": epoch}
VALID_CACHE_TTL_SECONDS = 86400   # confirmed-real tickers rarely stop existing - cache 1 day
INVALID_CACHE_TTL_SECONDS = 300   # could be a transient failure - only cache 5 minutes


def _curated_lookup(ticker: str):
    for t in TICKERS:
        if t["ticker"] == ticker:
            return t["name"]
    return None


def _get_cached_validity(ticker):
    entry = _validity_cache.get(ticker)
    if not entry:
        return None
    ttl = VALID_CACHE_TTL_SECONDS if entry["valid"] else INVALID_CACHE_TTL_SECONDS
    if (time.time() - entry["timestamp"]) < ttl:
        return entry
    return None


def _live_lookup(ticker: str):
    """Confirm a ticker is real via yfinance, and grab its display name while we're at it.
    Returns (valid: bool, name: str or None). Never raises."""
    try:
        info = yf.Ticker(ticker, session=get_session()).get_info()
        if not info or not info.get("symbol"):
            return False, None
        name = info.get("longName") or info.get("shortName") or ticker
        return True, name
    except Exception as e:
        print(f"[tickers] live lookup for {ticker!r} failed: {e!r}", file=sys.stderr, flush=True)
        return False, None


def is_valid_ticker(ticker: str) -> bool:
    """Check whether a ticker is real: curated list first (instant), then a
    live Yahoo Finance check for anything else (cached to avoid repeat network calls)."""
    ticker = ticker.upper().strip()

    if not _TICKER_FORMAT.match(ticker):
        return False

    if _curated_lookup(ticker) is not None:
        return True

    cached = _get_cached_validity(ticker)
    if cached is not None:
        return cached["valid"]

    valid, name = _live_lookup(ticker)
    _validity_cache[ticker] = {"valid": valid, "name": name, "timestamp": time.time()}
    return valid


def get_company_name(ticker: str) -> str:
    """Look up the company name for a given ticker: curated list first, then
    a live/cached Yahoo Finance lookup, falling back to the ticker itself."""
    curated_name = _curated_lookup(ticker)
    if curated_name is not None:
        return curated_name

    cached = _get_cached_validity(ticker)
    if cached is not None and cached["name"]:
        return cached["name"]

    valid, name = _live_lookup(ticker)
    _validity_cache[ticker] = {"valid": valid, "name": name, "timestamp": time.time()}
    return name or ticker
