# StockLens — Day 3 Summary: Project Setup & Foundation

**Date:** Day 3 of 10 — AB Talks 60-Day Claude AI Challenge Capstone

---

## ✅ What Was Completed Today

### Environment Setup
- Confirmed Python 3.12.8 already installed (no install needed)
- Discovered and worked around a Windows Device Guard policy blocking `pip.exe` directly — solved by using `python -m pip` for all package management
- Confirmed VS Code already installed; installed the official Microsoft Python extension
- Opened project folder in VS Code and trusted the workspace

### Project Initialization
- Created and activated a Python virtual environment (`venv`)
- Fixed a PowerShell execution policy block preventing venv activation (`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)
- Installed core dependencies: Flask 3.1.3, requests 2.34.2, python-dotenv 1.2.2 (+ sub-dependencies)
- Generated `requirements.txt` with all pinned versions

### Repository Setup
- Verified the Day 2 GitHub clone was correctly linked to Git (`git status` confirmed branch `main`, connected to `origin/main`)
- Filled in `.gitignore` (previously empty) to exclude `.env`, `venv/`, `__pycache__/`, `*.pyc`, `*.db`, `.vscode/`
- Filled in `.env.example` with documented variable names (`FINNHUB_API_KEY`, `FLASK_SECRET_KEY`)
- Created real `.env` file with actual Finnhub API key and a generated Flask secret key
- Confirmed via `git status` that `.env` and `venv/` are correctly excluded from tracking
- Branching strategy confirmed: single `main` branch, direct commits (appropriate for solo 10-day build)

### Foundation Built
- Wrote `app.py`: Flask app initialization, environment variable loading, reusable database connection function, automatic database initialization from `schema.sql`, one live route (`/`) and one auth-scaffolded placeholder route (`/dashboard`)
- Ran the app successfully — confirmed `stocklens.db` auto-created with `users` and `watchlist` tables
- Verified in-browser: `/` shows "StockLens is running"; `/dashboard` correctly redirects to `/` when not logged in, proving the session-based auth scaffold works

---

## 🔧 Issues Encountered & Resolved

| Issue | Resolution |
|---|---|
| `pip.exe` blocked by organization's Device Guard policy | Use `python -m pip` instead of `pip` for all package commands, project-wide |
| PowerShell blocked venv activation script | Ran `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once |
| Terminal initially in wrong folder for `git status` | Navigated into the correct cloned repo folder with `cd "stock-Lens"` |

No blocking issues remain. No scope, timeline, or architecture changes were required.

---

## 🚧 What's Ready to Build Tomorrow (Day 4)

- Foundation is fully working: Flask + SQLite + env vars + auth scaffold + Git, all verified locally.
- `templates/` folder is ready to receive real HTML files.
- `tickers.py` is ready to be populated with the curated stock list.
- Database schema (`users`, `watchlist`) is live and tested.

## 🎯 Tomorrow's Objective (Day 4 — per Implementation Blueprint)

Build the **Watchlist Core**: populate `tickers.py` with a curated list of 50–100 stocks, build the search/add box, build the real `dashboard.html` template showing the user's watchlist (tickers only, no live data yet — that's Day 5), and implement add/remove functionality scoped correctly per logged-in user.

No additional environment setup, tooling, or planning is required — Day 4 begins directly with feature implementation.
