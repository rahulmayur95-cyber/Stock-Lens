import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from tickers import search_tickers, is_valid_ticker, get_company_name
from stock_api import get_quote
from news_api import get_news

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

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
    live quote data + computed alert status. Used by both /dashboard and /compare
    so the two views never drift out of sync with each other.
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
        return render_template("signup.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username or not password:
        return render_template("signup.html", error="Username and password are required.")

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

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid username or password.", username=username)

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
    query = request.args.get("q", "")
    results = search_tickers(query)
    return jsonify({"results": results})


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
            if target_price <= 0:
                return redirect(url_for("dashboard", message="Target price must be a positive number."))
        except ValueError:
            return redirect(url_for("dashboard", message="Target price must be a number."))

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
        return "<h1>Stock not found</h1><p><a href='/dashboard'>Back to Dashboard</a></p>", 404

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


if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)
