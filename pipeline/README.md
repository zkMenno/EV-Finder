# EV Finder pipeline

Python jobs that turn open sources into numbered catalogue releases. Agent rules: `AGENTS.md`.

## Run the pipeline

From `pipeline/`:

```sh
uv sync                               # install runtime + dev tools

# 1. Sources -> data/staging/<source>.records.jsonl (network; T-004 adapters)
uv run ev fetch openev && uv run ev normalise openev
uv run ev fetch rdw    && uv run ev normalise rdw
uv run ev fetch eea    && uv run ev normalise eea
#    offline, from the recorded samples instead:
#    uv run ev normalise openev --from-fixtures   (same for rdw, eea)

# 2. Match, merge, derive, validate, publish
uv run ev release --dry-run           # compute everything, print the summary, write nothing
uv run ev release                     # write data/releases/<n>/ and data/releases/latest

# Checks
uv run pytest && uv run ruff check . && uv run ruff format --check .
```

`EV_DATA_DIR=/some/dir uv run ev release` runs against another data folder (same layout).

### What `ev release` reads

| Path | What | Required |
|---|---|---|
| `data/seed/models.yaml` | Make → Model → Generation seed; `name_aliases`, `name_excludes` ("e-tron GT" is not an e-tron) and `bev_only_aliases` (bare RDW/EEA names like `KONA`, used for BEV-filtered sources only) for matching | yes |
| `data/staging/*.records.jsonl` | one `SourceRecord` per line (`ev_pipeline/records.py`) | no |
| `data/seed/variants.yaml` | hand-entered variants, source `seed-manual` | no |
| `data/sources.yaml` | licence gate: only `status: active` with a named, confirmed licence (or `permission: written`) is released | **yes*** |
| `data/field_sources.yaml` | per-field source order, tolerance and merge mode | no |
| `data/taxonomy/*.yaml`, `data/seed/{platforms,battery_packs,variant_links}.yaml` | Decision 010 platforms, packs, voltage | no |

\* Without `sources.yaml` the release fails (fail closed). Licences that are `none`/`unknown` or still
"(to confirm)" never pass unless the source has `permission: written`. `nyland` never reaches a
release, whatever the registry says. EEA records are used for registration counts only; its
registration-weighted spec averages are not facts (Q-039).

### What it writes

- `data/releases/<n>/catalogue.json`: schema `Catalogue` (compact JSON, numbers to 1 decimal),
  `catalogue.parquet` (same rows, flat), `facts.parquet` (every fact merged in), `diff.json`
  (vs the previous release), `coverage.md`, `README.md` (counts, licences, attribution),
  `run_log.json` (inputs, outputs, outcome).
- `data/releases/latest`: the newest release number. Roll back by writing an older number.
- `data/review/unmatched.csv` (records we could not place; other makes summarised),
  `validation.csv` (values dropped: out of range, bad unit), `conflicts.csv` (values outside
  the field tolerance of the winner; never averaged in).

A release fails, and writes nothing, when any row or fact breaks the JSON Schema or the
generated Pydantic models, a number lacks provenance, an excluded or non-active source shows up,
an ODbL source is present, a taxonomy/platform/pack id is unknown, or `data/sources.yaml` is missing.

### Stages (code)

| Stage | Code | Rules |
|---|---|---|
| Match | `ev_pipeline/match/` | normalise names, seed aliases and excludes, generation by year (shared years by variant-name/battery evidence, else newer, else `ambiguous-generation` to review), variant id `<generation>-<slug(name)>`, year bands `<variant>-<year>` when WLTP moves >5% or DC peak >10% |
| Merge | `ev_pipeline/merge/` | field policy (priority / median / newest) or default majority → priority → earliest model year → recency; confidence and conflicts |
| Derive | `ev_pipeline/derive/` | consumption, charging curve maths, motorway km in 10/20 min, real-range ladder, era, tier, pack inheritance, voltage class |
| Release | `ev_pipeline/release/` | range checks, licence gate, schema checks, numbering, diff, coverage, files |

All provisional constants (body ratios, default charge curve, motorway factor, net/gross) are
documented at the top of `ev_pipeline/derive/metrics.py`.
