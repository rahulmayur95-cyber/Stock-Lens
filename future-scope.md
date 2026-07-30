# StockLens — Future Scope

How this specific project could realistically evolve, broken into honest, achievable horizons.

---

## Next 3 Months: Solidify the Foundation

**Goal:** turn a solid MVP into a genuinely reliable daily-use tool.

- **Persistent database:** migrate off Render's ephemeral SQLite filesystem to a free-tier hosted Postgres (e.g., Render's own free Postgres, Supabase, or Neon) so watchlist data survives redeploys.
- **Password reset flow:** add email-based password reset (using a free transactional email tier like Resend or Brevo) — currently the single biggest basic-auth gap.
- **Automated testing:** add a `pytest` suite covering auth, watchlist CRUD, and the alert-calculation logic — currently all testing is manual, which won't scale as features grow.
- **Real-time-ish refresh:** add a manual "Refresh" button on the dashboard that bypasses the cache for users who want an up-to-the-minute price without waiting for a full page reload.
- **Expanded ticker list:** grow from ~60 curated tickers to a searchable subset of a few hundred, while still respecting Finnhub's free-tier rate limits via smarter caching.

## Next 6 Months: Deepen the Product

**Goal:** move from "watchlist" to genuinely useful investing companion.

- **Portfolio tracking:** let users log actual buy/sell transactions and see real profit/loss, not just watchlist price movement — this was explicitly deferred in the v1.0 PRD and is the most-requested type of feature for a tool like this.
- **Email/push alerts:** replace the in-app-only alert badge with real notifications (free tier via a service like Resend or a browser push API), closing the gap noted in the original PRD's "Future Scope."
- **Historical price charts:** add a simple price history chart per stock (Finnhub's free tier includes candle data) — currently the app only shows a snapshot, not a trend.
- **Sentiment on news:** lightweight positive/negative tagging on news headlines using a free/open-source sentiment library (not a paid AI API), giving users faster context without reading every article.
- **Multi-device session handling:** review and harden session behavior across multiple devices/tabs as usage grows.

## Next 12 Months: Platform Maturity

**Goal:** a tool ready for a wider audience, not just a personal project.

- **Full market search:** move beyond the curated list entirely, with a proper search-as-you-type against a broader symbol database.
- **Mobile app or PWA:** convert the responsive web app into an installable Progressive Web App so it behaves like a native app on phones.
- **Team/shared watchlists:** allow a watchlist to be shared (read-only or collaborative) — useful for investment clubs or teaching contexts.
- **Public API:** expose a small, rate-limited read-only API so other developers could build on top of a user's watchlist data (with explicit opt-in).
- **Accessibility audit at scale:** commission or run a full WCAG 2.1 AA audit now that the user base (hypothetically) has grown beyond the original solo-developer testing.

---

## Deliberately Not on This Roadmap

Consistent with the original PRD's philosophy of protecting scope: this roadmap does not include becoming a trading/brokerage platform, real-money transactions, or AI-generated investment advice — those introduce regulatory and liability considerations far beyond this project's intent as a personal tracking and learning tool.
