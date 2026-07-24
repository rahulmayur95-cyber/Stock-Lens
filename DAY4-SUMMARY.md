# StockLens — Day 4 Summary: Core Feature Implementation

**Date:** Day 4 of 10 — AB Talks 60-Day Claude AI Challenge Capstone

---

## ✅ What Was Completed Today

### Milestone 1: Real Authentication (completing what Day 3 deferred)
- Built `templates/signup.html` and `templates/login.html` (Bootstrap forms)
- Rewrote `app.py` with full signup/login/logout logic: password hashing (Werkzeug), duplicate-username checks, minimum password length, session-based login state
- Added a reusable `login_required` decorator applied to all protected routes

### Milestone 2: Curated Ticker List
- Built `tickers.py` with 60 popular tickers (ticker + company name), plus helper functions: `search_tickers()`, `is_valid_ticker()`, `get_company_name()`

### Milestone 3: Watchlist Core
- Built `templates/dashboard.html`: search box, watchlist cards, target price form, view/remove buttons, empty-state message
- Built `static/js/search.js`: debounced live search calling `/search`, rendering "Add" buttons dynamically
- Added routes to `app.py`: `/dashboard`, `/search`, `/watchlist/add`, `/watchlist/remove/<id>`, `/watchlist/target/<id>`
- All watchlist queries scoped to `session['user_id']` — verified no cross-user data leakage possible (ownership checked in every UPDATE/DELETE)

---

## 🐞 Major Issue Found & Fixed: Empty `schema.sql`

**Root cause of ~90 minutes of debugging today:** `schema.sql` was created as an empty skeleton file on Day 2 and never actually filled in with content. This caused `sqlite3.OperationalError: no such table: users` intermittently — because `init_db()` only ran the schema *if the database file didn't already exist yet*, and a stray empty `stocklens.db` from an earlier failed run masked the real problem.

**Two-part permanent fix applied:**
1. `schema.sql` now contains the real `CREATE TABLE` statements (users, watchlist) — verified present and correct.
2. `init_db()` in `app.py` was changed to **always** run `schema.sql` on startup (safe, since it uses `CREATE TABLE IF NOT EXISTS` and never wipes existing data), instead of only running it conditionally. This makes the app self-healing against this exact class of bug in the future.

**Secondary issue also fixed:** Flask's debug auto-reloader was restarting the server mid-database-write in some cases, contributing to the confusing intermittent symptoms. Fixed by setting `app.run(debug=True, use_reloader=False)`.

**Lesson for future days:** always verify skeleton files created in early days (Day 2-3) actually contain real content before relying on them functionally, not just checking that they exist.

---

## ✅ Verification Performed

- [x] Signup creates a new user with a hashed password
- [x] Login authenticates correctly and starts a session
- [x] Logout clears the session
- [x] `/dashboard` redirects to `/login` when not authenticated
- [x] Search box returns live matching results from the curated list
- [x] Adding a stock via search persists it to the watchlist (tested with TSLA, AAPL)
- [x] Setting a target price saves and persists across page refresh
- [x] Removing a stock deletes it and updates the view immediately
- [x] Duplicate-add protection works (DB `UNIQUE` constraint + friendly redirect)

---

## 🚧 What's Ready to Build Tomorrow (Day 5)

- Watchlist add/remove/target-price is fully functional with real per-user data.
- `stock_api.py` is still an empty placeholder, ready to be filled in.
- Dashboard cards currently show "Price data: coming Day 5" — this is the exact hook Day 5 will replace with live Finnhub data.

## 🎯 Tomorrow's Objective (Day 5 — per Implementation Blueprint)

Integrate live stock data: build `stock_api.py` to call Finnhub's `/quote` and `/stock/metric` endpoints, update the `/dashboard` route to enrich each watchlist item with real price/% change/P/E, add graceful fallback for failed API calls, and add basic caching to respect Finnhub's free-tier rate limit.

No additional environment setup or planning required — Day 5 begins directly with implementation.
