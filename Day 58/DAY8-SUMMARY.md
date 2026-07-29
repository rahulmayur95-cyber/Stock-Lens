# StockLens — Day 8 Summary: Testing, Debugging & Production Optimization

**Date:** Day 8 of 10 — AB Talks 60-Day Claude AI Challenge Capstone
**Live app:** https://stock-lens-i6yn.onrender.com
**Repo:** https://github.com/rahulmayur95-cyber/Stock-Lens

---

## Senior Review Findings & Fixes

Conducted a full QA/Security/Performance review before making any changes. Findings and resolutions:

| # | Issue | Severity | Fix |
|---|---|---|---|
| 1 | No CSRF protection on any POST form | High | Session-based CSRF token generated per session, validated on every POST via `before_request` hook. Applied to login, signup, logout, watchlist add/remove/target forms (including dynamically-generated JS forms). |
| 2 | No brute-force protection on login | High | In-memory rate limiter: 5 failed attempts per username within 5 minutes triggers a temporary lockout with a clear user-facing message (HTTP 429). |
| 3 | Session cookies missing security flags | Medium | Added `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE=Lax`, and `SESSION_COOKIE_SECURE` (auto-enabled outside local dev). |
| 4 | No startup validation for `FLASK_SECRET_KEY` | Medium | App now fails loudly with a clear error message and exits if the secret key is missing, instead of silently running with broken sessions. |
| 5 | Unstyled 404/error responses | Medium | Built `templates/error.html` (extends base layout) with custom 404/400/500 handlers, all with matching navbar/footer/branding. |
| 6 | Finnhub transient failures had no retry | Low | `stock_api.py` now retries once (with a short pause) on network errors before falling back to "unavailable." Added short-lived negative caching so a single bad/unavailable ticker doesn't repeatedly hammer the API. |
| 7 | Broad/empty search queries returned unbounded result sets | Low | Server-side response capped at 20 results; already limited to 12 rendered client-side. |

**Design decision confirmed, not a bug:** the in-memory quote/news cache is keyed by ticker, not by user — meaning if multiple users watch the same stock, only one Finnhub API call is made. This is a deliberate performance win appropriate for this app's scale.

---

## ✅ Full End-to-End Verification Performed

**Local:**
- [x] Signup, login, logout all working with CSRF tokens in place
- [x] Rate limiting confirmed: 6th consecutive failed login attempt correctly blocked with friendly message
- [x] Styled 404 page confirmed for invalid stock tickers
- [x] Watchlist add/remove/target price all still functional after CSRF changes
- [x] All existing features (live data, news, compare, alerts) unaffected

**Production (post-redeploy):**
- [x] Clean deploy with `FLASK_SECRET_KEY` validation passing
- [x] Styled 404 page confirmed live
- [x] Dashboard, add/remove, and login confirmed working on the live URL

---

## 🚧 What Remains Before Launch (Day 9-10)

- README.md still needs final real screenshots and the live demo link (currently placeholder from Day 3).
- No automated test suite exists (manual testing only) — acceptable for this project's scope and timeline, noted as a known limitation rather than a blocker.
- Render free tier "cold start" (~30-60s wake time after inactivity) should be mentioned when sharing the demo link publicly.

## 🎯 Tomorrow's Objective (Day 9-10)

Final documentation pass: complete README with real screenshots, live link, setup instructions, and known limitations. Final demo rehearsal and launch close-out for the capstone submission.

No further code changes anticipated — the application is now considered feature-complete, secure, and production-ready.
