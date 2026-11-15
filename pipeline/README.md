# EV Finder pipeline

Python jobs that turn open sources into numbered catalogue releases. Agent rules:
[`AGENTS.md`](AGENTS.md). Source list: [`data/SOURCES.md`](../data/SOURCES.md) (human) and
[`data/sources.yaml`](../data/sources.yaml) (machine registry, coordinator-owned).

## Quick start

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/). From `pipeline/`:

```sh
uv sync                                   # runtime + dev tools (CI: uv sync --locked --all-extras --dev)
uv run ev --help                          # subcommands: version, fetch, normalise, release
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
**Rollback:** write an older number into `latest`.

**A release folder** `data/releases/<n>/` contains:

| File | What |
|---|---|
| `catalogue.json` | schema `Catalogue`, one wide row per variant (compact, numbers to 1 decimal). The web app reads this. |
| `catalogue.parquet`, `facts.parquet` | the same rows flat; every merged fact with its provenance |
| `diff.json` | added / removed / changed vs the previous release |
| `coverage.md` | how many rows have each field, and from which source |
| `qa.json`, `qa.md` | release QA (R-05 §1): blocking checks plus review items, and the `backtest` section (scores the real-range ladder on `data/backtest/*.jsonl`; `skipped` when there are none) |
| `README.md`, `run_log.json` | counts, licences, attribution; inputs, outputs, outcome |
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
