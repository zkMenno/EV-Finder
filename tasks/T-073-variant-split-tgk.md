# T-073 Variant split from RDW TGK versions (+ EEA corroboration) into the review queue
Role: builder   Lane: pipeline/ev_pipeline/variants, data/review   Wave: launch (R-41 task 1)
Status: review (WS1 7th, 2026-11-18)

## Goal
Turn every type-approval version (RDW TGK) of our seed models into candidate variants per generation, so a reviewer can add the missing variants; write them to `data/review/`, never straight into a release.

## Acceptance criteria
- [x] `ev variants propose` reads the TGK records + seed, places each version on a seed variant (existing matcher) or clusters it into a candidate (generation × 30-min power × WLTP/NEDC range band × energy drawn).
- [x] Output `data/review/variant-candidates.csv` (review ids via review_queue) + `variant-coverage.json` (models / generations / variants / candidates / % EU registrations).
- [x] EEA is counts only (Decision 049): EU registrations per TAN|variant|version corroborate a candidate and weight the coverage share; no EEA spec value becomes a fact.
- [x] Every candidate row cites its TGK record keys; no value without source + date.
- [x] Tests on fixtures (no network); dry run on the live TGK data quoted in the PR (rule G-10).
- [x] Coverage count in the PR body (Menno, 2026-11-18).

## Inputs
research/R-41-catalogue-coverage.md (task 1), research/R-08 (adapter plan D: spec fingerprint), Decisions 048, 049, 068. WS0 INBOX 2026-11-18 08:58.

## Out of scope
Seed edits (WS3 owns data/seed; candidates are proposals for them). Kilowatt rows (Q-047). ev-database.org. Battery kWh (R-41 task 3, WS3).

## Handoff notes
- Built: `ev variants fetch-eea` (sources/eea/versions.py, EU counts per TAN base|Va|Ve, 2010–2025, licence checked per SDI record, no spec column selected) and `ev variants propose` (variants/propose.py, commands/variants.py). Review ids prefix `vc-` (review_queue KEYS); the step writes only its own CSV, the release's CSVs are untouched.
- Fingerprint: cycle × single/multi motor × energy drawn (split at > 4 % gaps). Exact 30-min power is listed, not split on: Tesla files one car under 88–127 kW. Tried "8 % from the lowest" first; it cut dense one-pack runs (Mach-E 99–109 kWh) at arbitrary points.
- Dry run 2026-11-18 (RDW TGK 8,519 versions, OpenEV, EEA 9,109,550 EU BEVs): 5,439 versions in 115 seed generations → 390 groups: 154 have, 33 several, 107 tie, 35 no-fit, 61 no-variant. Candidates (no-fit + no-variant) = 96 → 367 variants if all are real. Matcher variant set = release 2's 271 exactly (checked).
- Below R-41's ~450–550 estimate: the fingerprint deliberately under-splits (trims sharing pack + motor count stay one group; reviewers split by `trade_names`). 107 ties are variants we have but can't pick between; resolving them is evidence work, not new rows.
- Found while testing: OpenEV gives the ID.7 Pro 86 kWh net (that is the Pro S), so the 77 kWh Pro versions fit nothing (`no-fit`). Same pattern likely on other `no-fit` rows: check the seed battery before adding a variant.
- 3,052 versions are models not in the seed (EQV, Model X, EQE, e-tron GT, e-up!, vans): WS3's R-41 task 2. Top 25 in variant-coverage.json.
- Next: R-41 task 5 long tail (Decision 048 stretch): same tool, groups for models not in the seed.

## Review
