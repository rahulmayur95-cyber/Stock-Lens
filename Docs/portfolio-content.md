# StockLens — Portfolio Content

Tailored specifically to this project. Copy/adapt any section for LinkedIn, resume, portfolio site, or interviews.

---

## Project Description (Long — Portfolio/LinkedIn)

**StockLens** is a full-stack stock watchlist and analysis dashboard I built solo over a 10-day sprint, taking it from a blank idea to a secure, publicly deployed production application. Users can create an account, build a personal watchlist from a curated list of popular stocks, view live prices and P/E ratios pulled from the Finnhub API, read recent news per stock, set price-target alerts that trigger visual in-app badges, and compare their entire watchlist in a sortable table.

The project follows a real software development lifecycle — requirements gathering and a formal PRD, system architecture and database design, iterative implementation, a dedicated security-hardening pass (CSRF protection, rate limiting, secure sessions), a senior-level UI/UX design review, and a full production launch with SEO metadata, custom error pages, and complete documentation.

Built with Python, Flask, SQLite, and Bootstrap, deployed on Render, using only free-tier tools throughout.

**Live:** https://stock-lens-i6yn.onrender.com
**Code:** https://github.com/rahulmayur95-cyber/Stock-Lens

## Project Description (Short — Resume/Portfolio Card)

StockLens — a secure, full-stack stock watchlist and price-alert dashboard built solo in 10 days (Flask, SQLite, Finnhub API), from PRD through deployment. Live app + open source on GitHub.

---

## Resume Bullet Points

Pick 2-4 depending on the role you're applying for:

- Designed and shipped **StockLens**, a full-stack stock watchlist and analysis web application, independently completing the entire SDLC from requirements and architecture through deployment in a 10-day sprint.
- Built a Flask/SQLite backend with session-based authentication, CSRF protection, and brute-force rate limiting, following OWASP-aligned security practices appropriate for the application's scope.
- Integrated a third-party financial data API (Finnhub) for live stock quotes, fundamentals, and news, implementing caching and retry logic to handle rate limits and transient failures gracefully.
- Conducted a structured senior-level UX and accessibility review, implementing a custom design system, responsive layouts, ARIA labeling, and keyboard-accessible navigation.
- Deployed and maintained a production Flask application on Render using gunicorn, environment-based configuration, and a documented CI-free deploy workflow via GitHub integration.
- Diagnosed and resolved multiple production bugs independently (database initialization under WSGI servers, PowerShell environment issues, execution policy conflicts), demonstrating practical debugging skills across the full stack.

---

## Interview Talking Points

**"Tell me about a project you're proud of."**
> "I built StockLens, a stock watchlist app, over a 10-day solo sprint — from a blank idea to a deployed, secured production app. What I'm most proud of isn't just that it works, but that I followed a real process: I wrote a PRD before touching code, designed the database schema and API contract on paper first, and only then started building. That discipline paid off — when I hit a nasty bug on Day 4 where the database silently had no tables, I could trace it back to a specific decision (an empty schema file from Day 2) instead of guessing."

**"Tell me about a bug you had to debug."**
> "On deployment day, signup worked locally but failed in production with 'no such table: users.' I checked Render's logs and found my database initialization code was wrapped in `if __name__ == '__main__':` — which never runs when gunicorn imports the app directly instead of running it as a script. I moved the initialization to module level so it runs on import regardless of how the app starts. It taught me to think about *how* code actually gets executed in different environments, not just whether the logic is correct."

**"How do you approach security in a project like this?"**
> "I did a dedicated security review before launch, treating it like a checklist a senior engineer would run: CSRF tokens on every state-changing form, rate limiting on login to prevent brute-force attempts, secure/HTTPOnly/SameSite session cookies, and parameterized SQL everywhere. I also made sure the app fails loudly — for example, if the Flask secret key isn't configured, the app refuses to start rather than silently running with insecure sessions."

**"How did you handle scope, given the tight timeline?"**
> "Every day I worked from a locked scope document — the PRD explicitly listed what was out of scope for v1.0, like real-time price streaming or portfolio P&L tracking. When I was tempted to add features mid-build, I referred back to that list instead of improvising. That's what let me actually ship something complete in 10 days instead of an unfinished, over-ambitious version."

---

## Short Demo Script (3–4 minutes)

**0:00–0:30 — Hook**
"This is StockLens, a stock watchlist app I built solo in 10 days — from idea to a secured, live production app. Let me show you how it works."

**0:30–1:15 — Core flow**
- Show signup/login → "Basic auth, but with CSRF protection and rate limiting against brute-force attempts."
- Search and add 2 stocks → "Live prices and P/E ratios come from the Finnhub API."

**1:15–2:00 — Feature depth**
- Click into a stock detail page → "Recent news headlines, pulled live."
- Set a target price → show the alert badge → "This is a lightweight in-app alert — no backend jobs needed, it just checks on page load."
- Go to Compare → click to sort → "A sortable comparison table across the whole watchlist."

**2:00–2:45 — Under the hood**
- Mention: "It's a Flask + SQLite app, deployed on Render, with a proper security pass — CSRF tokens, secure cookies, custom error pages — and a full PRD/architecture doc trail on GitHub if you want to see the process."

**2:45–3:15 — Close**
"The whole build — including a senior-style UX and security review — is documented day by day in the repo. Happy to walk through any part of the code or the decisions behind it."

---

## GitHub Repository Metadata Recommendations

**Description:** *(already set Day 9)*
> A free stock watchlist, analysis, and price alert dashboard — built as a 10-day capstone for the AB Talks 60-Day Claude AI Challenge.

**Topics:** *(already set Day 9)*
`flask` `python` `sqlite` `finnhub-api` `stock-market` `dashboard` `bootstrap` `claude-ai`

**Additional topics to consider adding today:**
`portfolio-project` `capstone-project` `csrf-protection` `webapp`

**Suggested "Website" field:** already set to the live Render URL — confirm it's still there.
