# StockLens — ENVIRONMENT.md

**Purpose:** Documents every environment variable, tool, and configuration setting used in this project.

---

## Environment Variables

All variables are stored in a local `.env` file (never committed to Git). `.env.example` documents the required names with placeholder values only.

| Variable | Purpose | Where to get it | Example format |
|---|---|---|---|
| `FINNHUB_API_KEY` | Authenticates requests to Finnhub for stock quotes, fundamentals, and company news | Free signup at https://finnhub.io/register — key shown on your Finnhub Dashboard | `csomething123abc` (long alphanumeric string) |
| `FLASK_SECRET_KEY` | Signs and secures Flask session cookies (keeps login sessions safe from tampering) | You generate this yourself — any long, random, unpredictable string | `x7Kq9!mPz2vBn5wRtY8sLf3` (made up by you) |

**Rule:** `.env` is listed in `.gitignore` and must never be committed or pasted into chat/screenshots. `.env.example` is safe to commit since it contains no real values.

---

## `.env.example` (safe template, already committed)

```
FINNHUB_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

---

## Tools & Their Roles

| Tool | Version (confirmed Day 3) | Role in this project |
|---|---|---|
| Python | 3.12.8 | Backend language/runtime |
| pip | 24.3.1 | Installs Python packages (accessed via `python -m pip` due to Device Guard policy on this machine) |
| Flask | 3.1.3 | Web framework — routing, templates, sessions |
| Werkzeug | 3.1.8 | Underlying WSGI library Flask depends on; also provides password hashing functions used for auth |
| Jinja2 | 3.1.6 | Templating engine for rendering HTML pages with dynamic data |
| requests | 2.34.2 | Makes HTTP calls to the Finnhub API |
| python-dotenv | 1.2.2 | Loads `.env` file contents into the app's environment at runtime |
| SQLite (via Python's built-in `sqlite3`) | Bundled with Python | Local file-based database — no separate install needed |
| Git | Bundled with Git for Windows | Version control |
| Git GUI | Bundled with Git for Windows | Visual interface for clone/commit/push |
| VS Code | Latest | Code editor |
| VS Code Python Extension (Microsoft) | Latest | Python language support inside VS Code |

---

## Configuration Files

| File | Purpose | Committed to Git? |
|---|---|---|
| `.env` | Real secrets (API key, Flask secret key) | ❌ No (git-ignored) |
| `.env.example` | Template documenting required variable names | ✅ Yes |
| `.gitignore` | Lists files/folders Git should never track | ✅ Yes |
| `requirements.txt` | Exact pinned dependency versions, used by Render during deployment | ✅ Yes |
| `schema.sql` | Database structure definition, run once to initialize `stocklens.db` | ✅ Yes |

---

## Local vs. Production Notes

- Locally, Flask runs in **debug mode** (`app.run(debug=True)`) — shows detailed errors and auto-reloads on code changes. This must be turned off/handled differently for the Day 9 production deployment on Render (production uses a proper WSGI server, not Flask's built-in dev server).
- `stocklens.db` is created automatically on first run via `init_db()` in `app.py` — no manual database setup step required locally.
