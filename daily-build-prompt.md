# StockLens — Daily Build Prompt (Reusable for the 30-Day Growth Plan)

Copy this prompt into a new chat each day of the 30-day growth plan. Only change the **[DAY NUMBER]** placeholder — everything else stays the same throughout the month.

---

```
PROJECT CONTEXT: StockLens — post-v1.0.0 growth plan (30-day roadmap)

I'm working through a 30-day growth plan for StockLens, a stock watchlist and analysis
dashboard that shipped as v1.0.0 after a 10-day capstone build.

LINKS:
- GitHub repo: https://github.com/rahulmayur95-cyber/Stock-Lens
- Live deployed app: https://stock-lens-i6yn.onrender.com

TECH STACK: Python + Flask, SQLite (migrating to Postgres per the growth plan),
Bootstrap 5, Finnhub API (free tier), hosted on Render (free tier), gunicorn.
Security: CSRF protection, login rate limiting, secure sessions - already in place
as of v1.0.0. Do not remove or weaken any of this.

SOURCE OF TRUTH: Please read 30-day-growth-plan.md in the repo root for the full plan.
Today is DAY [DAY NUMBER] of that plan. Complete ONLY that day's milestone -
do not skip ahead or redesign prior work.

MY SKILL LEVEL: Comfortable overall; learned Flask/SQLite/deployment during the
original 10-day capstone. I use VS Code + Git GUI/Source Control panel on Windows,
PowerShell terminal.

STANDING RULES:
- Whenever I need to do something manually (installing, configuring, deploying,
  running commands), give exact step-by-step instructions with real button/menu
  names and wait for my confirmation/screenshot before continuing.
- Never assume I've completed a step without confirmation.
- Use only free tools/APIs - no paid services.
- Generate complete, copy-pasteable files - no snippets or placeholders.
- Preserve all existing v1.0.0 functionality and security measures; do not
  regress anything that already works.
- If today's milestone depends on incomplete prior-day work, tell me clearly
  before proceeding rather than guessing or skipping ahead.
- End the session by confirming what was completed, updating any affected
  documentation, and helping me commit + push with a clear commit message
  referencing the day number (e.g., "Growth Plan Day 12: ...").

Please begin today's milestone now.
```

---

**Tip:** if a day's milestone turns out to be bigger than expected, it's fine to split it across two sessions — just tell the next session "Day X continued" instead of moving to Day X+1 prematurely, the same discipline used during the original 10-day build.
