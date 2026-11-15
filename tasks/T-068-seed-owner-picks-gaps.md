# T-068 Seed the models in Menno's picks that the catalogue lacks
Role: builder   Lane: data/seed   Wave: 9
Status: review (WS3, 2026-11-15)

## Goal
Every car in `data/editorial/menno-picks.yaml` maps to a seed generation.

## Acceptance criteria
- [x] Add models/generations (sourced years, aliases): XPENG G6 (2024 v1.1 / 2025 v1.3 as change marker or generation), P7, P7+, L03, L05 (announced), Zeekr 001, 7X, 7GT, X, Volvo EX60, EX50, EC40/C40, Kia EV4, Hyundai IONIQ 3, VW ID.5, Polestar 4, MG IM6, MG5, MGS5, Marvel R, BYD Sealion 7, Renault 4, Peugeot e-308 (+SW), Opel Astra Electric (+ST), Nissan Ariya, Opel Ampera-e, DS3 E-Tense, Fiat 600e, Smart #3, Genesis GV60, Ford Capri, Leapmotor B05, Lynk & Co 02, Audi A2 e-tron (announced), Geely E5, Subaru Uncharted
- [x] EV6 and IONIQ 5 2024 updates (84 kWh, V1.2) as distinct variants or a generation split (his tiers treat them as different cars); decide and log
- [x] Check years where his sheet and the seed disagree: Skoda Elroq (2024 vs 2025), Renault Scenic E-Tech (2023 vs 2024)
- [x] Fill `MODEL_MAP` in `data/editorial/import_menno_sheet.py`, re-run, no `seed_model_id: null` left for released makes
- [x] validate_seed.py + validate_variants.py pass

## Inputs
Decision 038, research/R-32. EV Database car ids in the picks file help matching only; never copy its data.

## Handoff notes
2026-11-15, WS3 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr).
- **36 models added** to `data/seed/models.yaml` (8 new makes: XPENG, Zeekr, Genesis, Leapmotor, Lynk & Co, Geely, Subaru, DS): XPENG G6 (gen1 + facelift), P7, P7+, L03, L05; Zeekr 001, 7X, 7GT, X; Volvo EX60, EX50, EC40 (C40 + EC40 gens); Kia EV4; Hyundai Ioniq 3; VW ID.5; Polestar 4; MG IM6, MG5, MGS5, Marvel R; BYD Sealion 7; Renault 4 E-Tech; Peugeot e-308 (+SW); Opel Astra Electric (+ST), Ampera-e; Nissan Ariya; DS 3 E-Tense (Crossback + facelift); Fiat 600e; Smart #3; Genesis GV60; Ford Capri; Leapmotor B05; Lynk & Co 02; Audi A2 e-tron; Geely E5; Subaru Uncharted. All `uncertain: true`.
- **Years:** T-051 rule (first RDW first-admission year with ≥ 5 % of NL cars) from live RDW queries (m9d7-ebf2, 2026-11-15); shared names (308, ASTRA, DS3, 600) split to BEV with RDW fuel data (8ys7-d773). Announced or not-yet-in-NL cars (L05, EX50, A2 e-tron, IM6, L03, P7+, G6 facelift, EX60) cite a maker or press page in `notes`. Counts are in each generation's notes.
- **Body:** OpenEV `body.style` (repo cloned 2026-11-15); else a judgement noted per model. **Segment:** length band (OpenEV or RDW `lengte`), judgement as in Q-081; rule in the comment above xpeng.
- **EV6 / Ioniq 5 / G6:** generation split (Decision 057): `kia-ev6-facelift`, `hyundai-ioniq-5-facelift`, `xpeng-g6-facelift` from 2024/2024/2025; gen1 ends 2024 (G6: 2025); the 7 gen1 seed variants capped at 2024. Pre-facelift EV6 GT sold into 2025 falls outside (noted).
- **Year checks:** Elroq stays 2025 (no NL car in 2024), Scenic E-Tech stays 2024 (none in 2023); his rows map as `generation_match: nearest` (Decision 058).
- **Importer:** `MODEL_MAP` filled; nearest-generation fallback (±1 year); new `--remap` mode refreshes seed ids without the xlsx. Re-run done: no `seed_model_id: null` left. Back-test unchanged: 24/30 exact (80 %).
- **Known gaps for WS1:** (1) `normalise.key` drops `+`, so P7 and P7+ share a key: RDW P7 2023-25 cars currently go to review (outside every generation of xpeng-p7-plus), never misplaced. Ask: tokenise `+` as `plus`. (2) No KBA / DfT / EEA aliases checked for the new models (no staging here); EEA files Genesis under 'HYUNDAI, GENESIS'. (3) Facelift generations have no `variant_links` defaults. (4) Release + `top40.yaml` not rebuilt (needs staging).
- **Cross-lane edit (flag for WS1):** `pipeline/tests/test_registrations.py` one expectation: DfT 'VOLKSWAGEN ID5 / ID5 MATCH PRO' now places on `volkswagen-id5` (it asserted "not in seed"). Placement spot checks for 60 source names were run locally (all as expected except the P7 key clash).
- Validators: validate_seed.py OK (35 makes, 99 models, 122 generations), self-test ok, validate_variants.py OK; pipeline pytest 1353 passed; ruff clean.

