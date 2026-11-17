# Overnight build 1 — addendum 5: the long queue (from WS0, 2026-11-15 01:15 UTC)

About 8–10 hours of work, and **Menno wants you to keep going all night**: when the list runs out, take the next item from "Bottomless backlog" below, and only stop when the session ends. Do it in this order; each item is its own commit (or small group of commits) with tests green, and a line in MORNING.md. If an item blocks (3 failures or 30 minutes without progress), log it in MORNING.md + QUESTIONS.md and move to the next one. Never stop early: if you finish, continue with "If there is still time".

You are the coordinator on `proto/overnight-1` tonight, so schema changes are yours. Read `docs/spec/` (on main) for the product detail behind every item.

## Rules for tonight
- Never invent data. Where a number needs a source you can't reach, leave it empty / `not-disclosed`, or mark `estimate: true` with a note. Placeholder fixture values live only in `**/fixtures/` and are visibly labelled as fixtures.
- No secrets, no calls to marketplaces, no scraping, no network in tests. Web research for citations is fine; cite URL + date.
- Brand name only from config (`brand.name = "EV Shortlist"`, Decision 018).
- Metric, euros, EN + NL complete; DE/FR/ES/IT may fall back to EN with keys present.
- Every new UI string gets a glossary ⓘ if it's a term; Simple / Detailed / Nerd respected.

## 0. Addendum 4 first (≈2.5 h)
If not done yet: everything in `workstreams/OVERNIGHT/ADDENDUM-4.md` (sync with main, R-01 → R-02 rename, Q-030 closed, T-018, T-023, T-030, T-024, T-026, T-036 with a fixture matrix behind a flag).

## 1. Country + language URLs (Decision 015) (≈1.5 h)
- Routes become `/{country}/{lang}/…`; `/{country}/` redirects to the country's default language (config, not code).
- hreflang for every country × language pair we serve + `x-default`; `sitemap.xml` listing only served pairs (a country's own languages + EN).
- Headers only suggest a language (a small banner), never redirect.
- Bring back static generation for model / generation / variant pages (this closes Q-033 / Q-034; write the answer under both).
- Playwright: language switch keeps filters and compare tray.

## 2. Price modes (Decision 017, T-043) (≈1.5 h)
- Schema `FinanceProfile` (country, product, typical_apr, default_term_months, default_deposit_pct, source, retrieved_at).
- `data/taxonomy/finance_profiles.yaml` for NL, DE, FR, BE, UK. Fill a typical used-car loan APR only where you find a citable public source (central bank statistics, e.g. ECB/DNB/Banque de France consumer-credit rates, or Bank of England); otherwise leave it empty and the calculator asks the user for a rate.
- Price-mode control (Buy outright / Loan per month / Lease per month) on Explore, model pages and Compare; remembered + in the URL.
- Calculator: monthly amount, total over the term, assumptions, "estimate, not an offer", and the CCD2 warning "Borrowing money costs money" (translated). Lease mode: labelled link placeholder only, no figures. No finance links for the UK.
- Glossary terms: loan, lease, private lease, balloon / PCP, residual value, total cost over the term (EN + NL).

## 3. Open data bundle (Decision 016) (≈1.5 h)
- Release step writes `data/releases/<n>/open/`: `variants.csv`, `variants.json`, `ATTRIBUTION.md` (per-source credit and licence), `LICENSE` (CC BY 4.0), `README.md` (release number, date, field list with units).
- Only licence-gate-passed sources; ODbL-derived values excluded (test this).
- `/[country]/[lang]/data` page: what's in it, licence, how to cite, download links, release history.

## 4. /learn content drafts (≈2 h)
Write EN + NL first drafts in `content/learn/<slug>/<lang>.md`, plain language, every claim linked to its rule or statistic (sources are in the spec tabs), front matter `review: needed`:
- `charging-2026` — "Charging in 2026: what's changed" (spec: Charging buildout, "First-time buyers"; leave US/AU out).
- `plugs-and-bidirectional` — incl. "Buying a wallbox from 2027" (ISO 15118-20 is the protocol, not two-way hardware) (spec: Bidirectional & plugs).
- `winter-range` — "Winter range explained" (spec: Trip fit §2).
- `chemistries` and `voltage-classes` from the Battery & voltage guide tab.
Render them through the existing `/learn` route with glossary tooltips.

## 5. Release QA checks (R-05 §1) (≈1.5 h)
Pipeline checks that run on every release and write `data/releases/<n>/qa.json` + a short `qa.md`:
- provenance completeness (blocking), licence gate (blocking), diff vs previous release (variant count, coverage per field, value changes beyond tolerance), outliers (P1–P99 per segment + physical impossibilities: usable > gross kWh, > 10 km/kWh WLTP, DC average > peak), coverage report for the top-40 used models.
- Tests with fixtures for each rule.

## 6. Security baseline in code (audits/A-01, "before staging") (≈1.5 h)
Do the items that are code, not server work:
- Security headers + a strict CSP in Next.js; no inline scripts without nonce.
- GitHub Actions: `permissions:` least privilege per job, actions pinned to commit SHA, no secrets in PR workflows from forks.
- Pipeline fetchers: allowlist of hosts from `data/sources.yaml`, block private/loopback IPs (SSRF guard), timeouts and size caps.
- Staff/review page: behind an env-flagged basic guard until real auth exists (Q-035), never linked publicly.
- Lockfiles committed; `pnpm audit` / `pip-audit` step in CI (warn, don't fail, tonight).
Write what you did and what's left (server items for WS4) into A-01 as a "Status" section.

## 7. Back-test harness skeleton (T-035) (≈1 h)
- Harness that takes condition-tagged tests (fixtures only tonight) and the real-range ratio model, runs leave-one-out, and reports median absolute % error overall / per body type / per brand + the 10 worst.
- Output in the same `qa.json` (section `backtest`). No real data needed tonight.

## If there is still time
- T-019 minimal bidi taxonomy rows (EN) + validation, so T-020 can start.
- A dark theme via CSS variables (light "Day trip", dark "Night drive"); use neutral placeholder colours, the UX chat will supply tokens.
- axe accessibility check in Playwright on Explore, a model page and /learn; fix criticals.
- Performance: Explore first load budget check (spec §13), report in `audits/`.

## Bottomless backlog (keep going until the session ends)
Take these in order. Refresh MORNING.md and push after each one, so stopping at any moment leaves a clean state.
1. Glossary sweep: every column, filter and badge has a glossary term in EN + NL; list missing ones as fixed.
2. Explore polish: cards view on phones (360 px), sticky header row, keyboard navigation, empty states with a reason ("no cars match: remove 'V2G' filter").
3. Compare: share link, print view check, "differences only" toggle.
4. Rankings: add "best used EV under €15k / €20k / €25k per country" pages from release data (only cars with sourced prices; hide if fewer than 5).
5. Seed coverage: list the top-40 used models missing generations, packs or platforms in `data/review/coverage-gaps.md` with what source could fill each (no values from memory).
6. Q-021 proposal: implement source-scoped aliases (`rdw_aliases`, `eea_aliases`) behind a flag with tests, and show the match-rate change in MORNING.md.
7. Q-019 option (a): attach EEA generation-level values as corroboration only (never as a value) behind a flag; report how many rows reach `sourced`.
8. Test depth: raise pipeline and web unit-test coverage on the merge, derive and release modules; Playwright flows for compare tray persistence and display levels.
9. Docs: `apps/web/README.md`, `pipeline/README.md` and `infra/README.md` brought up to date for a new builder (how to run, test, release).
10. Write task files `tasks/T-044…` for anything you found that should be done next, with acceptance criteria, and add them under a "Proposed by overnight" heading on BOARD.md.

## Finish (≈30 min, always do this; also do a light version every ~2 hours)
1. MORNING.md: a section "Addenda 4 + 5" with a table: item · done / partial / skipped · commit · notes; new QUESTIONS (numbered after your last Q); a 5-line retro (what slowed you, what Menno had to do by hand, which rule would have prevented it).
2. Push, open or refresh the draft PR to `main`, CI green.
3. Append one line to `workstreams/WS0/INBOX.md`: "Overnight done, PR #x, MORNING.md ready."
