# T-159 Elroq hold off, motor-count evidence for ties, trim-line version rule, manual terms wording
Role: builder   Lane: pipeline/, data/sources.yaml (WS1); data/manual Elroq hold (WS3 file, flag it)   Wave: launch
Status: todo (start after T-153 merges: #185, #186)

## Goal
The last T-154 asks are closed: the Elroq is matched by its cited power instead of a hold, version ties split by motor count, and a new entry trim no longer marks higher trims as "older".

## Acceptance criteria
- [ ] **Elroq hold off:** remove the source hold on OpenEV Elroq "Base" that T-154 added (#183); with T-153's "cited power wins" it joins the seed Elroq 85 and its wrong 150 kW stays withheld. Show the before / after rows.
- [ ] **Motor-count / drivetrain evidence for ties:** extend T-153's split evidence so these ties resolve (or stay tied with a reason in the queue): Kia EV3 LR vs AWD, EV6 facelift RWD vs AWD, MINI Countryman E vs SE ALL4, Hyundai Inster 42 vs 49 kWh. Repro (G-51): `ev variants propose` tie count for these four before / after.
- [ ] **Decision 088:** `version_flags` compares the same trim line (same model, same drivetrain, power within ±15 %). Back-test (`backtest_rules.py`) at or above today; the R-32 pairs (G6, EV6, IONIQ 5) keep their flags; e-tron GT 2024 S / RS / RS performance lose `older-version`. Approvals for moved scores in their own gate PR, scoped to a release not yet built (G-54).
- [ ] **Wording:** `data/sources.yaml` `manual` terms say Decision 087 (any number of single facts per car; never a whole table, range table or price list) instead of "one figure per car per document".
- [ ] Same-data rebuild diff (G-43), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
WS0 INBOX 2026-11-19 09:15 UTC (batch: catalogue T-154, asks 1–3); Decision 038, 087, 088; T-153 and T-154 Handoff notes.

## Out of scope
New seed variants (T-160). `ev verify` tool changes (T-158).

## Handoff notes

## Review
