# StockLens — Project Structure

**Status:** Finalized Day 2. This is the folder/file layout Day 3 onward will build into. It matches the skeleton already created in your local repo today.

---

## 1. Full Folder Structure

```
stock-Lens/
│
├── app.py                  # Main Flask application: routes, session handling, app entry point
├── schema.sql               # Database schema (users, watchlist tables) — run once to init stocklens.db
├── tickers.py                # Curated static list of ~50-100 tickers + company names (no API call needed to search)
├── stock_api.py              # Wraps Finnhub /quote and /stock/metric calls; includes caching + error handling
├── news_api.py                # Wraps Finnhub /company-news calls; includes caching + error handling
├── requirements.txt            # Exact pinned Python dependencies (Flask, Werkzeug, requests, etc.)
├── .gitignore                  # Excludes .env, __pycache__, *.db, venv folders from Git
├── .env.example                  # Documents required environment variable NAMES only (no real values)
├── README.md                      # Project overview, setup instructions, live demo link (filled in fully by Day 10)
│
├── templates/                       # Jinja2 HTML templates (rendered by Flask)
│   ├── base.html                      # Shared layout: navbar, page structure — all other templates extend this (built Day 8)
│   ├── signup.html                     # Signup form (Day 3)
│   ├── login.html                       # Login form (Day 3)
│   ├── dashboard.html                    # Main watchlist view (Day 4-5-7, evolves across days)
│   ├── stock_detail.html                  # Stock detail + news (Day 6)
│   └── compare.html                        # Comparison table (Day 7)
│
└── static/                                 # Static assets served directly (CSS, JS, images)
    ├── css/
    │   └── style.css                          # Small custom overrides on top of Bootstrap (Day 8)
    └── js/
        ├── search.js                           # Optional client-side filter for ticker search (Day 4)
        └── sort_table.js                        # Client-side column sorting for Compare view (Day 7)
```

---

## 2. What Each Major Folder/File Is Responsible For

| Path | Responsibility |
|---|---|
| `app.py` | The single Flask entry point: defines all 12 routes from API.md, initializes the database connection, manages sessions. Kept as one file for v1.0 since the app is small — no need for blueprints/packages at this scale. |
| `schema.sql` | Single source of truth for database structure, matching SCHEMA.md exactly. |
| `tickers.py` | A plain Python list/dict of curated tickers — acts as the "reference data" layer so search/add doesn't need a database table or an API call. |
| `stock_api.py` | All Finnhub quote/fundamentals logic lives here — isolated so Day 5 work doesn't touch routing code, and so error-handling/caching logic is written once and reused. |
| `news_api.py` | All Finnhub news logic lives here, same isolation reasoning as `stock_api.py`. |
| `templates/` | All user-facing HTML. `base.html` (added Day 8) is the shared shell every other page extends, to avoid repeating the navbar/layout code five times. |
| `static/css/` | Any custom CSS beyond what Bootstrap's CDN classes already provide — kept minimal by design. |
| `static/js/` | Small, dependency-free vanilla JS files for two specific interactive behaviors (search filter, table sort) — no JS framework needed for this scope. |
| `.env.example` | Lists the required environment variable names (e.g., `FINNHUB_API_KEY`, `FLASK_SECRET_KEY`) with placeholder values, so the project is reproducible without exposing real secrets in Git. |
| `.gitignore` | Prevents `.env` (real secrets), `__pycache__/`, `*.db` (local database file), and any virtual environment folder from ever being committed. |
| `requirements.txt` | Generated via `pip freeze` on Day 9 (or updated incrementally) so Render can install the exact same dependencies during deployment. |
| `README.md` | Human-facing project summary — filled in progressively, finalized Day 10 with screenshots and the live demo link. |

---

## 3. Where Future Code Will Live (Day-by-Day Mapping)

| Day | Adds/Modifies |
|---|---|
| Day 3 | `app.py` (auth routes), `schema.sql` (run to create DB), `templates/signup.html`, `templates/login.html` |
| Day 4 | `tickers.py`, `app.py` (watchlist add/remove routes), `templates/dashboard.html`, `static/js/search.js` |
| Day 5 | `stock_api.py`, `app.py` (dashboard route updated to enrich with live data) |
| Day 6 | `news_api.py`, `app.py` (`/stock/<ticker>` route), `templates/stock_detail.html` |
| Day 7 | `app.py` (target price + `/compare` routes), `templates/compare.html`, `static/js/sort_table.js` |
| Day 8 | `templates/base.html` (new), all templates refactored to extend it, `static/css/style.css` |
| Day 9 | `requirements.txt` (finalized), `.gitignore` (verified), deployment config on Render |
| Day 10 | `README.md` (finalized), final screenshots |

---

## 4. Why This Structure Was Chosen

- **Flat, single-file `app.py`** instead of a multi-package Flask project: appropriate for a 12-route, single-developer, 10-day app. Splitting into blueprints/packages would add structure overhead with no real benefit at this scale, and risks eating build time better spent on features.
- **Separate `stock_api.py` / `news_api.py`** instead of putting API calls directly in `app.py`: keeps external-service logic isolated, testable in isolation, and easy to hand off to a fresh AI conversation on the exact day it's needed (Day 5 / Day 6) without needing to read all of `app.py`.
- **`tickers.py` as code, not a database table:** it's fixed reference data curated once on Day 4, not user-generated — no need for the overhead of a DB table or migration.
- **`templates/` and `static/` as standard Flask convention folders:** Flask automatically looks for templates and static files in these exact folder names, so no extra configuration is needed.
- **No `venv/` in the repo:** virtual environments are local-machine-specific and belong in `.gitignore`, not committed — `requirements.txt` is what makes the environment reproducible elsewhere (including on Render).
