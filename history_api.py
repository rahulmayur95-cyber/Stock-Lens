"""
Historical price data + technical analysis for StockLens charts and the
Buy/Sell/Hold signal engine.

Uses yfinance for ALL tickers (US and Indian): Finnhub's free tier no longer
includes historical candle data for stocks, so yfinance (free, no API key)
is the single source for chart history.

Provides:
- OHLCV candles (for candlestick/OHLC/line charts + volume bars)
- SMA20/SMA50, RSI(14), MACD(12,26,9) - existing indicators
- Bollinger Bands (20, 2 std dev)
- Basic support/resistance levels (pivot high/low detection)
- Basic candlestick pattern flags (Doji, Hammer, Bullish/Bearish Engulfing)
"""

import sys
import time
import pandas as pd
import yfinance as yf
from yf_session import get_session
from yf_isolation import run_isolated

_cache = {}
CACHE_TTL_SECONDS = 900  # history changes slowly intraday - cache 15 minutes
NEGATIVE_CACHE_TTL_SECONDS = 60

# How much history to pull for each timeframe - longer lookback for coarser
# timeframes so there's still a meaningful number of candles to chart.
PERIOD_FOR_INTERVAL = {"1d": "6mo", "1wk": "2y", "1mo": "5y"}
VALID_INTERVALS = set(PERIOD_FOR_INTERVAL.keys())

EMPTY_RESULT = {
    "available": False,
    "interval": "1d",
    "dates": [],
    "timestamps_ms": [],
    "open": [],
    "high": [],
    "low": [],
    "close": [],
    "volume": [],
    "sma20": [],
    "sma50": [],
    "rsi": [],
    "macd": [],
    "macd_signal": [],
    "bb_upper": [],
    "bb_lower": [],
    "support_levels": [],
    "resistance_levels": [],
    "patterns": [],
    "latest": {"close": None, "sma20": None, "sma50": None, "rsi": None, "macd": None, "macd_signal": None},
}


def _cache_key(ticker, interval):
    return f"{ticker}|{interval}"


def _get_cached(ticker, interval):
    entry = _cache.get(_cache_key(ticker, interval))
    if not entry:
        return None
    ttl = CACHE_TTL_SECONDS if entry["data"]["available"] else NEGATIVE_CACHE_TTL_SECONDS
    if (time.time() - entry["timestamp"]) < ttl:
        return entry["data"]
    return None


def _store(ticker, interval, data):
    _cache[_cache_key(ticker, interval)] = {"data": data, "timestamp": time.time()}
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
    rsi = rsi.where(avg_loss != 0, 100.0)  # all gains, no losses -> RSI 100

    # Bollinger Bands: 20-period SMA +/- 2 standard deviations
    std20 = close.rolling(window=20).std()
    bb_upper = sma20 + (2 * std20)
    bb_lower = sma20 - (2 * std20)

    return sma20, sma50, rsi, macd, macd_signal, bb_upper, bb_lower


def _find_pivots(series: pd.Series, window: int, is_high: bool):
    """A point is a pivot if it's the max/min within `window` candles on each side.
    Returns the index positions of pivot points."""
    pivots = []
    values = series.values
    n = len(values)
    for i in range(window, n - window):
        segment = values[i - window: i + window + 1]
        if is_high and values[i] == segment.max():
            pivots.append(i)
        elif not is_high and values[i] == segment.min():
            pivots.append(i)
    return pivots


def _support_resistance_levels(high: pd.Series, low: pd.Series, max_levels=3):
    """Basic pivot-point support/resistance: find local swing highs/lows over the
    whole window, then return the most recent distinct levels. This is a simple
    heuristic, not a guarantee of where price will actually reverse."""
    window = 5
    if len(high) < (2 * window + 1):
        return [], []

    resistance_idx = _find_pivots(high, window, is_high=True)
    support_idx = _find_pivots(low, window, is_high=False)

    resistance_levels = [round(float(high.iloc[i]), 2) for i in resistance_idx[-max_levels:]]
    support_levels = [round(float(low.iloc[i]), 2) for i in support_idx[-max_levels:]]

    return support_levels, resistance_levels


def _detect_patterns(open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series, dates, lookback=30):
    """Flag simple, well-defined candlestick patterns on the most recent `lookback`
    candles: Doji, Hammer, Bullish Engulfing, Bearish Engulfing.
    These are shape-based rules only (no trend/context checks), so treat them as
    a starting point for further analysis, not standalone signals."""
    patterns = []
    n = len(close)
    start = max(1, n - lookback)  # need i-1 for engulfing, so start at least at 1

    for i in range(start, n):
        o, h, l, c = open_.iloc[i], high.iloc[i], low.iloc[i], close.iloc[i]
        body = abs(c - o)
        candle_range = h - l
        if candle_range <= 0:
            continue

        # Doji: body is a tiny fraction of the whole candle's range
        if body <= 0.1 * candle_range:
            patterns.append({"date": dates[i], "pattern": "Doji"})
            continue

        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        # Hammer: small body near the top, long lower wick, short/no upper wick
        if lower_wick >= 2 * body and upper_wick <= 0.3 * body and body > 0:
            patterns.append({"date": dates[i], "pattern": "Hammer"})
            continue

        # Engulfing patterns need the previous candle
        prev_o, prev_c = open_.iloc[i - 1], close.iloc[i - 1]
        prev_bullish = prev_c > prev_o
        curr_bullish = c > o

        if not prev_bullish and curr_bullish and o < prev_c and c > prev_o:
            patterns.append({"date": dates[i], "pattern": "Bullish Engulfing"})
        elif prev_bullish and not curr_bullish and o > prev_c and c < prev_o:
            patterns.append({"date": dates[i], "pattern": "Bearish Engulfing"})

    return patterns


def _fetch_once(ticker, interval):
    period = PERIOD_FOR_INTERVAL[interval]
    tk = yf.Ticker(ticker, session=get_session())
    hist = tk.history(period=period, interval=interval)

    if hist is None or hist.empty or "Close" not in hist:
        return dict(EMPTY_RESULT, interval=interval)

    hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
    if len(hist) < 2:
        return dict(EMPTY_RESULT, interval=interval)

    open_, high, low, close = hist["Open"], hist["High"], hist["Low"], hist["Close"]
    volume = hist["Volume"] if "Volume" in hist else pd.Series([0] * len(hist), index=hist.index)

    sma20, sma50, rsi, macd, macd_signal, bb_upper, bb_lower = _compute_indicators(close)

    dates = [d.strftime("%Y-%m-%d") for d in close.index]
    timestamps_ms = [int(d.timestamp() * 1000) for d in close.index]

    support_levels, resistance_levels = _support_resistance_levels(high, low)
    patterns = _detect_patterns(open_, high, low, close, dates)

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
        "interval": interval,
        "dates": dates,
        "timestamps_ms": timestamps_ms,
        "open": _series_to_list(open_),
        "high": _series_to_list(high),
        "low": _series_to_list(low),
        "close": _series_to_list(close),
        "volume": [int(v) if pd.notna(v) else 0 for v in volume],
        "sma20": _series_to_list(sma20),
        "sma50": _series_to_list(sma50),
        "rsi": _series_to_list(rsi),
        "macd": _series_to_list(macd),
        "macd_signal": _series_to_list(macd_signal),
        "bb_upper": _series_to_list(bb_upper),
        "bb_lower": _series_to_list(bb_lower),
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "patterns": patterns,
        "latest": latest,
    }


def get_history(ticker, interval="1d"):
    """
    Fetch OHLCV history for a ticker plus SMA20/SMA50, RSI(14), MACD(12,26,9),
    Bollinger Bands, support/resistance levels, and basic candlestick pattern
    flags, for charting and the signal engine.
    interval: "1d" (daily, ~6mo), "1wk" (weekly, ~2y), or "1mo" (monthly, ~5y).
    Never raises - on any failure, returns an "unavailable" result so the UI
    can show a fallback instead of erroring.
    """
    if interval not in VALID_INTERVALS:
        interval = "1d"

    cached = _get_cached(ticker, interval)
    if cached is not None:
        return cached

    for attempt in range(2):
        result = run_isolated(_fetch_once, ticker, interval, timeout=25)
        if result is not None:
            return _store(ticker, interval, result)
        if attempt == 0:
            print(f"[history_api] get_history({ticker}, {interval}) attempt {attempt} failed, retrying", file=sys.stderr, flush=True)
            time.sleep(0.3)

    return _store(ticker, interval, dict(EMPTY_RESULT, interval=interval))
