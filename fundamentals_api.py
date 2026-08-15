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
    "pb_ratio": None,
    "ps_ratio": None,
}

EMPTY_TRENDS = {
    "available": False,
    "quarters": [],
    "revenue": [],
    "net_income": [],
    "eps": [],
    "free_cash_flow": [],
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
        "pb_ratio": _round(info.get("priceToBook"), 2),
        "ps_ratio": _round(info.get("priceToSalesTrailing12Months"), 2),
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


_trends_cache = {}
TRENDS_CACHE_TTL_SECONDS = 3600
TRENDS_NEGATIVE_CACHE_TTL_SECONDS = 120

# yfinance's row labels vary slightly by ticker/region - try each candidate in order.
_REVENUE_ROWS = ["Total Revenue", "TotalRevenue"]
_NET_INCOME_ROWS = ["Net Income", "NetIncome", "Net Income Common Stockholders"]
_EPS_ROWS = ["Diluted EPS", "Basic EPS"]
_FCF_ROWS = ["Free Cash Flow", "FreeCashFlow"]


def _get_trends_cached(ticker):
    entry = _trends_cache.get(ticker)
    if not entry:
        return None
    ttl = TRENDS_CACHE_TTL_SECONDS if entry["data"]["available"] else TRENDS_NEGATIVE_CACHE_TTL_SECONDS
    if (time.time() - entry["timestamp"]) < ttl:
        return entry["data"]
    return None


def _row_values(df, candidate_names, num_quarters):
    """Pull a row from a yfinance quarterly statement DataFrame by trying each
    candidate row name, oldest-to-newest, limited to num_quarters. Returns None
    if no candidate row exists."""
    if df is None or df.empty:
        return None
    for name in candidate_names:
        if name in df.index:
            row = df.loc[name].dropna()
            row = row.sort_index()  # oldest -> newest, left to right on the chart
            row = row.iloc[-num_quarters:]
            return [round(float(v), 2) for v in row]
    return None


def _fetch_trends_once(ticker, num_quarters=8):
    tk = yf.Ticker(ticker, session=_session)
    income_stmt = tk.quarterly_income_stmt
    cashflow = tk.quarterly_cashflow

    if income_stmt is None or income_stmt.empty:
        return dict(EMPTY_TRENDS)

    revenue = _row_values(income_stmt, _REVENUE_ROWS, num_quarters)
    net_income = _row_values(income_stmt, _NET_INCOME_ROWS, num_quarters)
    eps = _row_values(income_stmt, _EPS_ROWS, num_quarters)
    fcf = _row_values(cashflow, _FCF_ROWS, num_quarters)

    if revenue is None and net_income is None and eps is None and fcf is None:
        return dict(EMPTY_TRENDS)

    # Quarter labels come from whichever series is longest/most reliable (revenue, usually)
    quarter_source = None
    for name in _REVENUE_ROWS:
        if name in income_stmt.index:
            quarter_source = income_stmt.loc[name].dropna().sort_index().iloc[-num_quarters:]
            break
    quarters = [d.strftime("%b %Y") for d in quarter_source.index] if quarter_source is not None else []

    return {
        "available": True,
        "quarters": quarters,
        "revenue": revenue or [],
        "net_income": net_income or [],
        "eps": eps or [],
        "free_cash_flow": fcf or [],
    }


def get_fundamental_trends(ticker):
    """
    Fetch recent quarterly Revenue, Net Income, EPS, and Free Cash Flow for a
    ticker, for the fundamentals trend charts on the stock detail page.
    Never raises - on any failure, returns an "unavailable" result. Retries
    once on transient errors.
    """
    cached = _get_trends_cached(ticker)
    if cached is not None:
        return cached

    for attempt in range(2):
        try:
            result = _fetch_trends_once(ticker)
            _trends_cache[ticker] = {"data": result, "timestamp": time.time()}
            return result
        except Exception as e:
            print(f"[fundamentals_api] get_fundamental_trends({ticker}) attempt {attempt} failed: {e!r}", file=sys.stderr, flush=True)
            if attempt == 0:
                time.sleep(0.3)
            continue

    result = dict(EMPTY_TRENDS)
    _trends_cache[ticker] = {"data": result, "timestamp": time.time()}
    return result


def format_large_number(value, currency_symbol):
    """Format a raw large number (market cap, revenue, net income, etc.) into a
    readable string, e.g. $2.95T, ₹18.2L Cr, or ($120.00M) for negatives."""
    if value is None:
        return "N/A"

    negative = value < 0
    abs_value = abs(value)
    formatted = format_market_cap(abs_value, currency_symbol)
    return f"({formatted})" if negative else formatted


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
