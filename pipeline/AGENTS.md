# AGENTS.md — pipeline/

Lane rules for the Python data pipeline. The root `AGENTS.md` still applies; this file adds to it.

## Layout

```
pipeline/
  pyproject.toml          uv project (package `ev_pipeline`, CLI `ev`)
  uv.lock                 committed; update with `uv lock`
  ev_pipeline/
    cli.py                `ev <subcommand>`; add yours in build_parser()
    schema_models.py      GENERATED from packages/schema; never edit (ruff skips it)
    sources/<name>/       one folder per source adapter
    merge/  derive/  release/   one folder per pipeline stage
  tests/
    fixtures/<name>/      small, licence-clean samples per source
    test_*.py
```

Source adapters live at `pipeline/ev_pipeline/sources/<name>/` (this supersedes the
`pipeline/sources/<name>/` path in the root AGENTS.md). Fixtures for a source live in
`pipeline/tests/fixtures/<name>/`.

## Rules

1. **Every Fact carries source, retrieval date, licence and confidence.** No value without
   all four. A missing field is a bug, not a default.
2. **No network in tests.** Tests read fixtures only. Network code takes an injectable
   `httpx.Client` (or transport) so tests can swap in `httpx.MockTransport`.
3. **Each step writes a run log**: what it read (inputs, with source and version/date),
   what it wrote (outputs, row counts), when, and the outcome. Steps are small and idempotent:
   re-running with the same inputs gives the same outputs.
4. **Licences stay separate.** Record each source's licence and attribution; never mix
   ODbL inputs into CC BY outputs.
5. **Raw data is not committed.** Raw fetches go to `data/cache/` (git-ignored) or object
   storage. Permission-pending sources (e.g. the Bjørn Nyland sheet) go to `data/local/`
   only (git-ignored) and never into fixtures or releases until permission is logged.
6. **Types come from `packages/schema`.** Don't hand-write models that the schema defines.
7. **Metric units internally** (km, kWh, Wh/km, kW, °C, €).
8. **Respect the shared server**: low memory, nightly jobs (Decision 006).

## Commands

```sh
cd pipeline
uv sync                      # installs runtime + dev group
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ev version
```

Fallback without uv: `pip install -e ".[dev]"` (dev extras mirror the uv dev group; keep
them in step when you add a dev tool).
