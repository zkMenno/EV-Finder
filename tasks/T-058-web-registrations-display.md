# T-058 Web registrations display
Role: WS2   Lane: apps/web   Wave: proposed by overnight 1
Status: review (web builder, 2026-11-15)

## Goal
Show model-level counts (shared years) clearly and fix the duplicate React key when a row has two RDW entries in the same period (Q-066).

## Acceptance criteria
- [x] 'all <model> generations' wording for model-level counts
- [x] No duplicate keys; e2e covers a shared-year model
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
- **Key fix (Q-066 point 1):** `registrationItemKey()` in `apps/web/src/lib/registrations.ts` = kind-period-level-source (missing level = generation). `Registrations.tsx` uses it, and each `<li>` carries `data-kind/-period/-level/-source` for tests.
- **Order:** `registrationsFor()` now puts the generation-level count before the model-level one when kind, period and source tie.
- **Wording (Q-066 point 2 + acceptance):** `reg.modelLevel` EN "generation unknown, shown on all {model} generations", NL "generatie onbekend, getoond bij alle generaties {model}". Kept source-neutral (not "shared year") because a model-level count from another source (e.g. UK DfT) also means "generation unknown". DE/FR/ES/IT have no `reg.*` keys and fall back to EN, as before. Numbers still go through `<Num>` with `registrations.<CC>` provenance; never summed.
- **Tests:** 3 new Vitest cases in `src/lib/registrations.test.ts` (order, unique keys, compare key tells levels apart; fixture shaped like Zoe ph1 in release 1). New `e2e/registrations.spec.ts` (Zoe ph1 + ph2 generation pages, a Niro EV DE variant page, Dutch wording); no fixed counts, so a rebuilt release doesn't break it.
- **Checks (2026-11-15):** lint, typecheck, 284 unit tests, `APP_URL=https://ev.example.com pnpm build` (first try hit "release changed during the build", second passed), e2e 79 passed / 1 skipped (TRIP_FIT=0 case), budget OK: Explore 156.2 KB gzip, catalogue 99.1 KB gzip.
- Note: the React duplicate-key warning only shows in dev, so the unit test on `registrationItemKey` is the real guard; e2e checks both lines render once each.

## Review
