# T-097 Hero Nerd table: show each factor's value with its unit
Role: WS2   Lane: apps/web   Wave: launch polish
Status: todo

## Goal
A buyer reading the Nerd score table understands every value: "387 km in 20 min", not "1.161,6".

## Acceptance criteria
- [ ] The Value column shows the car's own figure in buyer units (the raw field value with its unit via `Num`/format), not the factor's scaled internal value (`raw × scale`, e.g. km per 20 min × 3 = km/h)
- [ ] Units metric and translated in all 6 languages; unknown stays "nog onbekend"
- [ ] e2e: the first card's fast-charge row shows "km" and matches the card's own fast-charge text

## Inputs
Found by the fresh review of PR #50 (2026-11-17). `factorScore()` in src/lib/shortlist.ts returns `value` after `scale`; RuleFactor has `field` and `scale`.

## Out of scope
Changing the scores or rules.

## Handoff notes

## Review
