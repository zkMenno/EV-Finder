# T-146 Variant candidate review queue, biggest EU registrations first
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: doing (batch: variant queue, https://claude.ai/code/session_01JuyZEXkdc6m6bZgzVV874S, 2026-11-18)

## Goal
Work `data/review/variant-candidates.csv` (T-073) from the biggest EU registrations down: fix seed rows that make the matcher tie or miss, add cited variants for generations that have none, and record a decision for each group worked.

## Acceptance criteria
- [ ] Each group worked has an outcome: seed fix (PR), new cited variant (PR), or a `done` / `wont-fix` status with the reason (status.yaml, WS1 file: one INBOX line).
- [ ] No value from memory: every new or changed spec is cited (maker doc, type approval via RDW, or OpenEV) or left out.
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass for each PR; matching regression run (0 moves for already matched records, except intended ones).
- [ ] Coverage line (variant-coverage.json) before / after in each PR.

## Inputs
WS0 INBOX 2026-11-18 16:14 UTC "batch: catalogue" (item 6 triage); pipeline/README.md (variant-candidates.csv); ev_pipeline/variants/propose.py; workstreams/WS3/START.md.

## Out of scope
Matcher changes (WS1: asks go to INBOX). Prices. Photos.

## Handoff notes
**PR 1 (seed, 2026-11-18):** first variants for 5 "no-variant" generations, biggest EU first: Mokka-e 50 / 54 kWh, Twingo Electric 22 kWh, e-up! 18.7 / 32.3 kWh, EV3 Standard, Avenger 54 kWh. Battery + power `cited:` from maker pages (matching evidence; maker-docs values stay internal, the release takes figures from TGK / RDW / KilowattApp / ADEME as before). Links: existing platform rows, new pack rows with only the maker's capacity, new platform `vw-up-family`.
- Left out on purpose: **EV3 Long Range** (the 2026 two-motor EV3, TGK 572 km + EPA AWD records, would land on it by battery and flip it to AWD; add an AWD row when a Kia page gives its figures). **Mokka GSE** (2025+, 207 kW) not split.
- Known ties that go to review (nothing misplaced): Mokka 2022+ 100 kW vs 115 kW versions (both packs fit, years overlap); e-up! 2018-2020 versions without a range.
- Queue after PR 1 (fresh staging 2026-11-18): no-variant EU cars 891,029 -> 573,448; % EU registrations on groups we have 63.8 -> 66.7.

**Top tie / several groups (not seed-fixable, WS1 ask in INBOX):** the matcher can't tell apart variants that share a pack, because TGK evidence ignores 30-minute power, top speed and the TGK model code. Seen on: Model Y gen1 LR AWD vs Performance (217 vs 250 km/h; the 2021 Y5CD 507 km LR versions are placed on Performance), ID.4 Pro vs GTX (30-min power stated = one motor), e-208 / Corsa / e-2008 / Mokka 100 kW vs 115 kW (30-min 57 vs 62 kW; type codes ZKXZ vs ZKWZ; 2024-26 ZKXZ e-208 versions placed on the 51 kWh row by year).

## Review
