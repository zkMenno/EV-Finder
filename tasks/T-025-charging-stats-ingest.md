# T-025 charging_stats job and loaders
Role: WS1   Lane: pipeline/ev_pipeline/sources, data/sources.yaml   Wave: 6
Status: todo

## Goal
Monthly job that loads official charging statistics into charging_stats with one definition per series.

## Acceptance criteria
- [ ] Loaders for EAFO, Bundesnetzagentur, DfT (fixtures only in tests)
- [ ] Manual YAML path data/manual/charging/*.yaml (WS3 writes) loaded with required source URL
- [ ] Licence checked and recorded per download in data/sources.yaml; unclear → blocked from release
- [ ] Release diff flags >15 % month-on-month change or any drop
- [ ] Runs inside 00:30–02:30 UTC within 1 GB

## Inputs
Decision 012, docs/spec/charging-buildout.md, T-023, T-024. RVO is blocked (share-alike, overnight R- note).

## Out of scope
Country pages (T-028), US/AU (phase 4).

## Handoff notes
Pipeline builder, overnight 2026-11-15 (ADDENDUM-6 P6). Loaders done; integration open.
- `ev fetch|normalise eafo|bnetza|dft-charging` write `data/staging/<id>.charging_stats.jsonl` (ChargingStat rows, jsonschema-validated, ids checked against data/taxonomy, rows outside a definition's valid_from/valid_to dropped) and `<id>.charging_stats.meta.json` (licence, attribution, download URL + sha256, licence text seen, status, `releasable`).
- Live 2026-11-15: EAFO 898 rows (blocked, Q-077), BNetzA 2,720 (CC BY 4.0, Stand 01.10.2026), DfT 141 (OGL v3, 1 July 2026). Aggregates only; the BNetzA point list is never fetched.
- Open: manual YAML path (`data/manual/charging/*.yaml`), release diff (>15 % / drops), scheduling. Id spaces and taxonomy gaps: Q-075, Q-076. Shared helper: `pipeline/ev_pipeline/sources/eafo/charging_stats.py`.

## Review
