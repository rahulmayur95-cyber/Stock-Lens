"""
Curated list of popular stock tickers for StockLens v1.0.
This is a fixed reference list (not a database table) since it's static
reference data, not user-generated content. Used for search/add on the
dashboard. See ARCHITECTURE.md and SCHEMA.md for rationale.
"""

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


def search_tickers(query: str):
    """Return tickers matching a query by ticker symbol or company name (case-insensitive)."""
    if not query:
        return TICKERS
    q = query.strip().lower()
    return [t for t in TICKERS if q in t["ticker"].lower() or q in t["name"].lower()]


def is_valid_ticker(ticker: str) -> bool:
    """Check whether a ticker exists in the curated list."""
    return any(t["ticker"] == ticker for t in TICKERS)


def get_company_name(ticker: str) -> str:
    """Look up the company name for a given ticker; returns the ticker itself if not found."""
    for t in TICKERS:
        if t["ticker"] == ticker:
            return t["name"]
    return ticker
