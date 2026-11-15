# T-051 Expand seed top missing
Role: WS3 + WS1   Lane: data/seed   Wave: proposed by overnight 1
Status: todo

## Goal
Add the biggest BEV models missing from the seed (VW ID.7, Skoda Elroq, BMW iX1, Kia EV3, Volvo EX30, Audi Q6 e-tron, Ford Explorer and the rest of the top-20 in data/review/coverage-gaps.md / data/seed/top40.yaml).

## Acceptance criteria
- [ ] Each new model has generations with years from registration evidence (RDW/KBA/EEA) and Wikidata corroboration, `uncertain` flags where needed
- [ ] No specs from memory: variants come from OpenEV/KilowattApp/RDW/ADEME records
- [ ] Release coverage of NL/UK fleet and DE new registrations reported before/after
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
2026-11-15, overnight data builder (part 1: the 8 top-40 models missing from the seed). The other top-20 models from coverage-gaps.md (ID.7, Elroq, EV3, Q6 e-tron, ...) are still open.
- Added to `data/seed/models.yaml`: volvo-ex30, bmw-ix1, bmw-ix3 (2 gens), opel-mokka, mercedes-eqb (EQB + GLB electric), porsche-taycan (new make), bmw-ix, ford-explorer. The iX3 was not in the seed before (no partial entry). Years, body, segment and aliases are from staged RDW/EEA/KBA/DfT/OpenEV/KilowattApp/ADEME data and Wikidata; the counts are in each generation's `notes`. The rule is in the comment above volvo-ex30. Judgement calls: QUESTIONS Q-081.
- No variants were hand-entered. Rows come from OpenEV (21 new rows). opel-mokka-gen1, bmw-ix3-gen2 and mercedes-eqb-glb have 0 rows (no OpenEV record).
- `variant_links.yaml` not touched (no grounded pack/platform source). `validate_seed.py` not changed (its required list is the brief's 40, not the top-40).
- Tests: `pipeline/tests/test_seed_t051.py` (source names to model/generation, no network); `test_registrations.py` KBA "X1" now expects bmw-ix1 (X2 keeps the "never invent" case).
- Release 1 rebuilt (218 rows, was 197); `data/seed/top40.yaml` regenerated (40 of 40 in seed).
- Shares placed (same staging, before → after): NL RDW used fleet 2018-24 79.2 → 86.5 %, NL fleet all ages 63.9 → 71.8 %, UK DfT 62.9 → 71.8 %, DE KBA 2025 39.4 → 49.2 %, DE KBA 2026 YTD 32.2 → 41.5 %. Unmatched records 9780 → 9016.

## Review
