# T-015 Tests smoke
Role: coordinator   Lane: apps/web/e2e   Wave: 4
Status: merged (PR #1); fresh review via QA A-35; earlier note: reviewer agent, 2026-11-15

## Goal
All tests green; Playwright smoke test.

## Acceptance criteria
- [x] Explore → filter → compare 2 → reload → tray still there
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
**Reviewer, 2026-11-15.** All five checks run separately from the repo root, all green:

| Command | Result |
|---|---|
| `pnpm --filter @ev/web lint` | pass |
| `pnpm --filter @ev/web typecheck` | pass |
| `pnpm --filter @ev/web test` | pass: 17 files, 125 tests (was 16/123; +`src/i18n/nl-coverage.test.ts`) |
| `pnpm --filter @ev/web build` | pass (1,552 static params generated; all routes dynamic) |
| `pnpm --filter @ev/web e2e` | pass: 10 tests, of which 1 is an expected failure (`test.fail()`) documenting a bug |

Smoke test confirmed: `e2e/smoke.spec.ts` already does load Explore → min range 300 → 2 to compare → reload → filter and tray (2) still there → navigate → tray still there, and fails on any foreign request.

Extended in `e2e/review.spec.ts` (fixture data, no network):
- every page talks only to our own origin (Explore with popover, variant, generation, model, compare, learn, top, top/fastest-dc, /uk);
- tray survives a country switch, tray → `/de/compare?ids=a,b` shows both cars, reload keeps the tray;
- Explore URL state (filters, sort, view, level) round-trips through hydration and reload;
- keyboard: skip link first with a 3 px outline, sort with Enter (`aria-sort`), add with Space, remove from tray with Enter;
- Explore shows "—" for DC and 400 V behaviour on a car without DC data (Zoe R240);
- `test.fail()`: spec sheets/compare should not show 400 V behaviour without DC data. This is the T-009/T-010 bug; remove `test.fail()` once fixed.

Gap: CI does not run `e2e` (see A-02 finding 1).

## Review
