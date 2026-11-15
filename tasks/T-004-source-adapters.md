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

**Reviewer (fresh agent), 2026-11-15. Verdict: changes needed.**

Boxes confirmed: one folder per source under `pipeline/ev_pipeline/sources/` with fixtures under `pipeline/tests/fixtures/<name>/`. Tests are offline (`httpx.MockTransport`; no network in the suite). Licences in `data/SOURCES.md` match `data/sources.yaml`. No marketplace scraping anywhere: the only marketplace URLs are user-facing "see listings" deep-link templates in `apps/web/src/config/countries.ts`, which Decision 004 allows. No secrets: `.env.example` has names and dummy values only. Nyland: the URL comes from env only, output goes to git-ignored `data/local/nyland/` only, and the adapter fixture `tests/fixtures/nyland/synthetic.csv` is all invented "Testcar" rows.

Findings
1. **EEA spec facts are averages across different cars (medium-high).** `sources/eea/adapter.py:40-53` publishes registration-weighted means of mass, Z and Zr over *all* type approvals under one commercial name (all battery sizes, wheels and trims) as `wltp_range_km` / `consumption_kwh_100km` / `weight_kg` facts. Where a name covers several packs or trims, the fact is a blend that may match no single car. Such facts then sit on `-base` variants (e.g. `dacia-spring-gen1-base` WLTP 228 covers all 2025 Spring trims; the Q8 e-tron EEA rows give 18.5 to 29 kWh/100km across names, see conflicts.csv). That goes against the spirit of "conflicts are never averaged" (Decision 009). Options: group by type-approval variant (TAN/Va/Ve) and emit per-variant facts, or emit only when the group's min and max agree within tolerance, else count-only.
2. EEA `M (kg)` is *mass in running order* (includes a 75 kg driver), but it goes in as `weight_kg` next to OpenEV curb weight (`eea/adapter.py:161`). That causes systematic conflicts or a wrong winner on weight. Map it to its own field, or subtract the 75 kg and say so in the note. Low-medium.
3. Nyland fetch prints the httpx exception (`sources/nyland/adapter.py:104`). For `HTTPStatusError`, the message contains the full sheet URL, so it leaks to stdout and CI or cron logs. Print only the status code. Low.
4. `dc_avg_10_80` in the OpenEV adapter (`openev/adapter.py`) is a derived value (net × 0.7 / minutes), but it is emitted as an OpenEV source fact with the source's confidence, not marked derived. Low; it's documented in SOURCES.md.

## Fixes after review

**Builder, 2026-11-15 (proto/overnight-1).**
1. EEA averaged specs (finding 1) and EEA mass (finding 2): **EEA is count-only.** `sources/eea/adapter.py`
   emits only `registered_count` records. The registration-weighted M/Z/Zr averages stay in the raw pages
   and never become facts, so mass in running order can't merge with curb weight. Belt and braces:
   `matcher.COUNT_ONLY_SOURCES` drops any EEA spec record (e.g. a stale staging file) and counts it in the
   run log. Per-type-approval rows are QUESTIONS.md Q-039. Tests: `test_source_eea.py::test_counts_only_no_averaged_specs`,
   `test_match.py::test_variant_ids_and_year_merge`, `test_release.py::test_release_end_to_end`,
   `test_real_release.py::test_no_eea_spec_facts`.
2. Nyland fetch leak (finding 3): `nyland/adapter.py::scrub_error` prints `HTTP <code>` or the error
   class only, never the exception text (which holds the URL). Test: `test_source_nyland.py::test_fetch_error_never_prints_url`
   (status error and connect error).
3. Finding 4 (`dc_avg_10_80` from OpenEV not marked derived) was not in tonight's fix list and is still open.

Release 1 rebuilt (`rm -rf data/releases && uv run ev release`) from openev 1229, rdw 3124 and eea 1715 (counts only) records + seed: **195 rows** (was 210), 55 generations with rows, 6063 facts, conflicts.csv 79 (was 489), unmatched.csv 1383 rows (2726 seed-make records + 1920 other-make records unmatched), validation.csv 0, tiers single-source 195, real-range rungs body-ratio 105 / none 90, catalogue.json 1,925,423 B raw / 91,755 B gzipped. Checks green on my files: `ruff check`, `ruff format --check`, `pytest` (251 incl. test_real_release.py).
