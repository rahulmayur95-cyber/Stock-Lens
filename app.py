import os
import sys
import sqlite3
import secrets
import time
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from tickers import search_tickers, is_valid_ticker, get_company_name
from stock_api import get_quote
from news_api import get_news

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Startup validation - fail loudly instead of silently breaking sessions
# ---------------------------------------------------------------------------
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
if not FLASK_SECRET_KEY:
    print("FATAL: FLASK_SECRET_KEY environment variable is not set. "
          "The app cannot start safely without it (sessions would be insecure).")
    sys.exit(1)

app.secret_key = FLASK_SECRET_KEY

# Secure session cookie settings (HTTPS-only in production, restricts cross-site use)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") != "development",
)

DB_PATH = "stocklens.db"


def get_db_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Ensure tables exist by always running schema.sql (safe: uses CREATE TABLE IF NOT EXISTS)."""
    conn = get_db_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database ready (tables verified/created).")


def login_required(view_func):
    """Decorator: redirect to /login if the user isn't authenticated."""
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapped.__name__ = view_func.__name__
    return wrapped


def get_enriched_watchlist(user_id):
    """
    Shared helper: fetch the user's watchlist rows and enrich each with
    live quote data + computed alert status. Used by both /dashboard and /compare.
    """
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    watchlist = []
    for row in rows:
        quote = get_quote(row["ticker"])

        alert = False
        if quote["available"] and row["target_price"] is not None and quote["price"] is not None:
            if quote["price"] <= row["target_price"]:
                alert = True

        watchlist.append({
            "id": row["id"],
            "ticker": row["ticker"],
            "name": get_company_name(row["ticker"]),
            "target_price": row["target_price"],
            "price": quote["price"],
            "change_percent": quote["change_percent"],
            "pe_ratio": quote["pe_ratio"],
            "data_available": quote["available"],
            "alert": alert,
        })

    return watchlist


# ---------------------------------------------------------------------------
# CSRF Protection
# ---------------------------------------------------------------------------
# Lightweight, dependency-free CSRF protection: a random token is stored in
# the session and must be echoed back by every state-changing (POST) form.
# This stops other websites from forging requests to StockLens on a logged-in
# user's behalf (e.g. a malicious page auto-submitting a "remove stock" form).

def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": get_csrf_token()}


@app.before_request
def csrf_protect():
    if request.method == "POST":
        form_token = request.form.get("csrf_token", "")
        session_token = session.get("csrf_token", "")
        if not form_token or not session_token or not secrets.compare_digest(form_token, session_token):
            abort(400, description="Your session expired or the form was submitted incorrectly. Please try again.")


# ---------------------------------------------------------------------------
# Basic login rate limiting (brute-force protection)
# ---------------------------------------------------------------------------
# In-memory tracker: { username_lowercase: [timestamp, timestamp, ...] }
# Resets on app restart - acceptable for this project's scale. A real
# production system at larger scale would use Redis or a similar shared store.
_login_attempts = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300  # 5 minutes


def _is_rate_limited(username):
    now = time.time()
    attempts = _login_attempts.get(username, [])
    attempts = [t for t in attempts if now - t < WINDOW_SECONDS]
    _login_attempts[username] = attempts
    return len(attempts) >= MAX_ATTEMPTS


def _record_failed_attempt(username):
    now = time.time()
    _login_attempts.setdefault(username, []).append(now)


def _clear_attempts(username):
    _login_attempts.pop(username, None)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(400)
def bad_request(e):
    description = getattr(e, "description", "Bad request.")
    return render_template("error.html", code=400, message=description), 400


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong on our end. Please try again."), 500


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("signup.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username or not password:
        return render_template("signup.html", error="Username and password are required.")

    if len(username) > 50:
        return render_template("signup.html", error="Username must be 50 characters or fewer.")

    if len(password) < 6:
        return render_template("signup.html", error="Password must be at least 6 characters.", username=username)

    if password != confirm_password:
        return render_template("signup.html", error="Passwords do not match.", username=username)

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        return render_template("signup.html", error="Username already taken.", username=username)

    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()

    return render_template("login.html", success="Account created. Please log in.", username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    username_key = username.lower()

    if _is_rate_limited(username_key):
        return render_template(
            "login.html",
            error="Too many failed login attempts. Please wait a few minutes and try again.",
            username=username,
        ), 429

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        _record_failed_attempt(username_key)
        return render_template("login.html", error="Invalid username or password.", username=username)

    _clear_attempts(username_key)
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard / Watchlist
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    watchlist = get_enriched_watchlist(session["user_id"])
    message = request.args.get("message")
    return render_template("dashboard.html", watchlist=watchlist, message=message)


@app.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    if len(query) > 50:
        query = query[:50]
    results = search_tickers(query)
    return jsonify({"results": results[:20]})  # cap payload size for broad/empty queries


@app.route("/watchlist/add", methods=["POST"])
@login_required
def watchlist_add():
    ticker = request.form.get("ticker", "").strip().upper()

    if not is_valid_ticker(ticker):
        return redirect(url_for("dashboard", message="Unknown ticker."))

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)",
            (session["user_id"], ticker),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return redirect(url_for("dashboard", message=f"{ticker} is already in your watchlist."))
    conn.close()

    return redirect(url_for("dashboard"))


@app.route("/watchlist/remove/<int:item_id>", methods=["POST"])
@login_required
def watchlist_remove(item_id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM watchlist WHERE id = ? AND user_id = ?",
        (item_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/watchlist/target/<int:item_id>", methods=["POST"])
@login_required
def watchlist_target(item_id):
    target_price_raw = request.form.get("target_price", "").strip()

    target_price = None
    if target_price_raw:
        try:
            target_price = float(target_price_raw)
        except ValueError:
            return redirect(url_for("dashboard", message="Target price must be a number."))

        if target_price <= 0:
            return redirect(url_for("dashboard", message="Target price must be a positive number."))
        if target_price > 1_000_000:
            return redirect(url_for("dashboard", message="Target price seems too high. Please double-check."))

    conn = get_db_connection()
    conn.execute(
        "UPDATE watchlist SET target_price = ? WHERE id = ? AND user_id = ?",
        (target_price, item_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Stock Detail
# ---------------------------------------------------------------------------

@app.route("/stock/<ticker>")
@login_required
def stock_detail(ticker):
    ticker = ticker.strip().upper()
    if not is_valid_ticker(ticker):
        abort(404)

    name = get_company_name(ticker)
    quote = get_quote(ticker)
    news = get_news(ticker)

    return render_template(
        "stock_detail.html",
        ticker=ticker,
        name=name,
        price=quote["price"],
        change_percent=quote["change_percent"],
        pe_ratio=quote["pe_ratio"],
        data_available=quote["available"],
        news=news,
    )


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------

@app.route("/compare")
@login_required
def compare():
    watchlist = get_enriched_watchlist(session["user_id"])
    return render_template("compare.html", watchlist=watchlist)


init_db()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
