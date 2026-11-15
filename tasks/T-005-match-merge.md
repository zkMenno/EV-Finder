# T-005 Match merge
Role: builder   Lane: pipeline/ev_pipeline/merge   Wave: 2
Status: review

## Goal
Map source records to variants, merge with priority/majority/recency, confidence.

## Acceptance criteria
- [x] Rules-first matching
- [x] Unmatched rows → data/review/unmatched.csv
- [x] Tests for each merge rule
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**Done (builder, 2026-11-15).** Code: `pipeline/ev_pipeline/match/` (normalise, seed, matcher,
review) and `pipeline/ev_pipeline/merge/` (merge, policy). Tests: `tests/test_match.py`,
`tests/test_merge.py`; fixtures `tests/fixtures/release/`.
- Matching: accent/case/punctuation-free keys, longest whole-token prefix against seed name +
  `name_aliases` (with or without the make name), tiny `MAKE_ALIASES` (VW, Mercedes-Benz,
  Vauxhall...). Generation by year; shared boundary year goes to the newer generation (Q-014).
  Variant id `<generation>-<slug(name or 'base')>`; a seed-manual variant with the same
  normalised name lends its id. Units normalised (Wh/km, miles, currencies); bad units go to
  validation.csv. Registration counts aggregate per generation (model-level only for
  single-generation models, never double counted).
- unmatched.csv: 1412 rows tonight (seed makes in detail, other makes as one summary row each).
  3908 records of seed makes are unmatched, almost all long-tail models (EQB, iX, Ariya...) plus
  registration-style names the seed lacks (Q-021).
- Merge: `data/field_sources.yaml` drives priority order, tolerance and mode (priority / median
  as a real low-median value / newest); unlisted fields keep majority(3+) → priority → recency at
  3%. Confidence high on 2+ independent agreeing sources; seed-manual and model-estimate never
  count as independent (Q-015). Conflicts → data/review/conflicts.csv (489 tonight), never
  averaged.
- Surprise: EEA rows have no variant name, so they sit on `-base` variants and never agree with
  OpenEV's named variants; only 1 WLTP value tonight has 2 agreeing sources (Q-019).

Release 1 published from real staging (openev 1229, rdw 3124, eea 3430 records) + seed: 210 rows,
56 generations, 6554 facts, catalogue.json 1.96 MB raw / 96 KB gzipped. Run: see pipeline/README.md
"Run the pipeline". Checks green: `uv run pytest` (154), `ruff check .`, `ruff format --check .`.
Includes coordinator addenda: Decision 009 (field_sources policy, conflicts.csv, licence gate,
coverage.md, charge curves) and Decision 010 (platforms, packs, voltage, taxonomy).
Open questions raised: Q-014 to Q-023 in QUESTIONS.md.

## Review
