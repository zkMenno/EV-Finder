# T-025 charging_stats job and loaders
Role: WS1   Lane: pipeline/ev_pipeline/sources, data/sources.yaml   Wave: 6
Status: merged (PR #7); fresh review via QA A-35; earlier note: WS1, 2026-11-15

## Goal
Monthly job that loads official charging statistics into charging_stats with one definition per series.

## Acceptance criteria
- [x] Loaders for EAFO, Bundesnetzagentur, DfT (fixtures only in tests)
- [x] Manual YAML path data/manual/charging/*.yaml (WS3 writes) loaded with required source URL
- [x] Licence checked and recorded per download in data/sources.yaml; unclear → blocked from release
- [x] Release diff flags >15 % month-on-month change or any drop
- [x] Runs inside 00:30–02:30 UTC within 1 GB

## Inputs
Decision 012, docs/spec/charging-buildout.md, T-023, T-024. RVO is blocked (share-alike, overnight R- note).

## Out of scope
Country pages (T-028), US/AU (phase 4).

## Handoff notes
Pipeline builder, overnight 2026-11-15 (ADDENDUM-6 P6). Loaders done; integration open.
- `ev fetch|normalise eafo|bnetza|dft-charging` write `data/staging/<id>.charging_stats.jsonl` (ChargingStat rows, jsonschema-validated, ids checked against data/taxonomy, rows outside a definition's valid_from/valid_to dropped) and `<id>.charging_stats.meta.json` (licence, attribution, download URL + sha256, licence text seen, status, `releasable`).
- Live 2026-11-15: EAFO 898 rows (blocked, Q-077), BNetzA 2,720 (CC BY 4.0, Stand 01.10.2026), DfT 141 (OGL v3, 1 July 2026). Aggregates only; the BNetzA point list is never fetched.
- Open: manual YAML path (`data/manual/charging/*.yaml`), release diff (>15 % / drops), scheduling. Id spaces and taxonomy gaps: Q-075, Q-076. Shared helper: `pipeline/ev_pipeline/sources/eafo/charging_stats.py`.

**WS1, 2026-11-15 (PR `t-025-charging-stats`).**
- EAFO now ships (Decision 037): `active_pending_confirmation` is a releasable status
  (`gate.RELEASABLE_STATUSES`); live run today: 898 EAFO, 2,720 BNetzA, 141 DfT rows, all ship.
- Manual YAML: `data/manual/charging/*.yaml`, format in
  `pipeline/tests/fixtures/manual/charging/example.yaml` (sent to WS3). Same gate and row
  checks; `source_url` required; downloads win on duplicates.
- Release diff: `charging_review_rows` → `data/review/charging_changes.csv` (review only).
  ">15 % month-on-month" is applied as a compound monthly rate so EAFO's yearly rows don't
  flag normal growth (601 → 25 flags on today's data); any fall, revision or vanished
  series/date is flagged too. Today vs release 1: 65 rows, all EAFO (new series baseline).
- `ev refresh`: the runner used `<id>.records.jsonl` for every source, so charging sources
  and rdw-defects counted as "wrote no records". Adapters now declare `STAGING_SUFFIX`.
- Night window + 1 GB: each job peaks under 90 MB, under 5 s (measured live). Scheduling
  in the 00:30–02:30 UTC window is WS4's pg-boss/cron job.
- Q-075 / Q-076 defaults kept as engineering choices (proposed Decision 040 in WS0's INBOX):
  taxonomy ids on stats + registry aliases; unknown bands skipped and counted; taxonomy
  gaps (power bands, DfT valid_from, dc-50-plus) sent to WS3.
- Depends on PR #4 (T-064) and PR #5 (sources.yaml) — branch contains both; merge those first.

## Review
