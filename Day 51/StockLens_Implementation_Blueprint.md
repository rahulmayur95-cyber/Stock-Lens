# StockLens — Implementation Blueprint (Days 2–10)

**Project:** StockLens — Stock Watchlist, Analysis & News Dashboard with In-App Price Alerts
**Builder profile:** Comfortable overall skill level; knows HTML + SQL; a little Python; first-time deployer.
**Daily time budget:** 3–4 hours/day.
**Source of truth:** This document + the StockLens PRD. Each day below is written so a *fresh* AI conversation can pick up exactly where the previous day left off — paste in that day's section (plus "Handoff Notes" from the prior day) to continue building without re-planning.

> **How to use this each day:** Start a new chat, paste in that day's full section, tell the assistant what you actually finished vs. didn't, and attach a screenshot of your current app state if you have one. Do not let the assistant redesign scope — this blueprint is locked.

---

## Day 2 — Design & Tech Stack Decisions

🎯 **Objective:** Turn the PRD into concrete technical decisions: tech stack, database schema, page/screen map, and API choices. No code yet — this is the blueprint for everything after.

📖 **What I'll learn:** How to translate product requirements into an architecture; how to choose beginner-friendly tools; how to design a simple relational schema.

🛠 **Features to build:** None yet (design only), but you will produce artifacts used every day after.

📝 **Step-by-step implementation plan:**
1. Confirm tech stack (recommended, matched to your skills): **Python + Flask** (backend + routing), **Jinja2 templates** (HTML you already know), **SQLite** (SQL you already know, zero setup, file-based), **Bootstrap via CDN** (fast styling without writing much CSS).
2. Choose the free stock data API (e.g., a free-tier market data API with a documented "quote" and "fundamentals" endpoint) and free news API. Register for API keys today so you're not blocked later.
3. Choose the deployment platform (free tier, beginner-friendly, supports Flask + SQLite persistence or an easy swap to a hosted DB later). Create the account today.
4. Sketch the page map: `Login`, `Signup`, `Dashboard/Watchlist`, `Stock Detail`, `Compare View`.
5. Design the SQL schema (see below) and write it down in a `schema.sql` file.
6. Draw (on paper or in a doc) a simple wireframe of the Dashboard page showing: search/add box, list of watchlist cards (ticker, price, % change, target price, alert badge), and a link to Compare View.

📂 **Files/folders to create:**
```
stocklens/
  app.py
  schema.sql
  templates/
  static/
  requirements.txt
  .env.example
```

🔗 **APIs/tools to integrate:** Free stock quote API (get API key), free news API (get API key), Flask, SQLite, Bootstrap CDN.

🧪 **Testing tasks:** Call each chosen API manually once (e.g., via browser or `curl`) with your API key to confirm you get valid JSON back before committing to it.

🐞 **Common issues:** API requires signup + email verification (do this first thing today, not last); free tiers often cap requests/day — note the limit.

✅ **End-of-day checklist:**
- [ ] Tech stack decided and written down
- [ ] Stock API key obtained and tested
- [ ] News API key obtained and tested
- [ ] Deployment platform account created
- [ ] SQL schema drafted (see below)
- [ ] Page map + rough wireframe done

📸 **Expected state / screenshots:** Screenshot of a successful test API response (JSON) for both stock and news APIs; photo/scan of your wireframe sketch.

➡️ **Handoff notes for Day 3:** Bring your finalized schema.sql, API keys (store safely, do not share in chat), and page map. Day 3 builds the project skeleton and database using these exact decisions.

**Suggested SQL Schema:**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE watchlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  target_price REAL,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Day 3 — Project Setup & Authentication

🎯 **Objective:** Stand up the Flask project skeleton, connect SQLite, and build working signup/login/logout.

📖 **What I'll learn:** Flask app structure, routing, password hashing, session management, SQL CRUD basics in Python.

🛠 **Features to build:** Signup, Login, Logout, protected route redirect.

📝 **Step-by-step implementation plan:**
1. Set up a virtual environment; `pip install flask werkzeug`.
2. Create `app.py` with Flask app init and a route to initialize the DB from `schema.sql`.
3. Build `/signup` (GET shows form, POST creates user with hashed password using `werkzeug.security.generate_password_hash`).
4. Build `/login` (POST verifies with `check_password_hash`, sets `session['user_id']`).
5. Build `/logout` (clears session).
6. Add a `login_required` decorator; apply it to a placeholder `/dashboard` route.
7. Build simple `signup.html` and `login.html` templates using Bootstrap form components.

📂 **Files/folders:**
```
app.py
schema.sql
templates/signup.html
templates/login.html
templates/dashboard.html (placeholder)
requirements.txt
```

🔗 **Integrations:** Flask, Flask sessions, Werkzeug security, SQLite3 (Python built-in).

🧪 **Testing tasks:** Sign up a test user; confirm password isn't stored in plaintext (inspect DB); log out and confirm `/dashboard` redirects to login; try signing up with a duplicate username and confirm friendly error.

🐞 **Common issues:** Forgetting `secret_key` for sessions (app throws error); SQLite file path issues if run from wrong directory; passwords not hashed correctly.

✅ **End-of-day checklist:**
- [ ] Can sign up a new user
- [ ] Can log in and reach a placeholder dashboard
- [ ] Can log out
- [ ] Unauthenticated access to /dashboard redirects to /login
- [ ] Passwords confirmed hashed in DB

📸 **Expected state:** Screenshot of working signup form, login form, and placeholder dashboard after login.

➡️ **Handoff notes for Day 4:** Auth is working. Day 4 replaces the placeholder dashboard with the real watchlist add/remove feature, using `session['user_id']` to scope data per user.

---

## Day 4 — Watchlist Core (Add/Remove Stocks)

🎯 **Objective:** Let logged-in users search a curated ticker list and add/remove stocks from their personal watchlist, stored in SQL.

📖 **What I'll learn:** Many-relationship data modeling per user, form handling, basic search/filter logic.

🛠 **Features to build:** Curated ticker list, search/add box, watchlist display (tickers only, no live data yet), remove button.

📝 **Step-by-step implementation plan:**
1. Create a static curated list of 50–100 tickers (Python list/dict of `{ticker, company_name}`) in a `tickers.py` file — this avoids an extra API call just to search.
2. Build `/dashboard` (GET): query `watchlist` table for `session['user_id']`, render each as a card/row with ticker + company name + remove button.
3. Build a search box (client-side filter over the static ticker list using simple JS, or server-side `/search?q=`) that returns matching tickers to add.
4. Build `/watchlist/add` (POST): insert `(user_id, ticker)` into `watchlist` table if not already present.
5. Build `/watchlist/remove/<id>` (POST): delete row, scoped to `user_id` (never trust the client — always check ownership).
6. Style the dashboard with Bootstrap cards/list group.

📂 **Files/folders:**
```
tickers.py
templates/dashboard.html (updated)
static/js/search.js (optional client-side filter)
```

🔗 **Integrations:** None new — pure Flask + SQLite + your curated list.

🧪 **Testing tasks:** Add 3–4 stocks, refresh page, confirm they persist; remove one, confirm it's gone; try adding a duplicate, confirm no duplicate row; log in as a second test user and confirm their watchlist is separate.

🐞 **Common issues:** Forgetting to scope queries by `user_id` (data leaks between users); duplicate tickers if you don't check existence before insert.

✅ **End-of-day checklist:**
- [ ] Curated ticker list created
- [ ] Search/add box working
- [ ] Watchlist persists per user after refresh
- [ ] Remove button works and is scoped to the owner
- [ ] Verified two different users have separate watchlists

📸 **Expected state:** Screenshot of dashboard with 3+ stocks added, and after removing one.

➡️ **Handoff notes for Day 5:** Watchlist add/remove is fully working with tickers only (no price data yet). Day 5 connects the stock data API to show real price/%change/P/E next to each watchlisted ticker.

---

## Day 5 — Live Stock Data Integration

🎯 **Objective:** Fetch and display real price, % change, and a basic fundamental (e.g., P/E) for each watchlisted stock from the chosen free API.

📖 **What I'll learn:** Calling external APIs from Python, handling API errors/timeouts gracefully, basic response caching.

🛠 **Features to build:** Live metrics on the dashboard for every watchlisted stock.

📝 **Step-by-step implementation plan:**
1. Write a helper function `get_quote(ticker)` in a new `stock_api.py` that calls your chosen stock API and returns `{price, percent_change, pe_ratio}`.
2. In `/dashboard`, after loading the user's watchlist tickers, call `get_quote()` for each and pass the combined data to the template.
3. Wrap each API call in try/except; if it fails, show "Data unavailable" for that stock instead of crashing the page.
4. Add simple in-memory or file-based caching (e.g., a dict keyed by ticker with a timestamp) so repeated dashboard reloads within a short window don't re-hit the API for every stock — respects free-tier rate limits.
5. Update `dashboard.html` to show price, % change (color-coded green/red), and P/E per stock card.

📂 **Files/folders:**
```
stock_api.py
app.py (updated dashboard route)
templates/dashboard.html (updated)
```

🔗 **Integrations:** Your chosen free stock quote API (from Day 2).

🧪 **Testing tasks:** Confirm real prices show for 5+ different tickers; temporarily break the API key to confirm the "data unavailable" fallback works instead of a crash; check that reloading the page doesn't immediately exceed your API's per-minute rate limit.

🐞 **Common issues:** Rate limiting when watchlist has many stocks (loop of API calls); inconsistent JSON field names across API responses; API key exposed in code (move to `.env` / environment variable, never commit it).

✅ **End-of-day checklist:**
- [ ] Real price + % change shown per watchlisted stock
- [ ] P/E (or chosen fundamental) shown per stock
- [ ] Graceful fallback when API call fails
- [ ] Basic caching in place
- [ ] API key stored as environment variable, not hardcoded

📸 **Expected state:** Screenshot of dashboard showing real live prices/%change for your watchlisted stocks.

➡️ **Handoff notes for Day 6:** Live metrics are working. Day 6 adds the news feed per stock using the same error-handling and caching patterns established today.

---

## Day 6 — News Feed Integration

🎯 **Objective:** Show 3–5 recent news headlines per stock, linking to the source.

📖 **What I'll learn:** Working with a second external API, building a "detail page" pattern, passing dynamic URL parameters in Flask.

🛠 **Features to build:** Stock Detail page with news headlines; link from dashboard cards to detail page.

📝 **Step-by-step implementation plan:**
1. Write `get_news(ticker_or_company_name)` in a new `news_api.py` that calls your chosen free news API and returns a list of `{title, source, url, published_at}` (top 3–5 results).
2. Build `/stock/<ticker>` route: fetch the quote (reuse Day 5 helper) and news list, render `stock_detail.html`.
3. On `dashboard.html`, make each stock card/name a link to `/stock/<ticker>`.
4. Build `stock_detail.html`: show ticker, company name, price/%change/P/E, then a list of headlines (title as link, source + date as subtext).
5. Apply the same try/except + fallback pattern as Day 5 if the news API fails or returns nothing.

📂 **Files/folders:**
```
news_api.py
templates/stock_detail.html
app.py (new /stock/<ticker> route)
```

🔗 **Integrations:** Your chosen free news API (from Day 2).

🧪 **Testing tasks:** Visit detail pages for several different watchlisted stocks; confirm headlines load and links open the correct articles; test a ticker with little/no news coverage to confirm the empty-state message shows instead of breaking.

🐞 **Common issues:** News API search matching on ticker symbol vs. company name (some APIs need the full company name for relevant results); duplicate headlines from multiple sources.

✅ **End-of-day checklist:**
- [ ] Stock Detail page live at `/stock/<ticker>`
- [ ] 3–5 headlines shown with working links
- [ ] Dashboard links to detail pages
- [ ] Empty/failed state handled gracefully

📸 **Expected state:** Screenshot of a Stock Detail page showing metrics + news headlines for a real ticker.

➡️ **Handoff notes for Day 7:** Metrics + news are complete. Day 7 adds the price-target alert feature and the comparison table — the two remaining core features before deployment.

---

## Day 7 — Price Alerts & Comparison View

🎯 **Objective:** Let users set a target price per stock with a visual in-app alert badge, and build the sortable comparison table.

📖 **What I'll learn:** Conditional UI rendering, basic client-side table sorting, updating existing SQL rows.

🛠 **Features to build:** Set/edit target price; alert badge logic; `/compare` sortable table page.

📝 **Step-by-step implementation plan:**
1. Add an inline form on each dashboard card: input for target price + "Save" button, posting to `/watchlist/target/<id>` which updates the `target_price` column for that row (scoped to the logged-in user).
2. In the dashboard route, after fetching each stock's live price, compare it to `target_price` (if set) and compute an `alert = True/False` flag to pass to the template.
3. In `dashboard.html`, show a 🔔 badge or highlighted card border when `alert` is True.
4. Build `/compare` route: fetch all watchlisted stocks + live metrics + target price + alert status, render as a table.
5. Add simple client-side sorting (a small vanilla JS snippet that re-orders table rows when a header is clicked) — no extra library needed.
6. Link `/compare` from the dashboard nav.

📂 **Files/folders:**
```
templates/compare.html
static/js/sort_table.js
app.py (target price route + /compare route)
```

🔗 **Integrations:** None new.

🧪 **Testing tasks:** Set a target price below current price, confirm alert badge appears; set one above current price, confirm no badge; edit an existing target; confirm compare table shows correct data and sorts correctly by each column.

🐞 **Common issues:** Off-by-logic on alert condition (decide clearly: "alert if current price ≥ target" or "≤" — document your choice); table sorting breaking on non-numeric text if `%` or `$` symbols are in the cell (sort on raw numeric values, format for display separately).

✅ **End-of-day checklist:**
- [ ] Target price can be set/edited per stock
- [ ] Alert badge correctly appears/disappears based on price vs. target
- [ ] `/compare` page shows all watchlisted stocks in a table
- [ ] Table columns are sortable

📸 **Expected state:** Screenshot of dashboard with at least one alert badge triggered, and the Compare table view.

➡️ **Handoff notes for Day 8:** All core v1.0 features are functionally complete (auth, watchlist, metrics, news, alerts, compare). Day 8 is dedicated to styling/UX polish and full manual testing — no new features.

---

## Day 8 — UI Polish & End-to-End Testing

🎯 **Objective:** Make the app look and feel like a finished product, and systematically test every feature before deployment.

📖 **What I'll learn:** UX polish techniques with Bootstrap, structured manual QA/testing practices, responsive design basics.

🛠 **Features to build:** No new features — polish and fixes only. This protects Day 9–10 from scope creep.

📝 **Step-by-step implementation plan:**
1. Add a consistent navbar (logo/name, Dashboard, Compare, Logout) across all pages using a shared `base.html` template with Jinja `{% block %}` inheritance.
2. Improve visual hierarchy: consistent spacing, card shadows, color-coded green/red for % change, clear empty states ("Your watchlist is empty — add a stock below").
3. Test responsiveness at mobile width (browser dev tools device toolbar) and fix any broken layouts using Bootstrap's responsive grid classes.
4. Write a test checklist covering every user story from the PRD and manually walk through each one as a fresh user (new signup) end-to-end.
5. Fix any bugs found; do not add new features even if tempted.
6. Add basic form validation messages (e.g., empty password, invalid target price).

📂 **Files/folders:**
```
templates/base.html (new shared layout)
templates/*.html (updated to extend base.html)
static/css/style.css (small custom overrides)
```

🔗 **Integrations:** None new.

🧪 **Testing tasks (full checklist):**
- [ ] Signup with new account works
- [ ] Login/logout works
- [ ] Add/remove watchlist stocks works
- [ ] Live metrics display correctly
- [ ] News feed displays correctly
- [ ] Target price + alert badge works
- [ ] Compare table + sorting works
- [ ] All pages usable at mobile width
- [ ] No console errors in browser dev tools

🐞 **Common issues:** Template inheritance breaking existing pages (test each page after refactor); mobile layout overflow on the comparison table (wrap it in a scrollable container).

✅ **End-of-day checklist:**
- [ ] Shared navbar/layout applied to all pages
- [ ] Full manual test checklist passed
- [ ] Mobile responsiveness confirmed
- [ ] All known bugs fixed

📸 **Expected state:** Screenshots of the polished Dashboard, Stock Detail, and Compare pages, plus one mobile-width screenshot.

➡️ **Handoff notes for Day 9:** App is feature-complete, polished, and tested locally. Day 9 is dedicated entirely to deployment — this is your first deployment ever, so follow every step carefully and confirm each one before moving on.

---

## Day 9 — Deployment (First-Time Deploy)

🎯 **Objective:** Deploy StockLens to a live public URL for the first time.

📖 **What I'll learn:** Preparing a Python app for production, environment variables in production, basic deployment troubleshooting.

🛠 **Features to build:** None — deployment only.

📝 **Step-by-step implementation plan:**
1. Add `requirements.txt` (freeze exact dependencies: `pip freeze > requirements.txt`).
2. Add a `Procfile` or equivalent start command file if your chosen platform needs one (platform-specific — confirm during Day 2 platform research).
3. Move all secrets (API keys, Flask `secret_key`) into environment variables; confirm nothing sensitive is hardcoded or committed to any repo.
4. Push code to a GitHub repository (guided step-by-step if this is your first time using git/GitHub).
5. Connect the repository to your chosen hosting platform and configure the environment variables there.
6. Deploy and watch the build logs for errors.
7. Test the live URL exactly like Day 8's checklist, but on the deployed version.
8. Fix any deployment-specific issues (commonly: missing dependency, wrong start command, SQLite file not persisting — see Debugging tips).

📂 **Files/folders:**
```
requirements.txt
Procfile (or platform equivalent)
.gitignore (exclude .env, __pycache__, instance/*.db if applicable)
.env.example (documents required variables without real values)
```

🔗 **Integrations:** GitHub, your chosen free hosting platform.

🧪 **Testing tasks:** Full manual walkthrough of the live URL as a brand-new user (signup → add stocks → view metrics/news → set alert → compare) exactly as in Day 8, but on production.

🐞 **Common issues & debugging tips:**
- **App crashes on load:** check platform build/runtime logs first — usually a missing package in `requirements.txt`.
- **"Internal Server Error" with no detail:** temporarily enable debug logging on the platform (not `debug=True` in production) to see the real traceback.
- **SQLite database resets on every deploy:** many free hosts have ephemeral filesystems — if this happens, note it as a known limitation for now (acceptable for a capstone demo) or migrate to the platform's free persistent storage/DB add-on if time allows.
- **Environment variables not picked up:** confirm they're set in the platform's dashboard, not just your local `.env` file.
- **CSS/static files not loading:** check static file path configuration for the platform.

✅ **End-of-day checklist:**
- [ ] Code pushed to GitHub
- [ ] App deployed and reachable at a public URL
- [ ] Environment variables configured on the platform
- [ ] Full user journey tested successfully on the live URL
- [ ] Live URL saved/documented for Day 10

📸 **Expected state:** Screenshot of the live deployed app in a browser showing the public URL in the address bar, with a working dashboard.

➡️ **Handoff notes for Day 10:** App is live. Day 10 is final QA, README/documentation, and preparing your demo/presentation — no new features, no risky changes to the deployed app.

---

## Day 10 — Final QA, Documentation & Launch

🎯 **Objective:** Lock in a stable, polished v1.0, document it, and prepare to present it.

📖 **What I'll learn:** Writing a project README, final release discipline, presenting technical work clearly.

🛠 **Features to build:** None — this day is a freeze. Only critical bug fixes allowed.

📝 **Step-by-step implementation plan:**
1. Run the full end-to-end test checklist (from Day 8/9) one final time on the live URL.
2. Fix only critical/blocking bugs found; resist adding anything new.
3. Write a `README.md` for the GitHub repo: project description, features, screenshots, tech stack, setup instructions, live demo link.
4. Take final polished screenshots of every page (desktop + mobile) for the README and for your pitch deck.
5. Do a final review of the Pitch Deck (generated Day 1) against the actual finished product — update any details that changed during the build (e.g., final tech stack, final feature list).
6. Do a dry run of a 3–5 minute demo: sign up live, add stocks, show metrics/news, trigger an alert, show compare view.
7. Tag/document this as your v1.0 release (e.g., a GitHub release tag or simply a note in the README).

📂 **Files/folders:**
```
README.md
/screenshots (final images used in README/deck)
```

🔗 **Integrations:** None new.

🧪 **Testing tasks:** Final full regression test of every PRD user story on the live deployed app.

🐞 **Common issues:** Last-minute "just one more feature" urge — refer back to the PRD's Out of Scope list and resist; broken links in README to screenshots (use relative paths correctly).

✅ **End-of-day checklist:**
- [ ] Full regression test passed on live URL
- [ ] README completed with live link and screenshots
- [ ] Pitch deck reconciled with final product
- [ ] Demo walkthrough rehearsed
- [ ] v1.0 tagged/documented as complete

📸 **Expected state:** Final screenshots of every page, live and working, ready to share.

➡️ **Handoff notes:** Capstone complete. Maintenance phase (post-Day 10, optional) would pick up items from the PRD's Future Scope section — real-time data, notifications, full market search, portfolio tracking.

---

## Locked Scope Reminder (applies to every day)

**Building:** Auth (basic) · Watchlist add/remove · Live price/%change/P/E · News headlines · Target-price in-app alerts · Sortable compare table · Public deployment.

**Not building in v1.0:** Real-time streaming data · full market coverage · email/push notifications · password reset/OAuth · native mobile app · portfolio P&L tracking.

If a future-day conversation suggests adding something from the "not building" list, decline and note it under Future Scope instead.
