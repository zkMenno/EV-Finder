# T-073 Variant split from RDW TGK versions (+ EEA corroboration) into the review queue
Role: builder   Lane: pipeline/ev_pipeline/variants, data/review   Wave: launch (R-41 task 1)
Status: doing (WS1 7th, 2026-11-18)

## Goal
Turn every type-approval version (RDW TGK) of our seed models into candidate variants per generation, so a reviewer can add the missing variants; write them to `data/review/`, never straight into a release.

## Acceptance criteria
- [ ] `ev variants propose` reads the TGK records + seed, places each version on a seed variant (existing matcher) or clusters it into a candidate (generation × 30-min power × WLTP/NEDC range band × energy drawn).
- [ ] Output `data/review/variant-candidates.csv` (review ids via review_queue) + `variant-coverage.json` (models / generations / variants / candidates / % EU registrations).
- [ ] EEA is counts only (Decision 049): EU registrations per TAN|variant|version corroborate a candidate and weight the coverage share; no EEA spec value becomes a fact.
- [ ] Every candidate row cites its TGK record keys; no value without source + date.
- [ ] Tests on fixtures (no network); dry run on the live TGK data quoted in the PR (rule G-10).
- [ ] Coverage count in the PR body (Menno, 2026-11-18).

## Inputs
research/R-41-catalogue-coverage.md (task 1), research/R-08 (adapter plan D: spec fingerprint), Decisions 048, 049, 068. WS0 INBOX 2026-11-18 08:58.

## Out of scope
Seed edits (WS3 owns data/seed; candidates are proposals for them). Kilowatt rows (Q-047). ev-database.org. Battery kWh (R-41 task 3, WS3).

## Handoff notes

## Review
