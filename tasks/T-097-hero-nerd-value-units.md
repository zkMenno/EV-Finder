# T-097 Hero Nerd table: show each factor's value with its unit
Role: WS2   Lane: apps/web   Wave: launch polish
Status: done (WS2, 2026-11-17; branch t-097-hero-nerd-value-units)

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
Reviewer: fresh agent (2026-11-17), head 76ebe52 (first pass on 2ea43ab): R0–R3, D6, D8, D10: pass
- R0: CI green on 76ebe52 and 2ea43ab (e2e, web, build web, audit, schema, pipeline). R1: 0 conflict markers. R3: no gate files; the 360 px test measures each number, not each cell (numbers still must not split).
- Local on 76ebe52: vitest 361/361, tsc, eslint, build green; hero.spec 18/18; a11y.spec 32/32.
- D8: NL/EN/DE/FR at 360 + 1280 px, light + dark; axe 0 violations in 40 runs; 0 numbers split, 0 px clipped, 0 px overflow; contrast.py all AA.
- Value column = the card's own figure: dc-speed matches the why line on 3/3 cards in NL, EN, DE, FR.
- D6: 15 keys × 6 languages. D10: Explore first load 169.8 KB gzip < 200 KB.
- should-fix: the "6 languages" 360 px test opened /nl/{lang}; /nl/de, /nl/fr 308 to /nl/nl, so only NL + EN were tested → fixed in fix/hero-nerd-360-routes (served routes + redirect check).
- nit: "11,7 kWh/100 km" wraps to 3 lines at 360 px, readable. pre-existing: ES/IT not served (T-119).
- Merged by Menno as #56 (dabb31d), 2026-11-17 10:28 UTC.
