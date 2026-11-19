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
**Batch: data T-153 (2026-11-19), https://claude.ai/code/session_01JuyZEX99QgTw4AD6jgjZaL.** Part 1 = #185 (checks), part 2 = #186 (split, cited power, status.yaml).
- **Split evidence** lives in `pipeline/ev_pipeline/match/tgk_split.yaml` (per seed variant: `type_codes`, `power_30min_kw`, `top_speed_kmh`, `motors: 2`, each with a `basis`). Applied in `tgk_pick` after the year check. A candidate is only ruled out by its own listed value; all out → review. Default order kept (type code, 30-min, top speed, then motors). New car = new row; the test fails on an id that is neither a seed variant nor in its `BUILT_ONLY` list.
- **Motors is opt-in, not general:** A-05 F12 (I-Pace) shows a dual-motor version can carry one 30-min row, so only `motors: 2` rows (ID.4 GTX) are ruled out by a stated 30-min power.
- **Model Y needed type codes too**: top speed alone left the 57.5 kWh RWD fitting the Y5CD energy (wide net band 1.0–1.5). Rows for LR / Performance / RWD and OpenEV's LR RWD (`tesla-model-y-gen1-long-range-rwd`, no seed row).
- **Cited power wins:** needs alias + cited (`cited:`) power + battery evidence that agrees; the record's `power_kw` is withheld (validation.csv). No effect on today's data; it works for the Elroq 85 once T-154 (#183) adds that row (scratch test in the #186 body). Reviewer nit, open: also require agreement with a cited WLTP where there is one (Elroq RS 250 kW / 77 kWh aliased by mistake would also join; visible in validation.csv).
- **Mark done:** 234 `have` groups (task said 214; the queue was regenerated since) → `data/review/status.yaml` (new).
- **Checks:** G-48 seed vs built (baseline release N-1, keyed on row + kind; new ones fail verify), G-49 exclusive staging lock (refresh refuses a second refresh, verify refuses while held and re-checks after the rebuild), G-50 validator warning (29 variants today).
- **Follow-ups (not done here):** (1) WS3: 2025-26 ZKXZ (57 kW, 100 kW motor) e-208 / Corsa / e-2008 versions now go to review because the 50 kWh rows end 2023: extend or split those rows. (2) WS3: `tesla-model-s-facelift-75d` seed `rwd` vs built `awd` (row is "75 / 75D"), the one G-48 hit. (3) WS1: Model Y gen1 Performance still shows WLTP 507 km, the 2021 LR figure, from the RDW model-year aggregate `TESLA|MODEL Y|2021`; TGK Performance versions say 514–528. (4) Review nits #185: refused `ev refresh` prints verify's wording; a short refresh inside a verify rebuild goes unseen (staging is symlinked); a narrow race on stale-lock takeover. (5) The propose fingerprint (cycle × motors × energy) still groups Model Y LR/Perf and e-208 50/51 as `several` though each version is placed right; adding the split fields to the fingerprint would turn them `have`.

## Review
