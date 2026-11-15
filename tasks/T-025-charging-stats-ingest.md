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

## Review
