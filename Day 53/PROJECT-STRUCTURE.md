# StockLens — Project Structure (Updated Day 3)

**Status:** Updated after Day 3 foundation build. Original structure from Day 2 is unchanged in design — this update reflects what now actually exists on disk, plus two files not explicitly listed on Day 2 (`.env`, `venv/`).

---

## 1. Full Folder Structure (Current State — End of Day 3)

```
stock-Lens/
│
├── app.py                  # ✅ BUILT Day 3: Flask app entry point, DB connection, init_db(),
│                            #    routes: / (home) and /dashboard (placeholder, auth-scaffolded)
├── schema.sql               # ✅ Unchanged from Day 2 — used by init_db() to create tables
├── tickers.py                # ⏳ Still empty — populated Day 4
├── stock_api.py               # ⏳ Still empty — populated Day 5
├── news_api.py                  # ⏳ Still empty — populated Day 6
├── requirements.txt              # ✅ BUILT Day 3: Flask, requests, python-dotenv + sub-dependencies, pinned
├── .gitignore                     # ✅ BUILT Day 3: excludes .env, venv/, __pycache__/, *.pyc, *.db, .vscode/
├── .env.example                    # ✅ BUILT Day 3: documents FINNHUB_API_KEY, FLASK_SECRET_KEY (no real values)
├── .env                              # ✅ BUILT Day 3: real secrets — NEVER committed (git-ignored)
├── README.md                          # ⏳ Still placeholder — filled in fully Day 10
├── stocklens.db                        # ✅ AUTO-GENERATED Day 3 on first run — git-ignored
│
├── venv/                                # ✅ CREATED Day 3: local virtual environment — git-ignored
│
├── templates/                             # ⏳ Empty — first templates (signup.html, login.html) built Day 3-4 boundary → actually Day 4 per blueprint... see note below
│
├── ARCHITECTURE.md                          # ✅ From Day 2
├── SCHEMA.md                                 # ✅ From Day 2
├── API.md                                     # ✅ From Day 2
├── UI-WIREFRAMES.md                            # ✅ From Day 2
├── PROJECT-STRUCTURE.md                         # ✅ This file (updated Day 3)
│
└── static/                                       # Static assets
    ├── css/                                         # ⏳ Empty — populated Day 8
    └── js/                                            # ⏳ Empty — populated Day 4 & 7
```

**Note on `templates/`:** Day 3's foundation intentionally used plain string returns (`return "<h1>...</h1>"`) instead of real `.html` template files, to keep today focused purely on infrastructure (Flask + DB + env + auth scaffold) without pulling in Day 3/4 feature work early. Real templates (`signup.html`, `login.html`) begin Day 3→4 handoff, built as the first task of Day 4 per the blueprint. This is a timing clarification, not a scope change.

---

## 2. What's New Since Day 2

| Item | Status | Notes |
|---|---|---|
| `venv/` | New | Virtual environment folder, isolates project dependencies. Git-ignored. |
| `.env` | New | Real secrets file. Git-ignored. Not listed explicitly in Day 2's structure, added now as standard practice alongside `.env.example`. |
| `stocklens.db` | New (auto-generated) | Created by `init_db()` the first time `app.py` runs. Git-ignored per SCHEMA.md notes about Render's ephemeral filesystem. |
| `app.py` | Filled in | Now contains real foundation code: Flask app, DB connection helper, `init_db()`, two routes. |
| `requirements.txt` | Filled in | Previously empty skeleton file, now has 14 pinned packages. |
| `.gitignore` | Filled in | Previously empty skeleton file, now correctly excludes secrets and generated files. |

---

## 3. Confirmed Working (Day 3 Verification)

- ✅ Flask app runs without errors (`python app.py`)
- ✅ SQLite database auto-created from `schema.sql`
- ✅ Environment variables load correctly from `.env`
- ✅ Basic routing works (`/`)
- ✅ Auth scaffold works (`/dashboard` redirects when not logged in)
- ✅ Structure matches Day 2's ARCHITECTURE.md and PROJECT-STRUCTURE.md design intent

No changes to the planned Day 4–10 structure were required — everything proceeded as designed.
