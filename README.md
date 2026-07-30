# 📈 StockLens

A free, simple stock watchlist and analysis dashboard — track live prices, view recent news, and get notified when your price targets are hit.

**🔗 Live app:** https://stock-lens-i6yn.onrender.com
*(Free-tier hosting — the app may take 30–60 seconds to wake up if it's been idle. Thanks for your patience!)*

Built as a 10-day capstone project for the **AB Talks 60-Day Claude AI Challenge**, guided end-to-end by Claude AI.

---

## ✨ Features

- 🔐 **Secure accounts** — signup/login with hashed passwords, CSRF protection, and brute-force login protection
- 📋 **Personal watchlist** — search and add stocks from a curated list of 60 popular companies
- 📈 **Live market data** — current price, % change, and P/E ratio, powered by [Finnhub](https://finnhub.io)
- 📰 **Recent news** — the latest headlines for any stock you're tracking
- 🔔 **Price target alerts** — set a target price and get a visual badge when it's reached
- 📊 **Compare view** — sortable side-by-side table of your entire watchlist
- 📱 **Responsive design** — works cleanly on desktop and mobile

## 🖼️ Screenshots

> _Add your own screenshots here! Suggested: Dashboard, Stock Detail (with news), Compare view, and mobile view._

| Dashboard | Stock Detail | Compare |
|---|---|---|
| _screenshot here_ | _screenshot here_ | _screenshot here_ |

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, Jinja2, Bootstrap 5 |
| Database | SQLite |
| Auth | Flask sessions + Werkzeug password hashing |
| Market data & news | [Finnhub API](https://finnhub.io) (free tier) |
| Hosting | [Render](https://render.com) (free tier) |
| Production server | Gunicorn |

No paid services or third-party AI APIs are used anywhere in the running application.

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.10+
- A free [Finnhub API key](https://finnhub.io/register)

### Setup

```bash
# Clone the repository
git clone https://github.com/rahulmayur95-cyber/Stock-Lens.git
cd Stock-Lens

# Create and activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Then edit .env and add your real FINNHUB_API_KEY and a random FLASK_SECRET_KEY

# Run the app
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

### Environment Variables

| Variable | Description |
|---|---|
| `FINNHUB_API_KEY` | Free API key from [finnhub.io](https://finnhub.io/register) |
| `FLASK_SECRET_KEY` | Any long, random string — used to sign session cookies |

## 📂 Project Structure

```
stock-Lens/
├── app.py                  # Flask app: routes, auth, security
├── schema.sql               # Database schema
├── tickers.py                 # Curated stock list
├── stock_api.py                 # Finnhub price/fundamentals integration
├── news_api.py                    # Finnhub news integration
├── templates/                       # Jinja2 HTML templates
├── static/                            # CSS, JS, favicon
├── requirements.txt
├── render.yaml                          # Render deployment config
└── .env.example                           # Environment variable template
```

## 🔒 Security

- Passwords hashed with Werkzeug (never stored in plaintext)
- CSRF tokens required on all state-changing requests
- Login rate limiting (5 attempts per 5 minutes)
- Secure, HTTP-only, same-site session cookies
- Parameterized SQL queries throughout (no SQL injection risk)

## ⚠️ Known Limitations

- Free-tier hosting means the app "sleeps" after inactivity (first load may be slow)
- SQLite database resets on redeploy (Render free tier has an ephemeral filesystem) — acceptable for a demo/portfolio project, not intended for production data persistence at scale
- Curated list of ~60 stocks rather than full market coverage (by design, to stay within free API rate limits)
- No email/password-reset flow (basic auth only, by design for v1.0)

## 🗺️ Roadmap / Future Ideas

- Real-time price streaming
- Email/push notifications for alerts
- Full market search
- Portfolio profit/loss tracking

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with [Claude AI](https://claude.ai) as part of the **AB Talks 60-Day Claude AI Challenge**. Market and news data provided by [Finnhub](https://finnhub.io). Hosted on [Render](https://render.com).
