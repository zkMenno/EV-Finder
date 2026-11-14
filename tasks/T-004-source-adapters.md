# T-004 Source adapters
Role: builder   Lane: pipeline/sources   Wave: 2
Status: review (builder, 2026-11-15)

## Goal
OpenEV, RDW and EEA adapters: fetch → raw → normalise → Fact rows.

## Acceptance criteria
- [x] One folder per source with recorded sample fixtures
- [x] Tests run offline
- [x] Licences recorded in data/SOURCES.md
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
**Built** (`pipeline/ev_pipeline/sources/`): `openev`, `rdw`, `eea` and `nyland` (skeleton), plus
the shared helper `_common.py` (paths, `_fetch.json`, staging writer, run log). Each adapter
exposes `fetch_cmd()`, `normalise(raw_dir, retrieved_at)` and `normalise_cmd(from_fixtures)`.
`retrieved_at` is the fetch date stored in `_fetch.json`, so re-runs give the same output.
The output is sorted by `record_key`. Setting `EV_DATA_DIR` redirects `data/` (the tests use it).

**Live run, 2026-11-15** (rows out):
- openev: 1,229 records (1,189 vehicles + 40 DE EUR prices), commit `8edb266d`.
- rdw: 3,124 records, 922,990 BEV passenger cars in NL.
- eea: 3,430 records (1,715 counts + 1,715 type-approval averages), NL/DE/FR/BE, 2025 provisional.
- nyland: not run (no URL; permission pending).

**From fixtures:** openev 37, rdw 118, eea 68, nyland 3 (synthetic). The live normalise was
re-run afterwards, so `data/staging/` now holds the live output.

**Licences:** confirmed in metadata tonight and recorded verbatim in data/SOURCES.md:
- openev: CDLA-Permissive-2.0.
- rdw: CC0 ("Creative Commons 0 (CC0)").
- eea: "License CC-BY 4.0 … Copyright holder: DG-CLIMA". `data/sources.yaml` can drop "(to confirm)" for eea.

**Tests:** `tests/test_source_{openev,rdw,eea,nyland}.py`, 21 tests, offline (fixtures +
`httpx.MockTransport`). `ruff check` and `ruff format --check` are green. The full `pytest`
run has 4 failures, all in `tests/test_derive.py` (another lane, being edited during this
run: `derive.metrics` lacks `dc_km_per_10min`/`dc_avg_estimate`). None are in this lane.

**Things to know:**
- RDW has no join. Counts use the proxy "passenger car, no displacement, first admitted ≥ 2010",
  validated against the fuel dataset (Q-010). RDW trade names are raw (`NISSAN LEAF 40KWH`):
  matching has work to do.
- The EEA Discodata WAF returns 403 to GET queries, so the adapter POSTs. The table name is a
  constant (`co2cars_2025Pv31`) (Q-011).
- OpenEV: some upstream variant files break the naming rule. They attach to the year-base file
  whose name is the longest prefix of theirs, or to `base.json` alone. The data has no
  consumption and no DC curves. `dc_curve` can't be emitted until `SpecValue` allows a
  `ChargeCurve` (Q-009). The coordinator's mid-run request is covered: chemistry_id, cooling_id,
  voltage_nominal_v, voltage_max_v, warranty_years/km and dc_minutes_10_80 are emitted
  (field choices in Q-012).
- Nyland writes only to `data/local/nyland/` (records and its own run log). The URL is never
  logged. The column mapping is a placeholder (Q-013).
- Edits outside the lane: `.env.example` (`NYLAND_SHEET_CSV_URL`), `.gitignore` (`data/staging/`),
  `QUESTIONS.md` (Q-009 to Q-013). No new dependencies.

## Review
