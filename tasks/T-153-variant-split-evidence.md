# T-153 Split variants that share a battery, let a cited power win, three retro checks
Role: builder   Lane: pipeline/ (WS1); data/seed/validate_variants.py one-line cross-lane (WS3 file, flag it)   Wave: launch
Status: doing (batch: data T-153, https://claude.ai/code/session_01JuyZEX99QgTw4AD6jgjZaL, 2026-11-19)

## Goal
Source records for versions that share a battery land on the right variant, a power figure cited from the maker beats a wrong one from OpenEV, and three checks catch what the 18 Nov batches found by hand.

## Acceptance criteria
- [ ] **Split evidence (biggest win, ~1.2M EU cars):** the matcher can tell apart variants with the same pack using (order is the builder's call, WS0 default shown): TGK type code (e.g. Model Y `ZKXZ` / `ZKWZ`), 30-min power (Stellantis 57 vs 62 kW = 100 vs 115 kW), top speed (Model Y LR 217 vs Performance 250 km/h), stated single vs dual motor (ID.4 Pro vs GTX). Each rule is a config/data table, not hard-coded per model. Targets: Model Y gen1, ID.4, e-208, Corsa-e, e-2008, Mokka-e; the 2021 Model Y LR versions (Y5CD, 507 km) leave the Performance row.
- [ ] **Cited power wins:** when a seed variant has a power figure cited from a maker document (Decision 068 / 087), the power gate compares source records against that figure, so OpenEV Elroq "Base" (77 kWh, wrong 150 kW) can join the seed Elroq 85 that cites Škoda's 210 kW. The wrong OpenEV power is withheld, not published.
- [ ] **Mark done:** the 214 `have` groups in data/review/variant-candidates.csv are marked done in data/review/status.yaml (with a note naming this task).
- [ ] **Check 1 (G-48):** `ev verify` flags a seed variant whose built drivetrain differs from its seed, or whose built WLTP is more than 10 % off its own cited WLTP (the reviewer caught Kia EV3 twice by hand).
- [ ] **Check 2 (G-49):** `ev verify` refuses to run while `ev refresh` holds the staging directory (lock file), with a plain message.
- [ ] **Check 3 (G-50):** `data/seed/validate_variants.py` warns when a seed `cited:` block uses a source whose status is `blocked` (those values never ship; move them to data/manual). Cross-lane one-liner, flagged in the PR and the INBOX line.
- [ ] Same-data rebuild diff in the PR body (G-43): records that move, per model; 0 unintended moves; queue numbers before / after (no-variant, tie, several EU cars).
- [ ] Tests with fixtures for every rule; `ev verify --base main` evidence in the PR body.

## Inputs
WS0 INBOX 2026-11-18 16:14 UTC (batch: catalogue, retro 4) and 18:53 UTC (batch: variant queue, asks 1–2, retro 4); Decision 068, 087; tasks/T-148 Handoff notes; pipeline/ev_pipeline/match/matcher.py (`power_close`, `_power_pool`); docs/process/rules.md G-43, G-48–G-50.

## Out of scope
New seed variants (T-154, WS3). OpenEV `markets` filter (parked). Schema changes: if a field is missing (e.g. type code on a variant), ask WS0 in the INBOX with the exact field.

## Handoff notes

## Review
