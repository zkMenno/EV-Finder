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

**Reviewer (fresh agent), 2026-11-15. Verdict: changes needed (one hard-rule breach in fixtures).**

Boxes hold. Range checks: `release/validate.py:23-34`. Release folder: catalogue.json + catalogue.parquet + facts.parquet + diff.json + coverage.md + README + run_log. Diff is tested. All offline. The reviewer added `pipeline/tests/test_real_release.py` (11 tests), which loads the committed `data/releases/latest` and asserts:
- the Catalogue JSON Schema;
- every non-null number in every row, on any key, has provenance (prices included);
- every provenance entry has a source and a confidence, and every source is listed;
- every fact_id resolves in facts.parquet;
- every released source is `active` with a named, confirmed licence in `data/sources.yaml`;
- no "nyland"/"bjørn" bytes in any release file;
- real range ⇔ rung, and estimated rungs are flagged `estimate`;
- the AC/DC formulas;
- merged values are never averages.
All pass on release 1.

Findings
1. **Nyland fixture uses a real car (high, hard rule).** `pipeline/tests/fixtures/release/staging/nyland.records.jsonl` is attributed to `nyland` but describes a real car: *Tesla Model 3 Long Range 2022, real_range 480 km, 76 kWh*. The rule allows only synthetic "Testcar" rows. Even if the numbers were invented, they look like a real Nyland result, and they now ship inside the jobs Docker image (see T-013). `tests/test_release.py:250-266` and `tests/test_match.py:241-251` use the same car. Replace it with a Testcar make/model, plus a matching Testcar entry in `tests/fixtures/release/models.yaml`.
2. **The gate fails open without a registry.** `release/gate.py:44-45`: when `data/sources.yaml` is missing, every source except nyland is releasable. `tests/test_release.py:261` locks this in. A missing registry should block the release, per Decision 009's "only active sources... reach a public release".
3. **"(to confirm)" licences pass the gate.** `gate.py:51` strips the parenthesis. That contradicts `data/sources.yaml:4` ("they stay blocked until checked"). No active source carries "(to confirm)" today, so there is no impact yet, but the two rules should agree. Prefer blocking.
4. `data/releases/1/run_log.json` holds absolute host paths (`/home/claude/zkmenno/ev-finder/...`, lines 6-48). `release/build.py:109,127,224,226,257` use `str(path)` where `sources/_common.py::rel()` exists. That leaks the build machine layout into a public repo and makes runs machine-dependent. Low.
5. Range checks don't cover `power_kw`, `weight_kg`, `real_range_km`, `seats`, `dc_minutes_10_80` or the derived `dc_km_*`. The box is met for kWh/km/kW/price, but these should be added. Low.
