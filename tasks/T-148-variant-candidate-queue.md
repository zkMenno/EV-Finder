# T-148 Variant candidate review queue, biggest EU registrations first
Renumbered from T-146 on 2026-11-18: the coordinator gave T-146 to the hero results follow-ups at the same time. Branch names keep t-146-*.
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
**PR 1 (seed, 2026-11-18):** first variants for 5 "no-variant" generations, biggest EU first: Mokka-e 50 / 54 kWh, Twingo Electric 22 kWh, e-up! 18.7 / 32.3 kWh, Avenger 54 kWh. Battery + power `cited:` from maker pages (matching evidence; maker-docs values stay internal, the release takes figures from TGK / RDW / KilowattApp / ADEME as before). Links: existing platform rows, new pack rows with only the maker's capacity, new platform `vw-up-family`.
- Left out on purpose: **Kia EV3** (whichever EV3 row exists takes the 2026 two-motor EV3 data: fresh review found the Standard row built as AWD / 583 km once it was the only row; the generation needs Standard, Long Range and AWD rows together, the AWD one from a Kia page). **Mokka GSE** (2025+, 207 kW) not split.
- Known ties that go to review (nothing misplaced): Mokka 2022+ 100 kW vs 115 kW versions (both packs fit, years overlap); e-up! 2018-2020 versions without a range.
- Queue after PR 1 (fresh staging 2026-11-18): no-variant EU cars 891,029 -> 573,448; % EU registrations on groups we have 63.8 -> 66.7.

**PR 2 (ID.7):** OpenEV's only ID.7 rows ("PRO", "Tour") carry the Pro S figures (86 net / 91 gross / 210 kW / 700 km; T-118's Italian price list said the same), so the 77 kWh Pro versions fit nothing (no-fit, 46k EU cars) and Pro S versions sat on a row named Pro. Seed rows Pro (77 kWh), Pro S (86 kWh, joins OpenEV "PRO" + "Tour" via source_names) and GTX (86 kWh, AWD), VW Newsroom cited; old ids retired to the Pro S row; the IT list price moved with it (Tourer price parked as a comment). All ID.7 TGK groups now `have`. Pro S cites 200 kW DC so OpenEV's 175 (the Pro's) is withheld.

**PR 3 (Elroq, narrowed after fresh review):** OpenEV has only "Base" (77 kWh, 581 km: the Elroq 85, but with 150 kW) and "RS". Seed rows Elroq 50 / 60 from Škoda's technical data (5 May 2025), years = generation start 2025, drivetrain from Škoda's 9 Dec 2024 press kit: 50 / 60 TGK groups now `have` (32k EU cars). Base kept: a seed 85 with Škoda's 210 kW does not take Base's records (power gate), so the 85 would lose its charging data; Elroq 85 versions still tie (now 60 / Base / RS). Base's NL price 42,005 and used prices came from RDW Elroq 60 records (placed by OpenEV's wrong 150 kW) and now sit on the 60 row: 2 approvals in gate PR #168. Next: fix OpenEV Base's power (source hold or WS1 power-gate exception for cited power) and then add the 85.

**Top tie / several groups (not seed-fixable, WS1 ask in INBOX):** the matcher can't tell apart variants that share a pack, because TGK evidence ignores 30-minute power, top speed and the TGK model code. Seen on: Model Y gen1 LR AWD vs Performance (217 vs 250 km/h; the 2021 Y5CD 507 km LR versions are placed on Performance), ID.4 Pro vs GTX (30-min power stated = one motor), e-208 / Corsa / e-2008 / Mokka 100 kW vs 115 kW (30-min 57 vs 62 kW; type codes ZKXZ vs ZKWZ; 2024-26 ZKXZ e-208 versions placed on the 51 kWh row by year).

## Review
