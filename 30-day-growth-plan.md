# StockLens — 30-Day Growth Plan

A realistic, one-milestone-per-day roadmap taking StockLens from v1.0.0 toward the "Next 3 Months" goals in `future-scope.md`. Each day assumes ~1-2 hours and builds on the previous day. Use `daily-build-prompt.md` each day to execute.

## Week 1: Persistence & Reliability Foundations
1. Research free-tier hosted Postgres options (Render Postgres, Supabase, Neon); pick one and create the account.
2. Create a Postgres database instance and note connection credentials (store safely, not in Git).
3. Update `schema.sql` for Postgres syntax differences; test schema creation against the new database locally.
4. Add `psycopg2` (or equivalent) and refactor `get_db_connection()` to support Postgres via environment variable, with SQLite as a local dev fallback.
5. Migrate `app.py` database calls to work correctly against Postgres; test full auth + watchlist flow locally against the new DB.
6. Update Render environment variables and deploy; verify data survives a manual redeploy (the core problem this fixes).
7. Update README and ENVIRONMENT.md to reflect the new database setup; commit "Week 1: Persistent database migration."

## Week 2: Account Recovery & Testing Foundation
8. Research a free transactional email tier (Resend, Brevo) and create an account.
9. Add a `password_reset_tokens` table and generate secure, time-limited reset tokens.
10. Build `/forgot-password` route and email-sending logic (test with your own email first).
11. Build `/reset-password/<token>` route and form; validate token expiry and single-use behavior.
12. Style the new pages consistently with the existing design system (extend `base.html`).
13. Install `pytest`; write first test file covering signup/login success and failure cases.
14. Write tests for watchlist add/remove/target-price logic and the alert calculation; commit "Week 2: Password reset + initial test suite."

## Week 3: Data Freshness & Ticker Expansion
15. Add a "Refresh" button on the dashboard that bypasses the cache for a single manual reload.
16. Add a loading spinner/disabled state on the Refresh button while the request is in flight.
17. Audit Finnhub's free-tier rate limits against a larger ticker list; calculate a safe expansion size.
18. Expand `tickers.py` from ~60 to ~150-200 tickers across more sectors.
19. Add basic sector/category tagging to `tickers.py` for future filtering.
20. Update the search UI to show a "Popular" vs "All" toggle now that the list is larger.
21. Full regression test of search/add/remove with the larger list; commit "Week 3: Manual refresh + expanded ticker coverage."

## Week 4: Portfolio Tracking Groundwork
22. Design a `transactions` table (buy/sell, quantity, price, date) in a new schema migration file.
23. Build `/portfolio/add` route to log a manual buy/sell transaction.
24. Build basic portfolio P&L calculation logic (current value vs. cost basis).
25. Build a simple `/portfolio` view showing holdings and unrealized gain/loss.
26. Add navigation entry and empty-state design for the new Portfolio page, matching existing UX patterns.
27. Write tests for the P&L calculation logic (edge cases: partial sells, multiple buys at different prices).
28. Full end-to-end test of the new portfolio feature locally.
29. Deploy Week 4 changes to production; verify on live URL.
30. Final 30-day retrospective: update `future-scope.md` with what shipped, what's next, and write a short "30 days later" update to the README.

---

**Note:** This plan intentionally stays within free-tier tools throughout (Render Postgres/Supabase, free email tiers, Finnhub free tier) — consistent with the original project's constraint of using only free tools.
