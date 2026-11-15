# T-061 Web: known issues, EPA range, generation-year badges, charging charts
Role: builder   Lane: apps/web   Wave: 5 (MORNING.md wave 5 item 6)
Status: review (web builder, 2026-11-15)

## Goal
Show the new release data from T-059 (known issues, EPA range, Wikidata year checks, charging stats) in the web app, honestly labelled, in EN + NL, at all three detail levels and in both themes.

## Acceptance criteria
- [x] Generation pages show known issues per first-registration year: top defect codes as "N per 100 sampled cars" next to "all EVs of that year: M per 100". A rate is only ever compared with its own year (Q-078).
- [x] Cohorts flagged `few_reports` show "not enough inspections yet" and no rates. Generations without data say so.
- [x] RDW's Dutch labels are shown as published (`lang="nl"`), with a plain-language note. Source wording follows the Q-037 interim line "Dutch vehicle register (RDW open data, CC0)", here and in the About credits (`rdw-defects`).
- [x] Simple shows the top 3 codes, Detailed the top 5, Nerd adds codes, articles, sample sizes, the rate basis and the sample rule.
- [x] "EPA range (US test)" is its own spec row on variant and compare pages, never mixed with WLTP. It is not in the generation diff, and Explore keeps WLTP (EPA is not shipped to the browser).
- [x] Year badge: "years checked against Wikidata" / "Wikidata disagrees" (details at Nerd) / the existing "years not yet checked", from one shared function on the model, generation and variant pages.
- [x] `/{country}/{lang}/charging`: public charging points over time and by power band for DE (BNetzA) and UK (DfT), one chart per definition (Decision 012). Each chart has a data-table fallback, source, licence and period, and follows the dark theme. Other countries show "no open data yet". Linked from the charging links block and listed in the sitemap.
- [x] Every number goes through `Num` with provenance. All labels exist in EN + NL. Explore first-load JS stays < 200 KB.
- [x] Unit tests + e2e (with axe on the new pages, both themes). All checks are green.

## Inputs
DECISIONS 012, 022; QUESTIONS Q-037, Q-078, Q-080; schema defs KnownIssues / KnownIssueCohort, GenerationYearsCorroboration, PublishedVariant.epa_range_km, ChargingStat / ChargingStatsRelease; `data/releases/1/catalogue.json`, `data/releases/1/charging_stats.json`.

## Out of scope
Regional charging figures, installed kW, points per 100k people (all in the release, not charted yet). Cross-country comparison (EAFO/IEA only, Decision 012). Taxonomy and glossary edits (data lane).

## Handoff notes
**What was built**
- Data access: `src/lib/catalogue.ts` gains `knownIssues()` and `chargingStats()`. The second reads `charging_stats.json` next to the release's catalogue.json, lazily. A missing file means null; a broken file fails the build (same rule as the catalogue).
- Known issues: view logic in `src/lib/known-issues.ts` (pure, tested), UI in `app/[country]/[lang]/ev/_components/KnownIssues.tsx`, placed on the generation page after the listings block.
- Display levels on static pages: `src/lib/use-level.ts` (`?level=` wins, then the level Explore remembered, else detailed; `useSyncExternalStore`, server snapshot "detailed"). `src/components/LevelGate.tsx` has `LevelGate` (shows children at given levels) and `LevelNum` (a `Num` that follows the level). Reusable on any static page.
- EPA: one line in `SPEC_FIELDS` (`src/lib/spec-diff.ts`) plus the `field.epa_range_km` label.
- Year badge: `yearsStatus()` in `ev/_lib/data.ts` (on `GenerationView.years`) and `ev/_components/YearsBadge.tsx`, used by the model, generation and variant pages.
- Charging: `src/lib/charging-stats.ts` (blocks per metric × definition, whole-country only, notes, axis helpers), `src/components/LineChart.tsx` (hand-written SVG server component, colours from `--chart-1…4`, dash patterns plus a legend for colour-blind safety, role="img" with a text summary), and page `app/[country]/[lang]/charging/page.tsx`. `ChargingLinks` takes `statsHref`, passed on Explore, model, generation, variant and learn pages. Source notes (e.g. the UK July 2026 clean-up) are listed once per chart at Detailed/Nerd, not on every number.
- i18n: new keys `gen.ki.*`, `years.wikidata.*`, `years.check.*`, `field.epa_range_km`, `charging.stats.*` (EN + NL; all server-only prefixes).
- Tests: `known-issues.test.ts`, `charging-stats.test.ts`, `use-level.test.ts`, `explore-data.test.ts`, plus additions to `spec-diff.test.ts` and `ev/_lib/data.test.ts`. e2e: `e2e/known-issues-charging.spec.ts`, and 4 new pages in `e2e/a11y.spec.ts` (known issues + years at Nerd, DE charging with the table open, UK at Nerd, FR "no data"), in both themes.

**Checks (from root, 2026-11-15):** lint ✓, typecheck ✓, test ✓ (253), build ✓, e2e ✓ (72 passed, 1 skipped as before), `node apps/web/scripts/budget.mjs` ✓: Explore 156.3 KB gzip (unchanged), client catalogue 94.3 KB gzip (the release grew meanwhile). The charging page adds no client JS beyond the shared `Num`/`LevelGate`.

**Missing glossary term ids** (the ⓘ appears automatically once the data lane adds them to `data/taxonomy/glossary_terms.yaml`):
- `known-issues`: what the known-issues section is
- `apk`: the Dutch periodic roadworthiness test
- `epa-range`: the US EPA range test vs WLTP
- (suggested) `first-registration-year`, `defect-rate`, `power-band`, `wikidata-years`: no code references them yet. They would go on the cohort heading, the per-100 columns, the band chart and the year badge.

**Judgement calls:** logged in Q-088 ("per 100 sampled cars" instead of "inspected", the verdict rule within 20 %, Dutch labels, level split, badge precedence, the charging page instead of the Explore footer).

**Surprises / follow-ups**
- The schema gained `Catalogue.used_prices` (median/p25/p75/period) while I worked. The web's own `UsedPriceBand` (typical/low/high, Q-085) no longer matched, which broke typecheck. Minimal fix: `usedPrices()` now reads the field as `unknown` and keeps its runtime guard. With today's schema shape the guard drops every band. **Align `src/lib/used-rankings.ts` with the schema `UsedPriceBand` in a follow-up task** (coordinator to schedule).
- The DE page in `de` falls back to the EN strings (only EN + NL are translated, as per lane rule 9).
- The first build of the session failed once, most likely while the pipeline was rewriting the release; the rebuild was green.

## Review
