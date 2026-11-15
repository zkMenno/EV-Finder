# T-059 Integrate new sources
Role: WS1   Lane: pipeline/ev_pipeline/{match,merge,release}   Wave: proposed by overnight 1
Status: review (pipeline builder, 2026-11-15)

## Goal
Integrate the overnight sources that only reach staging so far: RDW defects (Known issues), fueleconomy.gov (agreement counts on shared models), charging stats (EAFO, BNetzA, DfT) into catalogue / charging_stats, Wikidata corroboration of generation years.

## Acceptance criteria
- [x] Each source has a release path with provenance and the licence gate
- [x] coverage.md and qa.json show the change
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
Pipeline builder, 2026-11-15 (overnight). Judgement calls in QUESTIONS.md Q-080.

**What shipped (release 1, rebuilt from scratch):**
- **fueleconomy → `epa_range_km`** (new optional PublishedVariant field, also in coverage.md and
  the provenance check). Merged only with EPA facts (field policy: fueleconomy primary, OpenEV
  fallback, 2 %), never with WLTP; EPA consumption stays ignored. 84 rows have EPA range,
  65 use fueleconomy, 45 fueleconomy only; **12 rows gain a 2nd agreeing EPA source** via
  fueleconomy. 280 EPA values sit in conflicts.csv (several US trims/years per variant).
- **Wikidata generation years**: `wikidata` added to `CORROBORATION_SOURCES` (as
  `YEAR_CORROBORATION_SOURCES`, not behind the EEA flag); `merge/generation_years.py` puts
  `years_corroboration` on generations (±1 year, nearest boundary). 13 records: 9 checks on
  8 generations, **7 agree, 2 disagree** (skoda-enyaq-gen1 start 2017 vs 2020; volkswagen-id3-gen1
  start 2024 "Chuzhong" vs 2020), 4 records skipped (model not in seed). Years never change.
- **Known issues** (`derive/known_issues.py`): `catalogue.known_issues` (schema `KnownIssues`),
  per generation × first-registration year, top 5 codes per 100 sampled cars plus the
  same-year baseline (Q-078), `few_reports` flag, Dutch RDW labels. 306 groups in, 211 placed
  (89 model not in seed, 5 shared year, 1 outside generations): **47 generations, 152 cohorts
  (35 few reports), 22 codes**. Source `rdw-defects`.
- **Charging stats** (`release/charging_stats.py`): `data/releases/<n>/charging_stats.json`
  (schema `ChargingStatsRelease`, each row validated as `ChargingStat`, ids checked against the
  charging taxonomies, definition must belong to the same source). **bnetza 2,720 + dft-charging
  141 = 2,861 rows**; EAFO 898 rows gated (status blocked). Aliases (Q-075) via new
  `aliases` support in `release/gate.py` (`Registry.canonical`).
- QA: licence-gate check covers the new sections; new report check `sections` (flag on year
  disagreements). coverage.md has an "Other sections" block.
- Schema (delegated, additive): `PublishedVariant.epa_range_km`, `Generation.years_corroboration`
  (+ `GenerationYearsCorroboration`, `GenerationYearCheck`), `Catalogue.known_issues`
  (+ `KnownIssues`, `KnownIssueCohort`, `KnownIssueDefect`, `KnownIssueCode`),
  `ChargingStatsRelease`; fixtures added, `pnpm --filter @ev/schema gen` run, TS tests pass.
- Size: catalogue.json 3.54 MB raw, **192 KB gzip** (was 179 KB); charging_stats.json 1.48 MB
  raw / 37 KB gzip.
- Tests: `pipeline/tests/test_t059_sections.py` (20 tests); 862 pass, ruff clean.

**Open / next:** WS2 views for known issues, year badges, EPA field and charging charts;
adapter owner may set the rdw-defects `SOURCE.id` to `rdw-defects` and update the wikidata
adapter docstring (it still says the matcher skips its records).

## Review
