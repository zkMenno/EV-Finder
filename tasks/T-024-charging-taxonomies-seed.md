# T-024 Charging taxonomies and link-out config
Role: WS3   Lane: data/taxonomy, config/countries   Wave: 6
Status: review (overnight builder, 2026-11-15)

## Goal
Seed the charging taxonomies and the per-country link-out block for the five launch countries.

## Acceptance criteria
- [x] `charging_metrics`, `charging_definitions` (one row per source definition, incl. public vs semi-public), `power_bands` with source-band mapping
- [x] `country_charging_links` for NL, DE, FR, BE, UK: max five links, order per spec, each with job + URL
- [x] Plain-language label per row in EN + NL (other languages may be marked review: needed)

## Inputs
docs/spec/charging-buildout.md, T-023.

## Out of scope
Ingest jobs, pages.

## Handoff notes
Overnight builder, 2026-11-15 (branch proto/overnight-1; no git commands run, commit is the coordinator's).

**Files.** New: `data/taxonomy/charging_metrics.yaml` (10), `charging_definitions.yaml` (11: AFIR/EAFO, IEA, NL RVO public and public + semi-public, DE BNetzA, FR Avere, BE EV Belgium public + semi-public, UK DfT devices to 2025 → EVSE from 2026 with `replaced_by`, US AFDC ports, AU EV Council connectors), `power_bands.yaml` (13: our 5 + 8 source bands with `maps_to`), `taxonomy_sources.yaml` (18 cited sources, URLs from the spec / R-01 only). `charging_links` appended to `config/countries/{nl,de,fr,be,uk}.yaml`. EN + NL label and short on every row; de/fr/es/it are absent (the schema has no `review: needed` field), so they fall back to EN.

**Links per country** (spec per-country table, URLs copied from the spec): NL 4 Chargemap, ABRP, Chargeprice, PlugShare · DE 4 Bundesnetzagentur Ladesäulenkarte (`official: true`), ABRP, Chargemap, Chargeprice · FR 4 Chargemap, ABRP, Chargeprice, Electromaps · BE 4 Chargemap, ABRP, Chargeprice, PlugShare · UK 3 Zapmap, ABRP, PlugShare. Jobs use the schema enum (`official-map`, `local-app`, `map`, `route-planner`, `price-compare`). Checked with the web loader (`loadChargingLinks()` and `loadListingConfig()` both pass; read-only, no files written).

**Gaps / judgement calls (Q-057).** No Open Charge Map 5th slot (not in the per-country table). The DE URL is the BNetzA E-Mobilität start page as the spec gives it, maybe not the map page. `verified: false` can't be written (web loader rejects unknown keys), so it is a comment per file: no link has been opened by hand. Schema `label` is LocalizedText but the web loader wants a string; YAML follows the web loader. No DC <50 kW band of ours. DfT slow/fast, AFDC and Avere bands below 150 kW left out (no band limits in the spec). `be` fully-public 24/7 series not added (spec gives no source for the ~22k figure).

**WS2:** `apps/web/src/config/charging-links.generated.json` is still the empty version; `next build`/`dev` regenerate it (`node scripts/charging-links.mjs`), but the committed copy should be regenerated in the web lane.

**Checks.** `python3 -I data/taxonomy/validate_taxonomy.py` 0 errors (7 old warnings); `--self-test` 22/22 (11 new cases: dangling route/source/maps_to/replaced_by, kW overlap, short > 20 words, `{param}` mismatch, missing spec id, invented link URL, > 5 links, job outside the enum). The validator also requires every link URL to appear in `docs/spec/charging-buildout.md`.

**Pipeline.** `pipeline/ev_pipeline/release/taxonomy.py` loads the optional tables into `catalogue.taxonomy` (only next to the base four, which `Taxonomy` requires), re-checks cross-refs, and holds back `bidi_equipment` rows whose sources aren't releasable. Release-time allowed-value check for `iso15118_20_support` / `heat_pump` (enums read from the schema) and `drag_coefficient` (0–1 or `not-disclosed`) in `release/validate.py`: bad facts are dropped and listed, plus a final guard on the published facts. No such facts exist yet. Tests: `pipeline/tests/test_release_taxonomy.py` (22). Release 1 rebuilt: 195 rows, gz catalogue 153,314 bytes (the 10 new tables add ~10.6 KB gz), all 457 pipeline tests pass, ruff clean on release/ and the new test (repo-wide ruff currently fails on another builder's in-progress `qa/checks.py` and `tests/test_net.py`).

## Review
