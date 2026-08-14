"""
Historical price data + technical indicators for StockLens charts and the
Buy/Sell/Hold signal engine.

Uses yfinance for ALL tickers (US and Indian), not just Indian ones: Finnhub's
free tier no longer includes historical candle data for stocks, so yfinance
(free, no API key) is the single source for chart history.
"""

import time
import pandas as pd
import yfinance as yf

_cache = {}
CACHE_TTL_SECONDS = 900  # history changes slowly intraday - cache 15 minutes
NEGATIVE_CACHE_TTL_SECONDS = 60

EMPTY_RESULT = {
    "available": False,
    "dates": [],
    "close": [],
    "sma20": [],
    "sma50": [],
    "rsi": [],
    "macd": [],
    "macd_signal": [],
    "latest": {"close": None, "sma20": None, "sma50": None, "rsi": None, "macd": None, "macd_signal": None},
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


def _none_if_nan(value):
    if value is None or pd.isna(value):
        return None
    return round(float(value), 4)


def _series_to_list(series):
    return [_none_if_nan(v) for v in series]


def _compute_indicators(close: pd.Series):
    sma20 = close.rolling(window=20).mean()
    sma50 = close.rolling(window=50).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    # Where avg_loss is 0 (all gains, no losses) RSI is 100
    rsi = rsi.where(avg_loss != 0, 100.0)

    return sma20, sma50, rsi, macd, macd_signal


def _fetch_once(ticker, period):
    tk = yf.Ticker(ticker)
    hist = tk.history(period=period, interval="1d")

    if hist is None or hist.empty or "Close" not in hist:
        return dict(EMPTY_RESULT)

    close = hist["Close"].dropna()
    if len(close) < 2:
        return dict(EMPTY_RESULT)

    sma20, sma50, rsi, macd, macd_signal = _compute_indicators(close)

    dates = [d.strftime("%Y-%m-%d") for d in close.index]

    latest = {
        "close": _none_if_nan(close.iloc[-1]),
        "sma20": _none_if_nan(sma20.iloc[-1]),
        "sma50": _none_if_nan(sma50.iloc[-1]),
        "rsi": _none_if_nan(rsi.iloc[-1]),
        "macd": _none_if_nan(macd.iloc[-1]),
        "macd_signal": _none_if_nan(macd_signal.iloc[-1]),
    }

    return {
        "available": True,
        "dates": dates,
        "close": _series_to_list(close),
        "sma20": _series_to_list(sma20),
        "sma50": _series_to_list(sma50),
        "rsi": _series_to_list(rsi),
        "macd": _series_to_list(macd),
        "macd_signal": _series_to_list(macd_signal),
        "latest": latest,
    }


def get_history(ticker, period="6mo"):
    """
    Fetch ~6 months of daily closes for a ticker plus SMA20/SMA50, RSI(14),
    and MACD(12,26,9), for charting and the signal engine.
    Never raises - on any failure, returns an "unavailable" result so the UI
    can show a fallback instead of erroring.
    """
    cached = _get_cached(ticker)
    if cached is not None:
        return cached

    for attempt in range(2):
        try:
            result = _fetch_once(ticker, period)
            return _store(ticker, result)
        except Exception:
            if attempt == 0:
                time.sleep(0.3)
            continue

    return _store(ticker, dict(EMPTY_RESULT))
