# StockLens — System Architecture

**Status:** Finalized Day 2. Source of truth for implementation (Days 3–9).
**Related docs:** PRD, Implementation Blueprint, SCHEMA.md, API.md, UI-WIREFRAMES.md, PROJECT-STRUCTURE.md

---

## 1. Finalized Tech Stack

| Layer | Choice |
|---|---|
| Frontend | HTML + Jinja2 templates + Bootstrap 5 (CDN) |
| Backend | Python + Flask |
| Database | SQLite (file-based, `stocklens.db`) |
| Authentication | Flask sessions + Werkzeug password hashing |
| AI Model/API | None required for v1.0 |
| Stock + News Data | **Finnhub API** (single provider — `/quote`, `/stock/metric`, `/company-news` endpoints) |
| Hosting | Render (free tier, GitHub-connected auto-deploy) |
| Version Control | Git + GitHub |

**Why one data provider (Finnhub) instead of two:** Originally the blueprint assumed a separate stock API and news API. Finnhub offers both stock quotes/fundamentals and company news under one free API key (60 calls/minute, no credit card). This was approved on Day 2 as a scope-safe simplification — it reduces setup steps and failure points without changing any PRD feature.

---

## 2. Component Diagram

```mermaid
graph TB
    subgraph Client["Browser (User)"]
        UI["HTML Pages<br/>Bootstrap UI"]
    end

    subgraph Server["Flask Application (Render)"]
        Routes["Flask Routes<br/>(app.py)"]
        Auth["Auth Module<br/>(session + password hashing)"]
        WatchlistLogic["Watchlist Logic"]
        StockAPI["stock_api.py<br/>(Finnhub quote/fundamentals)"]
        NewsAPI["news_api.py<br/>(Finnhub company-news)"]
        Tickers["tickers.py<br/>(curated ticker list)"]
        Cache["Simple in-memory cache<br/>(per ticker, short TTL)"]
    end

    subgraph Data["Data Layer"]
        DB[("SQLite<br/>stocklens.db")]
    end

    subgraph External["External Service"]
        Finnhub["Finnhub API"]
    end

    UI -->|"HTTP requests"| Routes
    Routes --> Auth
    Routes --> WatchlistLogic
    Auth -->|"read/write users"| DB
    WatchlistLogic -->|"read/write watchlist rows"| DB
    WatchlistLogic --> StockAPI
    WatchlistLogic --> NewsAPI
    WatchlistLogic --> Tickers
    StockAPI --> Cache
    NewsAPI --> Cache
    StockAPI -->|"HTTPS + API key"| Finnhub
    NewsAPI -->|"HTTPS + API key"| Finnhub
    Routes -->|"rendered HTML"| UI
```

---

## 3. Data Flow — Dashboard Page Load (Core Flow)

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as Flask App
    participant D as SQLite DB
    participant C as Cache
    participant Fh as Finnhub API

    U->>F: GET /dashboard (with session cookie)
    F->>F: Check session for user_id
    alt Not logged in
        F-->>U: Redirect to /login
    else Logged in
        F->>D: SELECT watchlist WHERE user_id = ?
        D-->>F: List of tickers + target_price
        loop For each ticker
            F->>C: Check cached quote?
            alt Cache hit (fresh)
                C-->>F: Return cached quote
            else Cache miss/stale
                F->>Fh: GET /quote?symbol=TICKER
                Fh-->>F: price, % change
                F->>Fh: GET /stock/metric?symbol=TICKER
                Fh-->>F: P/E ratio
                F->>C: Store in cache
            end
        end
        F->>F: Compare price vs target_price -> alert flag
        F-->>U: Render dashboard.html with data
    end
```

---

## 4. Request Lifecycle (General Pattern)

```mermaid
flowchart LR
    A["Browser sends request"] --> B{"Route requires login?"}
    B -- No --> E["Handle request"]
    B -- Yes --> C{"session has user_id?"}
    C -- No --> D["Redirect to /login"]
    C -- Yes --> E["Handle request"]
    E --> F{"Needs DB data?"}
    F -- Yes --> G["Query SQLite"]
    F -- No --> H
    G --> H{"Needs external data?"}
    H -- Yes --> I["Call Finnhub (via stock_api.py / news_api.py)"]
    H -- No --> J
    I --> K{"API call succeeded?"}
    K -- No --> L["Use fallback: 'Data unavailable'"]
    K -- Yes --> J["Build template context"]
    L --> J
    J --> M["Render Jinja2 template"]
    M --> N["Return HTML response to browser"]
```

---

## 5. AI Interaction

**Not applicable for v1.0.** StockLens does not call any AI/LLM model at runtime — it is a data dashboard built on deterministic API calls and SQL queries. This keeps the app free of AI API costs and complexity, consistent with the approved PRD scope. (Noted in PRD Future Scope: AI-based news sentiment could be a future addition, not v1.0.)

---

## 6. External Services

| Service | Purpose | Auth Method | Failure Handling |
|---|---|---|---|
| Finnhub API | Stock quotes, fundamentals (P/E), company news | API key in query string / header | Wrapped in try/except; on failure, show "Data unavailable" for that stock instead of crashing the page (per PRD NFRs) |
| Render | Hosting the deployed Flask app | GitHub repo connection | N/A (deployment-time, not runtime) |
| GitHub | Source control, triggers Render auto-deploy | Git/HTTPS or SSH | N/A |

---

## 7. Caching Strategy (Simplification for Free-Tier API Limits)

To stay within Finnhub's free-tier rate limit (60 calls/minute) and keep the dashboard fast:

- A simple in-memory dictionary cache keyed by ticker symbol, storing `{data, timestamp}`.
- On each dashboard/detail page load, if a cached entry exists and is less than ~60 seconds old, reuse it instead of calling Finnhub again.
- This cache resets when the app restarts (acceptable for v1.0 — no persistence needed for cache data).

---

## 8. Security Notes (v1.0 scope)

- Passwords hashed with Werkzeug's `generate_password_hash` — never stored or logged in plaintext.
- All SQL queries use parameterized statements (no string-concatenated SQL) to prevent SQL injection.
- API keys and Flask `secret_key` stored as environment variables, never committed to Git (`.env` is git-ignored; `.env.example` documents required variable names only).
- Session cookies used for login state; no OAuth/social login in v1.0 (per PRD).
