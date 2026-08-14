"""
Rule-based Buy/Sell/Hold signal for StockLens.

Combines simple technical indicators (RSI, price vs 50-day moving average,
MACD vs its signal line) with keyword-based sentiment scanning of recent
news headlines (VADER - lightweight, no network calls, no paid API).

IMPORTANT: This is a simple heuristic, not investment advice or a prediction
of future performance. See DISCLAIMER below - it's always shown with the signal.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DISCLAIMER = (
    "This signal is generated automatically from basic technical indicators and "
    "news headline sentiment. It is not financial advice, not a prediction of "
    "future performance, and does not account for your personal financial situation. "
    "Always do your own research or consult a licensed financial advisor before investing."
)

_analyzer = SentimentIntensityAnalyzer()


def _news_sentiment(news):
    """Average VADER compound sentiment across headline titles. Returns (score, avg) where
    score is -1/0/+1 and avg is the raw average compound value (for display), or (0, None)
    if there's no news to score."""
    if not news:
        return 0, None

    compounds = [_analyzer.polarity_scores(item["title"])["compound"] for item in news]
    avg = sum(compounds) / len(compounds)

    if avg > 0.2:
        return 1, avg
    if avg < -0.2:
        return -1, avg
    return 0, avg


def build_signal(latest_indicators, news):
    """
    latest_indicators: dict with keys close, sma50, rsi, macd, macd_signal (values or None)
    news: list of dicts with a "title" key (as returned by news_api.get_news)

    Returns: {"verdict": "BUY"|"HOLD"|"SELL", "score": int, "factors_used": int,
              "reasons": [str, ...], "disclaimer": str}
    """
    reasons = []
    score = 0
    factors_used = 0

    rsi = latest_indicators.get("rsi")
    if rsi is not None:
        factors_used += 1
        if rsi < 30:
            score += 1
            reasons.append(f"RSI is {rsi:.1f} — in oversold territory, historically a mild bullish signal.")
        elif rsi > 70:
            score -= 1
            reasons.append(f"RSI is {rsi:.1f} — in overbought territory, historically a mild bearish signal.")
        else:
            reasons.append(f"RSI is {rsi:.1f} — a neutral, non-extreme reading.")

    close = latest_indicators.get("close")
    sma50 = latest_indicators.get("sma50")
    if close is not None and sma50 is not None:
        factors_used += 1
        if close > sma50:
            score += 1
            reasons.append("Price is trading above its 50-day moving average (short/medium-term uptrend).")
        else:
            score -= 1
            reasons.append("Price is trading below its 50-day moving average (short/medium-term downtrend).")

    macd = latest_indicators.get("macd")
    macd_signal = latest_indicators.get("macd_signal")
    if macd is not None and macd_signal is not None:
        factors_used += 1
        if macd > macd_signal:
            score += 1
            reasons.append("MACD is above its signal line (positive momentum).")
        else:
            score -= 1
            reasons.append("MACD is below its signal line (negative momentum).")

    news_score, avg_sentiment = _news_sentiment(news)
    if news:
        factors_used += 1
        score += news_score
        if news_score > 0:
            reasons.append("Recent news headlines lean positive in tone.")
        elif news_score < 0:
            reasons.append("Recent news headlines lean negative in tone.")
        else:
            reasons.append("Recent news headlines are mixed or neutral in tone.")
    else:
        reasons.append("No recent news available to factor into sentiment.")

    if factors_used == 0:
        return {
            "verdict": "HOLD",
            "score": 0,
            "factors_used": 0,
            "reasons": ["Not enough price history or news data available to generate a signal."],
            "disclaimer": DISCLAIMER,
        }

    if score >= 2:
        verdict = "BUY"
    elif score <= -2:
        verdict = "SELL"
    else:
        verdict = "HOLD"

    return {
        "verdict": verdict,
        "score": score,
        "factors_used": factors_used,
        "reasons": reasons,
        "disclaimer": DISCLAIMER,
    }
