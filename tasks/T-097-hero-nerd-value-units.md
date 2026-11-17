# T-097 Hero Nerd table: show each factor's value with its unit
Role: WS2   Lane: apps/web   Wave: launch polish
Status: review (WS2, 2026-11-17; branch t-097-hero-nerd-value-units)

## Goal
A buyer reading the Nerd score table understands every value: "387 km in 20 min", not "1.161,6".

## Acceptance criteria
- [x] The Value column shows the car's own figure in buyer units (the raw field value with its unit via `Num`/format), not the factor's scaled internal value (`raw × scale`, e.g. km per 20 min × 3 = km/h)
- [x] Units metric and translated in all 6 languages; unknown stays "nog onbekend"
- [x] e2e: the first card's fast-charge row shows "km" and matches the card's own fast-charge text

## Inputs
Found by the fresh review of PR #50 (2026-11-17). `factorScore()` in src/lib/shortlist.ts returns `value` after `scale`; RuleFactor has `field` and `scale`.

## Out of scope
Changing the scores or rules.

## Handoff notes
- `FactorScore` gains `field` + `raw` (the car's figure before `scale`); `value` is unchanged, so scoring and backtest parity don't move.
- `src/lib/nerd-value.ts` formats the Value cell: unit per numeric rule field (`hero.nerd.unit.*`, 6 languages), length in metres like the card's why line, heat pump / cooling / yes-no as words (`hero.nerd.val.*`), unknown = `hero.card.notKnown`.
- The Value cell may now wrap at the unit's spaces on a phone; numbers never split. The 360 px e2e measures each number instead of each cell (the old per-cell check failed by 25 px once units were added).
- Checked: vitest 48 files / 361 tests, tsc, eslint, test build, hero e2e 13/13, axe hero 7/7, NL/FR/DE Nerd table at 360 px with 0 px overflow.

## Review

Reviewer: fresh agent (2026-11-17), PR #68 head 6f9c75a: R0–R3, D8, D10: pass
- Round 1 (7202907): R0 fail, de/de + be/de Nerd table clipped 16 px on CI (system font wider than dev) → fixed: words may break, numbers in nowrap spans, test adds a 12 % wider pass.
- Round 2 (e5d2c33): pass, should-fix: Score/Weight headers broke mid-word ("Poi/ds") → fixed: one "Points 0–1 × Weight" column.
- Round 3 (6f9c75a): CI green; 6 routes × 360/1280 × light/dark: axe 0 in 24 runs, 0/220 numbers split, 0 px clipped; no header mid-word breaks (normal + 12 %); Explore 169.9 KB gzip. Main merged in afterwards (1857c21, docs-only change), CI re-run before merge.

