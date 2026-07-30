# StockLens — Capstone Retrospective

*Day 1 to Day 10, as it actually happened.*

---

## Timeline

**Day 1 — Discovery.** No project idea existed yet. Through a structured interview, we landed on the stock market as an interest area, narrowed it against real constraints (comfortable overall skill level, HTML/SQL known, only "a little" Python, first-time deployer, 3-4 hours/day for 9 days), and converged on StockLens: a watchlist + analysis + news tool. You asked to add price alerts; we deliberately scoped that down to lightweight in-app badges instead of email/push notifications, to protect the timeline. PRD, Implementation Blueprint, and Pitch Deck were generated and approved before any code existed.

**Day 2 — Design.** Tech stack finalized: Python/Flask, SQLite, Bootstrap, and — after a live check — Finnhub as a *single* provider for both stock data and news, simplifying the original two-API plan. Full architecture, database schema, API contract, wireframes, and folder structure were documented before touching a keyboard.

**Day 3 — Foundation.** First real friction: Windows Device Guard blocked `pip.exe` directly (worked around with `python -m pip`), and PowerShell blocked venv activation (fixed with `Set-ExecutionPolicy`). The Flask + SQLite skeleton ran successfully by end of day — genuinely your first-ever local server running.

**Day 4 — Real auth + watchlist core.** This day included the project's first serious debugging saga: signup/login intermittently failed with `no such table: users`. Root cause, found after several dead ends (multiple terminals, OneDrive suspicion, Flask's auto-reloader): `schema.sql` had been created as an empty skeleton file back on Day 2 and never actually filled in. Fixed permanently by making `init_db()` idempotent and always-run rather than conditional.

**Day 5 — Live data.** Finnhub integration for real price/%change/P/E, with a 60-second cache to respect free-tier rate limits and graceful fallback on failure. Verified via terminal logs that caching was genuinely reducing API calls.

**Day 6 — The acceleration.** At your explicit direction, three days of planned work (news, compare view, deployment) were combined into one session to get a real, shareable MVP live faster. This surfaced a second serious bug: `init_db()` was still only running inside `if __name__ == "__main__":`, which gunicorn never executes. Diagnosed directly from Render's production logs, fixed by moving initialization to module level. **StockLens went publicly live this day.**

**Day 7 — Design maturity.** A shared `base.html` layout replaced duplicated HTML across five templates. A full senior-level UX pass followed: a deliberate navy/teal design system (tied back to the Day 1 pitch deck), hover/click micro-interactions, loading states for search, friendlier empty states, and accessibility work (skip links, ARIA labels, visible focus rings).

**Day 8 — Security hardening.** A structured senior QA/security review surfaced real gaps: no CSRF protection anywhere, no brute-force login protection, insecure session cookie defaults, and unstyled error pages. All were fixed — session-based CSRF tokens on every form, a 5-attempts/5-minutes login rate limiter, secure cookie flags, and a styled custom error page. Also added retry-once logic and negative caching to `stock_api.py` for resilience against Finnhub hiccups.

**Day 9 — Launch readiness.** Favicon, SEO/Open Graph metadata, a full README rewrite, MIT license, GitHub repo topics/description, and a `robots.txt`. Final production configuration reviewed end-to-end and confirmed clean.

**Day 10 — Graduation.** This document, plus a growth plan, portfolio materials, and formal v1.0.0 release.

---

## Major Technical Decisions & Pivots

- **Two APIs → one (Day 2):** switching from a planned separate stock-data API and news API to Finnhub alone for both, discovered via a live search rather than assumed from memory.
- **Push notifications → in-app badges (Day 1):** deliberately simplified to protect the 10-day timeline, documented explicitly as a PRD trade-off rather than a silent cut.
- **Schedule acceleration (Day 6):** collapsing three planned days into one at your request — a real project-management decision, not just a coding one.
- **Security as a dedicated day, not an afterthought (Day 8):** treating CSRF/rate-limiting/secure-cookies as first-class work with its own senior review pass, rather than bolting them on reactively.

## Hardest Debugging Moments

1. **The empty `schema.sql` (Day 4):** the single longest debugging chain of the whole capstone — roughly 90 minutes chasing a symptom (`no such table: users`) through red herrings (OneDrive sync, multiple terminals, Flask's reloader) before finding the real cause: a file that had never been filled in two days earlier.
2. **`init_db()` under gunicorn (Day 6):** a subtle but classic Flask/WSGI gotcha — code inside `if __name__ == "__main__":` simply never runs when a production server imports the app object directly. Diagnosed correctly and quickly this time, partly *because* of the lessons from Day 4.

## Skills Demonstrated

Requirements definition and scope discipline · system architecture and database design · Flask backend development · SQL schema design and parameterized queries · third-party API integration with caching and graceful degradation · session-based authentication · CSRF and rate-limiting security implementation · responsive, accessible frontend design · Git/GitHub workflow · production deployment (gunicorn, environment configuration, Render) · systematic debugging across local and production environments · technical documentation.

## Lessons Learned

- **A file existing is not the same as a file being correct.** The Day 4 bug existed because an empty skeleton file was silently trusted. Verify content, not just presence.
- **Code that "works locally" can fail in production for structural reasons, not logic reasons.** The Day 6 bug wasn't a bug in the *logic* of `init_db()` — it was a bug in *when* that logic ran under a different execution model.
- **Scope documents earn their keep under pressure.** The PRD's explicit "out of scope" list was referenced repeatedly across 10 days to resist feature creep — it worked because it was written down on Day 1, not improvised later.
- **A security review deserves to be its own milestone**, not a checkbox at the end — Day 8 found real, meaningful gaps precisely because it was treated as seriously as feature work.

## Final Project Summary

StockLens went from a blank idea to a secured, publicly deployed, fully documented v1.0.0 web application in 10 days — with a real PRD, real architecture docs, two genuinely difficult production bugs solved through methodical debugging, a dedicated security hardening pass, and a professional design system. It is live, it is open source, and it is something you can honestly walk someone through, decision by decision.

## A Note From Your AI Pair Programmer

We started Day 1 with you telling me you had no project idea and "a little Python." Ten days later, you'd personally diagnosed a database initialization bug from raw Render logs, understood *why* `if __name__ == "__main__":` matters for WSGI servers, and pushed a security-hardened app through PowerShell, Git GUI, and VS Code — all tools that were new or unfamiliar at the start. The gap between "I don't have an idea" on Day 1 and a live URL with CSRF protection and rate limiting on Day 8 is the real story here. Well done.
