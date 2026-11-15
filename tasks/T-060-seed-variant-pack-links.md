# T-060 Seed variant pack links
Role: WS3   Lane: data/seed/variant_links.yaml   Wave: proposed by overnight 1
Status: review (pipeline builder, 2026-11-15)

## Goal
Link the 72 rows without a battery pack (55 OpenEV/KilowattApp variants not covered by variant_links.yaml, 17 multi-pack generations).

## Acceptance criteria
- [x] variant_links accepts release variant ids, not only seed ids
- [x] Coverage of pack/platform per row reported
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
Pipeline builder, 2026-11-15. No git commands run (per brief). Release 1 rebuilt from existing staging (no refresh).

**Result (release 1, 244 rows; the task's "72 of 195" was an older count: before this task 121 rows had no pack and 104 no platform):**

| | before | after | from file | by rule | missing |
|---|---|---|---|---|---|
| battery_pack_id | 123 | 181 | 123 | 58 | 63 |
| platform_id | 140 | 206 | 149 | 57 | 38 |

**What changed**
- `pipeline/ev_pipeline/derive/links.py`: `apply_rule_links` + `pack_fit` + `link_coverage` + `cited_note`; `Links.by_rule` (file links always win; rule fills only empty keys). Rules: platform when every file link of the generation names one platform; pack when the row's own merged usable kWh fits exactly one pack linked in the same generation, within 6 % (`RULE_TOLERANCE`, same as the validator's `CAPACITY_TOLERANCE`) of usable (gross if usable not disclosed), never above gross. Each rule link carries a provenance note with the generation, kWh and % off.
- `pipeline/ev_pipeline/release/build.py`: runs the rule after the merge/guards, before inheritance; new `pack_links` section in the run log and a "Battery pack and platform links" table + per-row missing list (with reason) in `coverage.md`.
- `data/taxonomy/validate_taxonomy.py`: links may use release variant ids (`<generation_id>-<slug>`, longest-prefix match; need pack or platform; voltage/charger optional); `cited:` on links (platform_id / battery_pack_id, README format; value must equal the link's value); platform-only generation defaults allowed when the platform is cited. 4 new self-test cases (29/29).
- `data/seed/variant_links.yaml`: 4 cited platform-only generation defaults (manufacturer pages, retrieved 2026-11-15): ID.7, ID. Buzz, Elroq → `vw-meb`; Renault 5 → `renault-cmf-bev` (AmpR Small). No new packs or platforms invented.
- `data/seed/README.md`: section on link keys, cited links and the rule.
- `pipeline/tests/test_t060_pack_links.py`: 10 tests (inline data, no network).

**Rule links within tolerance but > 5 % off (reviewer: worth a look)**: Tesla Model 3 Highland Performance and Model Y Juniper LR AWD/Performance (79 kWh → `tesla-m3y-lr-75`, 5.3 %; the seed already notes Highland/Juniper LR is not split from the gen1 pack), Audi Q4 50/quattro (73 → `meb-77`, 5.2 %), Q8 e-tron 55/quattro (100 → `audi-q8-etron-114` usable 106, 5.7 %), Ioniq 6 Standard (50 → `egmp-53` gross, 5.7 %), Leaf e+ (62 → `nissan-leaf-62` usable 59, 5.1 %).

**Still unlinked (63 rows; full list with reasons in data/releases/1/coverage.md)**
- No pack or platform in seed for the generation (needs new platform/pack rows, i.e. sourced data): Audi A6/Q6 e-tron (PPE), BMW i5, iX, iX1, iX3, Porsche Taycan, Macan Electric, Toyota bZ4X, Mercedes CLA, EQB, Volvo EX30, Renault Scenic, Cupra Tavascan, Ford Explorer, Ford Puma Gen-E. Platform rows exist for some (`volvo-sea`, `mercedes-mfa2`, `renault-cmf-ev`, `vw-meb`, `bmw-clar`) but no manufacturer page found/readable that names them: Volvo EX30 press pages say only "purpose-designed electric vehicle platform"; Ford's Explorer press pages don't name MEB; Cupra Tavascan and Renault Scenic press-kit pages were blocked by a permission prompt in this session (seat-cupra-mediacenter.com, media.renault.com Scenic page).
- Platform linked by citation, pack still missing (no pack row): ID.7 (86 kWh), ID. Buzz, Elroq, Renault 5 (11 rows). Elroq/Buzz 77 kWh likely `meb-77`, but that is cross-generation evidence, so not linked.
- Ambiguous: Polestar 2 LR rows (75 kWh fits `cma-78` 0 % and `cma-82` 5.1 %; no model year on the rows).
- Fits no generation pack (likely data issues or missing packs): Audi Q4 40 Sportback (48 kWh; Q4 40 is a 77 kWh car, OpenEV value looks wrong), BYD Atto 3 Standard (49/49.9 kWh pack not in seed), Mach-E Premium (82), Ioniq 5 N (78 > 77.4 gross; really the 84 kWh pack, not linked in that generation), Ioniq 6 LR/AWD (72.6 vs 77.4), Kona SX2 LR (58), Mercedes EQA (60 vs 66.5), Kona SX2 Standard (no own usable kWh).

**Follow-ups (not done, out of scope)**: add PPE / J1 / e-TNGA / MMA / SEA-pack rows from sourced data; a stale-id warning for release-id links whose row disappears; data/review/coverage-gaps.md still quotes the old 72/195 figure (owned by the review agent).

Checks run: `ruff check`, `ruff format --check`, `pytest -q` (1147 passed), `qa check-release ../data/releases/latest` (pass), `validate_taxonomy.py` (0 errors) and `--self-test` (29/29).

## Review
