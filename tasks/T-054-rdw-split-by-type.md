# T-054 Rdw split by type
Role: WS1   Lane: pipeline/ev_pipeline/sources/rdw   Wave: proposed by overnight 1
Status: merged (PR #1); fresh review via QA A-35; earlier note: pipeline builder, 2026-11-15, branch proto/overnight-1

## Goal
Split RDW price and WLTP groups by type/variant/uitvoering where that resolves the 680 price groups dropped for spread.

## Acceptance criteria
- [x] Mapping from type-approval codes to seed variants (rules, not guesses), unmapped codes to review: no code table (per the brief); records carry kW + WLTP evidence and the attach-only matcher rule places them; unplaceable ones go to unmatched.csv
- [x] Number of NL prices before/after: 366 → 1,257 records (live, 2026-11-15)
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
Pipeline builder, 2026-11-15. Code: `pipeline/ev_pipeline/sources/rdw/adapter.py`; tests: `pipeline/tests/test_source_rdw.py` (25, offline); fixture rebuilt from the live fetch (≤ 200 rows/file); docs: data/SOURCES.md RDW row + notes.

- **How:** a coarse group (merk × handelsbenaming × year) that is too wide for a field is split by `type`+`variant`, and a still-wide sub-group by `uitvoering` too. Price per sub-group: two more server-side grouped queries (`price-variant.json`, `price-uitvoering.json`). WLTP: the existing 10 % plate sample, now stored per code group (`sample-groups.json`, also kW from `netto_max_vermogen_elektrisch`) and summed upwards. Same spread rule (IQR > 5 % / < 5 cars) at each level.
- **No double counting:** per field, the coarse record when the coarse group passes, else only the finest passing sub-groups. Narrow coarse fields are never split. Tested (`test_split_never_counts_a_car_twice`).
- **Evidence for the matcher:** a fine record holds every field that passed for that sub-group (price travels with WLTP km) plus `variant_name` "<kW> kW" (median power, spread-checked). Power is never a fact (RDW lists one motor for some dual-motor cars). Integration test runs `match_records` on a 2-variant seed.
- **Live result (fetch 5.5 min, ~55 requests 1 s apart; normalise):** price 366 → 1,257, WLTP range 740 → 1,252, consumption 743 → 1,133. Coarse wide groups recovered: price 387 of 680, range 174 of 233, consumption 135 of 191. Sub-groups dropped: price 102 + 674 wide, 536 + 1,084 small (variant + uitvoering); range 6 + 47 wide, 154 + 233 small. Small fine price groups are mostly the 10 % sample being < 5 cars for a uitvoering.
- **Read-only matcher run (real seed, other staged sources, no release):** RDW price facts on variants 88 → 463 (40 → 109 variants); WLTP range 356 → 590. Fine records unmatched: 283 model not in seed, 256 no variant evidence, 31 no variant. Mis-placements where the seed lacks a row: Q-086.
- **Probe:** the new queries are in `_FETCH_QUERIES`, so pre-T-054 raw folders refetch once; afterwards `probe_unchanged` returns True with two metadata calls (checked live).
- Not done: coarse records still have no kW evidence (unchanged on purpose); RDW `type` code → generation evidence not used.

## Review
