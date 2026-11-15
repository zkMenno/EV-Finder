# EV Finder pipeline

Python jobs that turn open sources into numbered catalogue releases. Agent rules:
[`AGENTS.md`](AGENTS.md). Source list: [`data/SOURCES.md`](../data/SOURCES.md) (human) and
[`data/sources.yaml`](../data/sources.yaml) (machine registry, coordinator-owned).

## Quick start

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/). From `pipeline/`:

```sh
uv sync                                   # runtime + dev tools (CI: uv sync --locked --all-extras --dev)
uv run ev --help                          # version, fetch, normalise, release, refresh, sources, …
uv run pytest -q                          # all tests, no network (~680 tests, a few seconds)
uv run ruff check . && uv run ruff format --check .
```

Fallback without uv: `pip install -e ".[dev]"`.

### Offline run on the recorded samples

`normalise --from-fixtures` reads `tests/fixtures/<source>/` and **overwrites**
`data/staging/<source>.records.jsonl`. To keep the real staging data, point `EV_DATA_DIR` at a
scratch copy (same layout as `data/`):

```sh
export EV_DATA_DIR=$(mktemp -d)
cp -r ../data/{seed,taxonomy,releases,sources.yaml,field_sources.yaml} "$EV_DATA_DIR"/
for s in openev rdw eea dft-veh kba-fz10 ademe kilowatt-openev nyland; do
  uv run ev normalise "$s" --from-fixtures
done
uv run ev release --dry-run               # computes everything, prints the summary, writes nothing
```

(`nyland` writes to `local/nyland/`, never to `staging/`; see below.)

### Real run (network)

```sh
uv run ev fetch rdw && uv run ev normalise rdw        # same for each source id
uv run ev release --dry-run                           # check the summary and diff first
uv run ev release                                     # writes data/releases/<n>/ and data/releases/latest
```

Heavy fetches (DfT ~65 MB, OpenEV clone) belong on your machine or a temporary box, not on the
shared server (Decision 006).

## Keeping data fresh

One command does the whole loop for every source that is due (cadence in `data/sources.yaml`):

```sh
uv run ev refresh --dry-run      # what would run, plus cheap "changed?" probes; writes nothing
uv run ev refresh                # fetch → snapshot → fingerprint → normalise → release → QA
uv run ev refresh --sources rdw,ademe   # just these, now (ignores cadence)
uv run ev refresh --force        # every refreshable source, now
uv run ev sources check          # one table: status, last success / change, records, fingerprint
```

**What happens per source** (`ev_pipeline/refresh/runner.py`):

1. **Probe.** Git sources: `git ls-remote` vs the last commit. HTTP sources: a conditional
   `HEAD` per URL when the last fetch had ETag / Last-Modified (`304` = unchanged). An adapter
   can add its own check (`probe_unchanged`). Unchanged → done, nothing downloaded.
2. **Fetch** with the adapter's own `fetch_cmd()` (safe client, streaming). Every response's
   URL, status, ETag and Last-Modified are recorded without touching the adapter
   (`snapshot/recording.py` wraps `net.safe_client` during the fetch).
3. **Snapshot** of `data/raw/<dir>/` into the store (content hash per file and per tree).
   Same hash as the accepted data → unchanged, nothing else runs.
4. **Fingerprint** (column names / key paths and types). A column or file group that was
   there before and is gone **fails closed**: raw is restored from the snapshot, staging is
   untouched, an item goes to `data/review/source-health.csv`. New columns are only reported.
5. **Normalise.** If it fails, or yields under half the previous records, the old staging file
   is put back (and a review item is written for the drop).

A release is built only if some source brought new data, and published only if the catalogue
actually changed, no source of the latest release lost its staging file, and blocking QA
passes. Each run writes `data/runs/<timestamp>.json` (per step: seconds, outcome, rows,
peak memory) and updates `data/runs/sources-state.json`. Exit code: `0` ok, `1` the release
failed (see `data/review/qa.md`), `3` a source failed or drifted (its previous data is kept).

**After a refresh, check** `data/releases/<n>/qa.md` (blocking checks must say pass; read the
flagged items), `uv run ev release diff <n-1> <n>` (what changed, with examples), and
`uv run ev sources check` (any `drift`, `failed` or `rows_dropped`).

**Undo:**

```sh
uv run ev release list                 # releases, QA status, which one is latest
uv run ev release rollback --to 3      # latest -> 3 (atomic; refuses releases without passed QA)
uv run ev release diff 3 latest --json # machine-readable diff
```

Rollback deletes nothing; the next release still takes the highest number + 1.

**Schema drift or a big drop, after you checked the review item:**
`uv run ev sources accept <id>` re-fetches that source and accepts its new shape.

**Snapshot store** (`snapshot/store.py`): `SNAPSHOT_BACKEND=local` (default) keeps blobs and
manifests in `$SNAPSHOT_DIR` (default `data/snapshots/`, git-ignored). `SNAPSHOT_BACKEND=s3`
(Scaleway, `S3_*` env vars) has the same interface but is **not built yet**: it raises a clear
error. Until then, copy `data/snapshots/` to object storage by hand if you need off-machine
history.

**Memory:** the 2026-11-15 run of all seven open sources peaked at 223 MB (git children
122 MB), well inside the 1 GB `ev-jobs` limit (Decision 006). RDW is the slow one (~4.5 min:
paged queries with a 1 s pause); the others take 1–6 s each.

**Automatic updates:** `.github/workflows/data-refresh.yml` runs `ev refresh --force` every
Monday 03:17 UTC (and on demand, optionally with a source list). When a new release passes QA
it opens a pull request "Data release N" with only `data/releases/N/` and `latest`; merge it to
publish, or close it. Raw data, snapshots and run logs never leave the runner. Sources that need
a key are skipped. Later, on the server, the same command runs as a pg-boss job (Decision 021).

**For adapter builders:** nothing to change for `ev refresh`. Optional one-liners: call
`snapshot.recording.record_client(client, recorder)` if you build clients outside
`net.safe_client`; add `probe_unchanged` when a cheaper change check exists. RDW already has one: it compares the
datasets' `rowsUpdatedAt` and skips the ~265 s refetch when nothing changed.

## Steps

| Step | Command / code | What it does |
|---|---|---|
| Fetch | `ev fetch <src>`, `sources/<src>/adapter.py` | Downloads raw data to `data/raw/<src>/` (git-ignored) plus `_fetch.json` (time, query, licence text seen). Some adapters refuse to run if the licence text changed (EEA, KBA). |
| Normalise | `ev normalise <src>` | Raw → `data/staging/<src>.records.jsonl`, one `SourceRecord` per line (`ev_pipeline/records.py`), each with its `Source` and licence. Appends to `data/staging/runlog.jsonl`. |
| Match | `ev_pipeline/match/` | Places records on the seed (`data/seed/models.yaml`): name normalisation, aliases and excludes, generation by year, variant id `<generation>-<slug(name)>`, year bands when WLTP moves >5 % or DC peak >10 %. Unplaced records → `unmatched.csv`. |
| Merge | `ev_pipeline/merge/` | Per-field policy from `data/field_sources.yaml` (priority / median / newest), else majority → priority → earliest model year → recency. Values outside tolerance → `conflicts.csv`, never averaged. |
| Derive | `ev_pipeline/derive/` | Consumption, charge-curve maths, motorway km per 10/20 min, real-range ladder, era, tier, pack inheritance, voltage class. Provisional constants are documented at the top of `derive/metrics.py`. |
| Release | `ev release`, `ev_pipeline/release/`, `qa/`, `opendata/`, `backtest/` | Range checks, licence gate, schema checks, QA, numbering, diff, coverage, open-data bundle, files. |

## Sources

Active and imported (details, exact licence text and attribution lines in
[`data/SOURCES.md`](../data/SOURCES.md)):

| id | What | Licence |
|---|---|---|
| `openev` | Specs and DE prices (Open EV Data) | CDLA-Permissive-2.0 |
| `kilowatt-openev` | Fallback specs, DC curves (all `estimated`); attach-only | MIT with attribution (visible credit required) |
| `rdw` | NL registered BEV fleet | CC0-1.0 |
| `eea` | New BEV registrations NL/DE/FR/BE (counts only; spec averages are not facts, Q-039) | CC BY 4.0 |
| `kba-fz10` | DE new registrations, year-to-date | dl-de/by-2-0 |
| `dft-veh` | UK licensed BEV fleet at quarter end | OGL-UK-3.0 |
| `ademe` | FR list prices, best-case WLTP, mass; attach-only | Licence Ouverte 2.0 |
| `seed-manual` | Hand-entered seed variants (`data/seed/variants.yaml`), low confidence | CC BY 4.0 |
| `nyland` | Real-world tests; **permission pending, never released** | none |

Attach-only sources (`ATTACH_ONLY_SOURCES` in `match/matcher.py`) add facts to existing
variants and never create rows. Everything else in `sources.yaml` is either not imported yet or
`blocked` / `waiting_permission`.

## Releases

**Numbering:** plain integers counting up from 1 (Decision 008): the next release is the
highest existing `data/releases/<n>/` + 1. `data/releases/latest` holds the current number.
**Rollback:** `uv run ev release rollback --to <n>` (see "Keeping data fresh").

### Releases live outside git (T-064, Decision 035)

Git keeps only `data/releases/<n>/manifest.json` plus the small files listed under `in_git`
in `data/releases/publish.yaml` (README, QA report, coverage, diff). Every other file
(catalogue, parquet, charging stats, open bundle, the per-generation split) is an asset of the
GitHub Release `data-v<n>`. `.gitignore` keeps the big files out; a test keeps `.gitignore`
and `in_git` in step.

```sh
uv run ev release package 1     # per-generation split + manifest.json (ev release does this too)
uv run ev release verify 1      # local files vs manifest (size + sha256)
uv run ev release fetch latest  # download what git doesn't hold; every file sha256-checked
uv run ev release publish 1 --target dir --out /tmp/store   # local mirror (tests, inspection)
uv run ev release publish 1     # GitHub Release data-v1 via `gh` (needs GH_TOKEN, contents: write)
```

- **manifest.json:** release number, dates, QA summary, storage (`data-v<n>`, download URL),
  counts, and every file with path, asset name, bytes, sha256 and `in_git`.
- **Per-generation split:** `catalogue/index.json` (all rows without `provenance`, taxonomy,
  sources; `generation_files` maps each generation id to its file) and
  `catalogue/generations/<generation_id>.json` (that generation, its full rows, its known
  issues). `catalogue.json` stays as the full file. `package` refuses a split that doesn't
  round-trip to `catalogue.json`.
- **Who uploads:** the weekly `data-refresh.yml` uploads assets when it opens the "Data release
  N" PR (re-runs replace an unmerged release only); `data-publish.yml` runs when a manifest
  lands on main (normally "unchanged") or by hand for a release still in git. Both use
  `pipeline/scripts/gh-publish-release.sh` (shell + jq + gh, no pipeline code in the write job).
  A release that has a manifest on main is never changed.
- **Who downloads:** the web build (`apps/web/scripts/fetch-release.mjs`, runs first in
  `pnpm build`/`dev`; `CATALOGUE_SOURCE=auto|manifest|local`), CI `data-qa`
  (`ev release fetch latest`), and the pipeline itself when it needs an older release (diff
  for the next release, rollback, `ev refresh`). A failed or wrong download is an error, never
  "no previous release".
- **Rollback** is unchanged: `ev release rollback --to <n>` points `latest` at an earlier
  release; its files are fetched and checked first, then the QA re-check runs. The web
  build after that fetches release n by its manifest. To preview without switching:
  `CATALOGUE_RELEASE=<n> node apps/web/scripts/fetch-release.mjs`.
- **Unmerged release PR closed?** Delete its GitHub Release (`gh release delete data-v<n>
  --cleanup-tag`) or let the next refresh replace it; the number is reused.

**A release folder** `data/releases/<n>/` contains:

| File | What |
|---|---|
| `catalogue.json` | schema `Catalogue`, one wide row per variant (compact, numbers to 1 decimal). The web app reads this. Optional sections (T-059): `known_issues` (RDW APK defects per generation × first-registration year), `generations[].years_corroboration` (Wikidata years, ±1), row field `epa_range_km`. |
| `catalogue.parquet`, `facts.parquet` | the same rows flat; every merged fact with its provenance |
| `diff.json` | added / removed / changed vs the previous release |
| `coverage.md` | how many rows have each field, and from which source |
| `qa.json`, `qa.md` | release QA (R-05 §1): blocking checks plus review items, and the `backtest` section (scores the real-range ladder on `data/backtest/*.jsonl`; `skipped` when there are none) |
| `README.md`, `run_log.json` | counts, licences, attribution; inputs, outputs, outcome |
| `charging_stats.json` | schema `ChargingStatsRelease` (T-059, Decision 012): aggregate charging statistics from gate-passed sources (BNetzA, DfT; EAFO stays out while blocked). Stat `source_id` is the taxonomy id; `source_aliases` maps it to the `data/sources.yaml` id (`aliases` there). |
| `sources.json` | health per source: status, last success, last change, "as of" date, records vs previous, schema fingerprint (staff page, Nerd mode) |
| `refresh.json` | only in releases made by `ev refresh`: per-source status and time, peak memory |
| `open/` | CC BY 4.0 open-data bundle (Decision 016): `variants.csv`, `variants.json`, `ATTRIBUTION.md`, `LICENSE`, `README.md`. Only gate-passed, non-ODbL sources; `<field>_sources` / `<field>_confidence` per value. Brand from `EV_BRAND_NAME`. |

Registration counts sit per country, source and period (`fleet` or `new_registrations`) and are
never added across sources, periods or kinds.

**Fails closed.** Nothing is written when: a row or fact breaks the JSON Schema or the generated
Pydantic models; a number lacks provenance; an excluded, non-active or ODbL source shows up; a
taxonomy/platform/pack id is unknown; or `data/sources.yaml` is missing. A blocking QA failure
writes `data/review/qa.{json,md}` instead.

**Licence gate** (`release/gate.py`): only `status: active` sources with a named, confirmed
licence (or `permission: written`) pass. `none`, `unknown` and "(to confirm)" licences fail.

### Review files (`data/review/`, rewritten by each release)

- `unmatched.csv`: records we could not place, with the reason (other makes summarised).
- `validation.csv`: values dropped (out of range, bad unit).
- `conflicts.csv`: values outside the field tolerance of the winner.

`coverage-gaps.md` there is a hand-written review note, not pipeline output.

### What `ev release` reads

| Path | Required |
|---|---|
| `data/seed/models.yaml` (Make → Model → Generation, aliases, excludes, `bev_only_aliases`, `source_aliases`) | yes |
| `data/sources.yaml` (licence gate) | yes |
| `data/staging/*.records.jsonl` | no |
| `data/seed/variants.yaml`, `platforms.yaml`, `battery_packs.yaml`, `variant_links.yaml` | no |
| `data/field_sources.yaml`, `data/taxonomy/*.yaml` | no |

Check the seed and taxonomy files by hand (needs PyYAML), from the repo root:

```sh
python3 -I data/seed/validate_seed.py data/seed/models.yaml   # add --self-test to check the validator
python3 -I data/seed/validate_variants.py
python3 -I data/taxonomy/validate_taxonomy.py                 # add --self-test likewise
```

## Adding a source

1. **Licence first.** Find the exact licence text and attribution line. No open licence and no
   written permission: stop and ask in `QUESTIONS.md`. ODbL never goes into a release.
2. **Registry** (coordinator edits it; ask in `QUESTIONS.md` or the WS0 inbox): an entry in
   `data/sources.yaml` with `id`, `name`, `owner`, exact `licence`, `access`, `cadence`,
   `status`, **`hosts`** (every host the fetcher may contact) and `terms`; a row in
   `data/SOURCES.md`.
3. **Adapter** at `ev_pipeline/sources/<id_with_underscores>/adapter.py`, following an existing
   one (`rdw` is the simplest):
   - `NAME` and `SOURCE` (schema `Source` with licence and attribution);
   - `fetch(client, target) -> int` and `normalise(raw_dir, retrieved_at) -> list[SourceRecord]`
     as pure functions;
   - `fetch_cmd(client=None)` building its client with `net.safe_client(NAME)`, writing
     `_fetch.json`, catching `httpx.HTTPError`;
   - `normalise_cmd(from_fixtures)` writing staging via `_common.write_records` and logging with
     `_common.log_step`. Retrieval date comes from `_fetch.json`, so re-runs are stable.
   - Add the id to `SOURCES` in `ev_pipeline/cli.py`.
   - Optional, for `ev refresh`: `REQUIRES_ENV = ["MY_API_KEY"]` (skipped when unset) and
     `probe_unchanged(client, previous_fetch_meta) -> bool | None`, a cheap "did it change?"
     check (see "Keeping data fresh").
4. **Fixture:** a small, licence-clean sample plus `_fetch.json` in
   `tests/fixtures/<id_with_underscores>/`. No permission-pending data in fixtures.
5. **Tests:** `tests/test_source_<id>.py` on the fixture; fetch tested with
   `httpx.MockTransport`. No network.
6. **Field rules:** add the id to the right fields in `data/field_sources.yaml`. If the source is
   BEV-only, or needs attach-only or per-source aliases, say so in the PR (seed and
   `match/matcher.py` live in other lanes).
7. Run `normalise --from-fixtures` and `release --dry-run` on a scratch `EV_DATA_DIR` and check
   `unmatched.csv` and the diff.

## Safe fetch rules (`ev_pipeline/net.py`)

Every HTTP fetch goes through `net.safe_client(source_id)`, which on every request and redirect:

- allows only `https` on the default port to hosts listed under that source's `hosts:`
  (`*.example.org` = subdomains only); IP literals and user info refused;
- resolves the host once, requires every address to be public, and connects to that checked
  address (no DNS rebinding);
- enforces timeouts, a total time budget and a size cap (also after gzip decoding). Stream large
  files with `client.stream(...)`;
- ignores environment proxies, and never puts URL paths or queries in error messages.

Git-cloned sources (`openev`, `kilowatt-openev`) don't go through `net.py`; their `hosts:` entry
records the egress. Respect robots.txt and site terms; never scrape marketplaces (Decision 004).

## Nyland exclusion

The Bjørn Nyland sheet is permission-pending. Its URL lives only in the `NYLAND_SHEET_CSV_URL`
env var. `fetch` and `normalise` write to `data/local/nyland/` (git-ignored), never to
`data/staging/`. The matcher drops `nyland` (`EXCLUDED_SOURCES`) and the release gate refuses it
whatever `sources.yaml` says. Tests use an invented CSV only.

## Coverage

```sh
uv run --with pytest-cov pytest --cov=ev_pipeline --cov-report=term-missing -q
```

pytest-cov is pulled in for the run only; it is not a project dependency. On 2026-11-15: 680
tests, 96 % overall (the gaps are mostly adapters' network paths and `match/`).

## Charging statistics (T-025, Decision 012)

Aggregates only, never point data. Three loaders (`ev fetch|normalise eafo|bnetza|dft-charging`)
write `data/staging/<id>.charging_stats.jsonl` + `.meta.json`; `ev refresh` runs them on their
cadence (adapters declare `STAGING_SUFFIX`, so the runner checks the right staging file).
Measured 2026-11-15 (live): each fetch + normalise under 90 MB peak and under 5 s.

- **Gate:** a file ships only when its source passes the licence gate (`active`, or
  `active_pending_confirmation` for EAFO, Decision 037) and its meta says `releasable: true`.
- **Manual figures:** `data/manual/charging/<name>.yaml` (WS3 writes), format in
  `tests/fixtures/manual/charging/example.yaml`: `schema: manual-charging/v1`, `source_id`,
  `stats:` rows like ChargingStat without `entered_by` (set to `staff`); `source_url`
  required. A manual copy of a downloaded figure is dropped (the download wins).
- **Review, not block:** `data/review/charging_changes.csv` lists figures that grew more than
  15 % a month (compound, so yearly series compare fairly), fell, were revised, or vanished
  since the previous release. The first release of a series checks its whole history once.

## Towns and climate (T-034, Trip fit)

`ev fetch|normalise geonames` then `ev fetch|normalise meteostat` (order matters: Meteostat
picks stations near the towns). The release writes `towns/<country>.json` per launch country:
towns (GeoNames cities5000, names in our six languages, coordinates rounded to ~1 km), the
stations they use, and `provenance` for both. Climate per station, 1991–2020: monthly means of
daily mean temperature, January mean, and P10 = 10th percentile of January daily means.

- A town takes the nearest station within 60 km and 250 m of its elevation, preferring one
  with a P10; no interpolation. Live 2026-11-15: 7,654 towns, 7,203 with climate (FR and
  rural UK have gaps), 10 without P10. Fetch ≈ 2 min, 1,000 stations tried, < 200 MB RAM.
- Meteostat is CC BY 4.0 (its own redistribution, R-27); credit "Meteostat and its data
  providers"; confidence medium. ERA5-Land (primary, Decision 036) is a stub until the CDS key
  arrives (`CDSAPI_KEY`, WS4); `ev refresh` skips it until then.

## Manual facts and the review queue

**Manual facts** are single values a person looked up by hand (a warranty booklet, a maker
spec sheet), one cited fact each, in `data/manual/<topic>/<name>.yaml`. Copy the layout from
`data/manual/_example/example.yaml` (a fixture: its ids exist only in the test fixtures).

```yaml
schema: manual-facts/v1
entered_by: menno                 # default for the file; a fact can override it
facts:
  - variant_id: some-variant-id   # or generation_id: applies to every variant of it
    field: warranty_years         # a schema FactField
    value: 8
    unit: years                   # must be the field's canonical unit (km, kWh, kW, ...)
    country: NL                   # optional; required for price_new (unit EUR or GBP)
    source_url: https://...       # required
    source_name: "Warranty booklet 2024"   # optional
    retrieved: 2026-11-15         # required, not in the future
    locator: "p. 4, table 2"      # a locator and/or a quote is required
    quote: "8 jaar of 160.000 km"
    confidence: medium            # high | medium | low
    claim: true                   # default true (maker documents are claims)
    notes: "..."                  # optional
```

- `uv run ev manual check` validates every file: the schema `Fact` def plus the rules above,
  plausible ranges and enum values (same checks as the release), and no duplicate
  (subject, field, country). Unknown variant/generation ids are warnings. Exit 1 on errors.
- `ev release` loads them as source `manual`. **Internal only until Q-008 is answered:**
  `manual` is `blocked` in `data/sources.yaml`, so the licence gate drops them (listed under
  `gated_sources` in the run log). Bad entries go to `validation.csv` with stage `manual`.
  Folders starting with `_` and files with `fixture: true` are never loaded by a release.
- Once releasable, add `manual` to `data/field_sources.yaml` where it should win; without
  that it ranks above `seed-manual` and below EEA/OpenEV (`MANUAL_PRIORITY`).

**Review queue.** Every row of `data/review/*.csv` starts with `review_id` and `status`
(`open | done | wont-fix`). The id is a short hash of source, record key and reason
(`um-` unmatched, `va-` validation, `cf-` conflicts); counts such as "(4x)" are left out, so
the same problem keeps its id across rebuilds. Staff decisions live in
`data/review/status.yaml`, keyed by `review_id`; set them there (optional `note`) or in a
CSV's `status` column, and the next `ev release` copies CSV edits into status.yaml before it
rewrites the CSVs. Entries are never dropped, so a problem that comes back keeps its status.
Code: `ev_pipeline/manual/facts.py`, `ev_pipeline/commands/manual.py`,
`ev_pipeline/review_queue.py`.
