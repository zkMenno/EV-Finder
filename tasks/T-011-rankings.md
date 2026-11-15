# T-011 Rankings
Role: builder   Lane: apps/web (top)   Wave: 3
Status: review (builder, overnight 2026-11-15)

## Goal
Three ranking lists.

## Acceptance criteria
- [x] Longest real range under €30k new
- [x] Fastest DC km/10 min (built as km in 20 min per Decision 009, see Q-031)
- [x] Most available used EVs in NL
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
- `/[country]/top` (index) and `/[country]/top/[list]` for `longest-real-range-under-30k`, `fastest-dc` and `most-available-nl`. Unknown list → 404. Logic: `src/lib/rankings.ts` (pure, tested). Table: `src/components/RankingTable.tsx` (caption, `scope` on headers, rank column, car as the row header).
- Every list has a method note (metric, sources, estimate status) and an "N of M values are estimates" / "All values are estimates" line computed from provenance.
- Longest real range under €30k: `real_range_km`, only rows with `price_new[country]` in the country's currency and below `PRICE_THRESHOLD` (EUR 30,000 / GBP 26,000, Q-032). Rows without a price are left out, never guessed. Release 1 has prices for 7 DE variants only, all over €30k, so the list shows "No priced models yet for this country" everywhere. The fixture has rows that pass (tested).
- Fastest DC: `dc_km_per_20min` per Decision 009, not peak kW. The T-011 acceptance line says km/10 min (Q-031). Top 50. All 99 values in release 1 are estimates (generic curve), and the page says so.
- Most available in NL: one row per generation (`registered_count_nl` is generation-level), linking to the generation page. Source: RDW (CC0). The note says it is a proxy for used supply, not a listings count.
- Ties share a rank (1, 1, 3). Range ties are broken by lower price.

Checks: `pnpm --filter @ev/web lint`, `typecheck`, `test` (15 files, 110 tests) and `build` all pass; `pnpm e2e` smoke (2 tests) passes. Pages checked by hand against release 1 with `next start` (200s for known ids; 404 for an unknown country, model, generation, variant or list).

## Review

**Reviewer, 2026-11-15 (fresh agent). Verdict: pass.**

- [x] Three lists with method notes, honest "N of M values are estimates" lines computed from provenance; values through `Num` (`top/[list]/page.tsx:44,99`); rank is a position, not a Fact.
- [x] Fastest DC uses `dc_km_per_20min` (Decision 009) and only rows with a positive value (`lib/rankings.ts:57`), so cars without DC data are never ranked. All 99 release-1 values are estimates and the page says so.
- [x] Under-€30k list leaves unpriced rows out and shows "No priced models yet" on release 1 rather than guessing.
- [x] Table semantics: caption, `scope`, car as row header; scroll region is focusable with a label.
- [x] No foreign requests on `/nl/top` and `/nl/top/fastest-dc` (new e2e).

Note (no change needed now): Q-031 (km/10 min in the acceptance line vs km/20 min built) is still open.
