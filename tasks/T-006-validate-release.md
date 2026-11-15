# T-006 Validate release
Role: builder   Lane: pipeline/ev_pipeline/release   Wave: 2
Status: review

## Goal
Range checks and release folder with catalogue.json + Parquet + diff.

## Acceptance criteria
- [x] Range checks for kWh, km, kW, price
- [x] data/releases/<n>/catalogue.json + .parquet
- [x] Diff against previous release
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**Done (builder, 2026-11-15).** Code: `pipeline/ev_pipeline/release/` (build, validate, gate);
CLI `ev release [--dry-run]` → `release_cmd`. Tests: `tests/test_release.py`.
- Range checks on every fact before merging and on derived values; ac_kw allows 2–43 (Zoe 43 kW
  AC, coordinator). Dropped values → data/review/validation.csv.
- Release folder: catalogue.json (compact, 1 decimal), catalogue.parquet, facts.parquet,
  diff.json, coverage.md, README.md (licences + attribution), run_log.json; written under a temp
  name and renamed; `latest` updated last. n = max + 1. Dry-run writes nothing.
- Fails on: JSON Schema or Pydantic errors, a number without provenance, an excluded or
  non-active source (data/sources.yaml gate; nyland always), ODbL licence, unknown
  taxonomy/platform/pack id. Tests prove a nyland record never reaches any release file, even
  smuggled into another source's file or without sources.yaml.
- Schema bug found (Q-017): `oneOf [Id, const 'not-disclosed']` rejects 'not-disclosed'.
  Interim workaround: those keys are left out of shipped platform/pack objects.
- EEA licence is "(to confirm)" but status active, so it is released (Q-022).

Release 1 published from real staging (openev 1229, rdw 3124, eea 3430 records) + seed: 210 rows,
56 generations, 6554 facts, catalogue.json 1.96 MB raw / 96 KB gzipped. Run: see pipeline/README.md
"Run the pipeline". Checks green: `uv run pytest` (154), `ruff check .`, `ruff format --check .`.
Includes coordinator addenda: Decision 009 (field_sources policy, conflicts.csv, licence gate,
coverage.md, charge curves) and Decision 010 (platforms, packs, voltage, taxonomy).
Open questions raised: Q-014 to Q-023 in QUESTIONS.md.

## Review
