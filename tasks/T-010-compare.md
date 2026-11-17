# T-010 Compare
Role: builder   Lane: apps/web (compare)   Wave: 3
Status: merged (PR #1); fresh review via QA A-35; earlier note: builder, overnight 2026-11-15

## Goal
Compare page: side by side, highlight differences, share URL, print view.

## Acceptance criteria
- [x] ?ids= drives the page
- [x] Differences highlighted
- [x] Print stylesheet
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
- `/[country]/compare?ids=a,b,c,d` (`app/[country]/compare/page.tsx`, server). `parseCompareIds` (`_lib/ids.ts`) trims, de-duplicates, drops ids that aren't id-shaped and caps at 4 (`COMPARE_MAX`). It reads exactly what `compareHref()` in the tray writes (tested). Unknown ids are listed in a status note. With no ids it shows an empty state linking to Explore.
- Table: `src/components/CompareTable.tsx`. Same field list and grouping as the variant page, plus the new price for the page's country and the RDW count. Every number goes through Num. Rows where all cars lack a value are dropped.
- Difference detection: `differingCells()` in `src/lib/spec-diff.ts`. All equal: no highlight. A clear majority: only the odd ones out are highlighted. No clear majority (e.g. 2 cars): every cell. A missing value counts as different. Highlight = amber background + ◆ + sr-only "differs" (not colour alone).
- "Only show differences" is a link toggling `&diff=1`, so the state lives in the URL and it works without JS. Each column has a "Remove" link that rewrites the URL.
- Share: `_components/CompareActions.tsx` uses `navigator.clipboard.writeText`, falls back to a textarea + `execCommand('copy')`, and if both fail shows a selectable read-only input. Status is announced via `role=status`. A Print button calls `window.print()`.
- Print: `compare/print.css`, scoped with `body:has([data-compare-page])`. It hides header/nav/footer/tray/skip link/ⓘ/popovers and prints black on white in A4 landscape with `table-layout: fixed`, so 4 columns fit. A print-only line shows the release number.
- `robots: noindex` on compare pages (endless id combinations).

Checks: `pnpm --filter @ev/web lint`, `typecheck`, `test` (15 files, 110 tests) and `build` all pass; `pnpm e2e` smoke (2 tests) passes. Pages checked by hand against release 1 with `next start` (200s for known ids; 404 for an unknown country, model, generation, variant or list).

## Review

**Reviewer, 2026-11-15 (fresh agent). Verdict: changes needed (shared DC bug from T-009), otherwise pass.**

- [x] `?ids=` drives the page; the tray's `compareHref()` output round-trips (unit) and the tray → compare link works from another country (`/de/compare?ids=a,b`, new e2e). Reload of the compare page keeps the tray.
- [x] Differences highlighted with amber + ◆ + sr-only "differs" (not colour alone); slate-900 on amber-50 = 17:1.
- [x] Print stylesheet hides chrome; `noindex`.
- [x] Every number through `Num` (`CompareTable` → `SpecValue`). Malformed ids (`?ids=<script>`) render a normal page, nothing reflected unescaped.
- [x] No foreign requests (new e2e).

Changes needed:
1. Same as T-009 #1: for a car without DC data the compare table shows "On 400 V chargers: native/booster" and "Power on 400 V chargers: 50 kW" (checked on release 1 with `hyundai-ioniq-6-gen1-53kwh-rwd`; fixture: `renault-zoe-x10-r240`). It also makes such a car "differ" in that row. Fix in the shared helper; the `test.fail()` e2e covers the compare page.
