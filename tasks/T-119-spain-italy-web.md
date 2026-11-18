# T-119 Serve /es/es and /it/it
Role: builder   Lane: WS2: apps/web/ (routing, country picker)   Wave: launch fixes (A-35)
Status: merged (PR #77)

## Goal
Spain and Italy are selectable and served in their own language (Decision 066).

## Acceptance criteria
- [ ] `countries.generated.json` includes es and it; routes /es/es and /it/it build; the country picker lists them; hreflang + sitemap include them
- [ ] Spanish and Italian appear only for Spain and Italy (no /nl/es style routes)
- [ ] Hero walk for ES and IT at two budgets; axe clean
- [ ] Depends on T-118 config and T-117 strings
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 066; audits/A-35 B5

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- **Served.** `scripts/listings.mjs` `COUNTRIES` now has es/it (T-118's `PENDING_COUNTRIES` step removed); `src/config/countries.ts` adds `es` (España, ES, EUR) and `it` (Italia, IT, EUR); languages come from config/countries/es.yaml + it.yaml (T-118, on main), so `countries.generated.json` serves es → [es, en], it → [it, en]. Listings and charging-link JSONs regenerated (2 + 4 links each). Everything else (static params, hreflang `es-ES` / `it-IT` / `en-ES` / `en-IT`, sitemap, header country picker, hero country step, Accept-Language banner, redirects) already follows `servedPairs()`; no other code change needed. Locale es-ES / it-IT was already in format.ts; schema `Country` has ES/IT since #71.
- **Spanish and Italian only for Spain and Italy:** /nl/es, /de/it, /uk/es, /es/it, /it/es → 308 to the country default (unit + e2e).
- **Reversible default (trip check):** the PROVISIONAL town fixture (hand-typed temperatures) has no ES/IT towns, and I didn't type more by hand. `hasTowns(country)` switches the trip check off for a country without towns (it's parked and off in production anyway), instead of falling back to another country's climate. ES/IT get it once WS1 ships sourced GeoNames + Meteostat towns. Test-change in trip-model.test.ts.
- **Tests.** Unit: ES/IT served pairs, no Spanish/Italian elsewhere, hreflang + sitemap (site-paths.test.ts); listings test now checks es/it are served. e2e: new `e2e/es-it.spec.ts` (redirects, picker, hreflang, sitemap, hero walk ES/IT × €20k/€40k at 360 px); smoke hreflang count 12 → 16 (15 served pairs + x-default, Test-change); hero.spec 360 px Nerd routes + es/es, it/it; axe `hero-es`, `hero-it-360`. Feature map: new flow `country-spain-italy`.
- **Build cost:** 7,005 static pages (was 5,137; +4 served pairs).
- **Open:** ES/IT used prices and list prices are thin (T-118: 0 ES list prices, 10 IT), so most ES/IT cards show "price not known yet" until release 2. When #69 (T-114) merges, the two new axe hero entries need the same `HAS_SCORES` readiness switch as the other hero entries (no-scores state on release 1).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->

WS0 subagent, 2026-11-17, df7baa5 + ab49c12: R0–R3, D6, D8–D10, D13 pass; /es/es and /it/it served, es-it e2e on release 2. **A-35 B5 (routes) fixed.**

Reviewed by QA, 2026-11-17 (A-36): pass (es/es, it/it, es/en, it/en answer 200; es-it e2e passes). English-only routing is T-137.
