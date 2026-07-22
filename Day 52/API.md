# StockLens — API Design (Internal Flask Routes)

**Status:** Finalized Day 2. Defines every route needed for v1.0. No implementation yet — this is the contract Day 3–7 will build against.

**Convention:** These are server-rendered Flask routes (return HTML via Jinja2), not a JSON REST API — consistent with the PRD's simple, template-based architecture. Where a route is form-submission-only (POST that redirects), that's noted.

---

## Authentication Routes

### `GET /signup`
- **Purpose:** Show the signup form.
- **Auth:** None required.
- **Response:** Renders `signup.html`.

### `POST /signup`
- **Purpose:** Create a new user account.
- **Request (form data):** `username` (string), `password` (string), `confirm_password` (string)
- **Validation:**
  - `username` not empty, not already taken
  - `password` not empty, minimum 6 characters (simple rule for v1.0)
  - `password` matches `confirm_password`
- **Response (success):** Redirect to `/login` with a success message.
- **Response (error):** Re-render `signup.html` with an inline error message (e.g., "Username already taken").
- **Auth:** None required.
- **Error cases:** Duplicate username → 200 with error message (not a crash); empty fields → 200 with validation message.

### `GET /login`
- **Purpose:** Show the login form.
- **Auth:** None required (if already logged in, redirect to `/dashboard`).
- **Response:** Renders `login.html`.

### `POST /login`
- **Purpose:** Authenticate a user and start a session.
- **Request (form data):** `username`, `password`
- **Validation:** Both fields required; credentials must match a stored hash.
- **Response (success):** Set `session['user_id']`, redirect to `/dashboard`.
- **Response (error):** Re-render `login.html` with "Invalid username or password" (generic message — do not reveal whether username exists, for basic security hygiene).
- **Auth:** None required.
- **Error cases:** Wrong password, nonexistent username → same generic error either way.

### `POST /logout`
- **Purpose:** End the user's session.
- **Auth:** Must be logged in.
- **Response:** Clear session, redirect to `/login`.

---

## Watchlist Routes

### `GET /dashboard`
- **Purpose:** Main watchlist view — shows all of the user's stocks with live metrics and alert badges.
- **Auth:** Required (redirect to `/login` if not authenticated).
- **Response:** Renders `dashboard.html` with: list of watchlist entries, each enriched with live price/%change/P/E (from Finnhub via `stock_api.py`) and computed `alert` boolean.
- **Error cases:** If Finnhub call fails for a given ticker, that stock's card shows "Data unavailable" instead of breaking the page.

### `GET /search?q=<query>`
- **Purpose:** Search the curated ticker list (for the "add stock" box).
- **Auth:** Required.
- **Request:** Query param `q` (partial ticker or company name).
- **Response:** Renders a partial list (HTML fragment or filtered `dashboard.html` state) of matching tickers from `tickers.py`. No external API call — this searches the static curated list only.
- **Validation:** `q` may be empty (returns full curated list) or any string (case-insensitive partial match).
- **Error cases:** No matches → empty result set, shown as "No matching stocks found."

### `POST /watchlist/add`
- **Purpose:** Add a ticker to the logged-in user's watchlist.
- **Auth:** Required.
- **Request (form data):** `ticker` (string, must exist in curated list)
- **Validation:**
  - `ticker` must be in the curated list (`tickers.py`) — reject unknown tickers.
  - `(user_id, ticker)` must not already exist (DB `UNIQUE` constraint backs this up).
- **Response (success):** Redirect to `/dashboard`.
- **Response (error):** Redirect to `/dashboard` with a flash message ("Already in your watchlist" / "Unknown ticker").
- **Error cases:** Duplicate add attempt → friendly message, not a crash (DB constraint will raise `IntegrityError`, caught and handled).

### `POST /watchlist/remove/<id>`
- **Purpose:** Remove a stock from the watchlist.
- **Auth:** Required.
- **Request:** URL parameter `id` (watchlist row ID).
- **Validation:** The row's `user_id` must match `session['user_id']` — never trust the client; a user must not be able to delete another user's row by guessing an ID.
- **Response (success):** Redirect to `/dashboard`.
- **Error cases:** `id` doesn't belong to the logged-in user → ignore/403-style redirect with no data change; `id` doesn't exist → redirect with no-op.

### `POST /watchlist/target/<id>`
- **Purpose:** Set or update the target price for a watchlist entry.
- **Auth:** Required.
- **Request:** URL parameter `id`; form data `target_price` (number, or empty to clear the alert).
- **Validation:**
  - `id` must belong to the logged-in user.
  - `target_price` must be a positive number if provided, or empty/null to clear it.
- **Response (success):** Redirect to `/dashboard`.
- **Error cases:** Non-numeric input → redirect with validation error message; `id` not owned by user → no-op.

---

## Stock Detail Route

### `GET /stock/<ticker>`
- **Purpose:** Show detail view for one stock: metrics + news headlines.
- **Auth:** Required.
- **Request:** URL parameter `ticker`.
- **Validation:** `ticker` must exist in the curated list; if not, show a friendly "Stock not found" page (404-style, not a crash).
- **Response:** Renders `stock_detail.html` with live quote/fundamentals (`stock_api.py`) and 3–5 news headlines (`news_api.py`).
- **Error cases:**
  - Finnhub quote call fails → show "Price data unavailable" section, rest of page still renders.
  - Finnhub news call fails or returns empty → show "No recent news found" instead of an empty broken section.

---

## Comparison Route

### `GET /compare`
- **Purpose:** Sortable table of all watchlisted stocks with metrics, target price, and alert status.
- **Auth:** Required.
- **Response:** Renders `compare.html` with a table; sorting is handled client-side via `static/js/sort_table.js` (no extra server round-trip needed).
- **Error cases:** Empty watchlist → show "Add stocks to your watchlist to compare them" instead of an empty table.

---

## Route Summary Table

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/signup` | No | Show signup form |
| POST | `/signup` | No | Create account |
| GET | `/login` | No | Show login form |
| POST | `/login` | No | Authenticate, start session |
| POST | `/logout` | Yes | End session |
| GET | `/dashboard` | Yes | Main watchlist view |
| GET | `/search` | Yes | Search curated ticker list |
| POST | `/watchlist/add` | Yes | Add ticker to watchlist |
| POST | `/watchlist/remove/<id>` | Yes | Remove ticker from watchlist |
| POST | `/watchlist/target/<id>` | Yes | Set/update target price |
| GET | `/stock/<ticker>` | Yes | Stock detail + news |
| GET | `/compare` | Yes | Comparison table |

**Total: 12 routes — matches exactly the feature set in the PRD, no more, no less.**
