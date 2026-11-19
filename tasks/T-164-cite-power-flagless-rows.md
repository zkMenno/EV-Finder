# T-164 Cite power for the rows that lose version flags only for missing power
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: todo (start after T-163's "cited values reach the release" merges)

## Goal
The rows Decision 088 can't compare only because `power_kw` is missing get a cited maker power, so their newest / older flags come back.

## Acceptance criteria
- [ ] After T-163, re-run the list: rows that still have no `power_kw` from T-161's 22 (Tesla first, 12 rows: Model 3 LR / LR 2021 / Performance / Performance 2021 / SR+ / SR+ LFP, Model S facelift 100D / 75D / P100D, Model S gen1 85 / 85D-90D, Model Y RWD; then Mach-E ER AWD / SR RWD, Enyaq 80x RS, ID.3 Pro, e-tron GE S, Spring 65, EV3 AWD, EV6 84 AWD, Mokka 54, ID.7 GTX).
- [ ] Cite each from a maker document (Decision 087); approvals for moved scores in their own gate PR (G-54).
- [ ] Plain `ev verify` (against the latest published release, which measures the approvals): the flags come back (count before / after).

## Inputs
WS0 INBOX 2026-11-19 15:05 UTC (batch: data T-161, WS3 ask); T-161 Handoff notes (the 22 rows).

## Out of scope
Code changes (T-163).

## Handoff notes

## Review
