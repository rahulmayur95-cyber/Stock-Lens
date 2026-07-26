# StockLens — Day 6 Summary: MVP Complete & Deployed

**Date:** Day 6 of 10 — AB Talks 60-Day Claude AI Challenge Capstone

**Note:** Today's session combined the originally-scheduled Day 6 (news), Day 7 (compare view — alerts were already done Day 5), and Day 9 (deployment) work at your explicit direction, to deliver a complete, shareable MVP now rather than waiting until Day 9. This was a deliberate schedule acceleration, not scope creep.

---

## ✅ What Was Completed Today

### Milestone 1: News Integration
- Built `news_api.py` using Finnhub's `/company-news` endpoint (same provider/API key as stock data — no new signup, no new cost)
- Built real `templates/stock_detail.html`: live price/%change/P/E + 3-5 recent headlines with source, date, and working links
- 5-minute cache added (news changes slower than prices) with graceful empty-state handling

### Milestone 2: Compare View
- Built `templates/compare.html`: full sortable table (ticker, name, price, % change, P/E, target, alert)
- Built `static/js/sort_table.js`: dependency-free vanilla JS click-to-sort on any column, ascending/descending toggle
- Refactored `app.py` to add a shared `get_enriched_watchlist()` helper, used by both `/dashboard` and `/compare`, so the two views can never drift out of sync

### Milestone 3: Footer (Challenge Requirement)
- Added "Built with Claude as part of the AB Talks 60-Day Claude AI Challenge." to every page: login, signup, dashboard, stock detail, compare
- Verified visible on the deployed live version, not just locally

### Milestone 4: Deployment to Render (Free Tier)
- Added `gunicorn` as the production WSGI server (Flask's dev server is not used in production)
- Added `render.yaml` describing the build/start commands and required environment variables
- Created Render account (GitHub sign-in), connected the `Stock-Lens` repository, selected the **Free** instance tier
- Configured `FINNHUB_API_KEY` and `FLASK_SECRET_KEY` as environment variables directly in Render (never committed to Git)
- **Live URL:** https://stock-lens-i6yn.onrender.com

---

## 🐞 Deployment Bug Found & Fixed

**Issue:** After first deploy, signup failed live with `sqlite3.OperationalError: no such table: users`.

**Root cause:** `init_db()` was still called only inside `if __name__ == "__main__":`, which never executes when gunicorn imports the app object directly (gunicorn runs `app:app`, not `python app.py`). The local fix from earlier in the day had been made in the editor but the actual committed/pushed file still had the old structure.

**Fix:** Moved `init_db()` to module level (executes on import, regardless of how the app is started):
```python
init_db()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
```
Committed as a follow-up fix, Render auto-redeployed, and the live app was verified working immediately after.

**Lesson for future days:** always verify a fix was actually saved and pushed to the exact file/location expected — don't assume a local edit made it into a commit without checking the deployed/pushed version directly (we did this by viewing the file on GitHub).

---

## ✅ Full Verification Performed (on the LIVE deployed URL)

- [x] Signup and login work on production
- [x] Watchlist add/remove works, scoped per user
- [x] Live price/%change/P/E display correctly (tested NVDA, GOOGL)
- [x] Stock detail page shows real news headlines with working links
- [x] Compare view renders and sorting works correctly (verified reordering by Price)
- [x] Footer visible on every page on the live site
- [x] No paid services used anywhere — Finnhub free tier + Render free tier only

---

## 🚧 What Still Needs Polishing (Tomorrow)

- No shared `base.html` layout yet — navbar/footer HTML is currently duplicated across 5 templates. Low risk, but worth consolidating for maintainability.
- No dedicated mobile-responsiveness pass yet (Bootstrap's grid gives reasonable default behavior, but hasn't been explicitly tested at mobile widths).
- Minor UX polish opportunities: empty states, form validation messaging, consistent spacing.
- README.md still has placeholder content — needs the live demo link and real screenshots.
- Render free tier note: the app "sleeps" after inactivity and takes ~30-60 seconds to wake on first visit — worth mentioning when sharing the demo link with others.

## 🎯 Tomorrow's Objective (Day 7 — adjusted)

Since news, compare, alerts, and deployment are already done, tomorrow shifts to **UI/UX polish and full regression testing** (originally Day 8's scope): build a shared `base.html` layout, verify mobile responsiveness, tighten up empty/error states, and do a full end-to-end test pass on the live deployed app — bringing the schedule back in line for a final polish + documentation day (Day 10) to close out the capstone.

No additional setup required — Day 7 begins directly with polish work on the already-working, already-deployed MVP.
