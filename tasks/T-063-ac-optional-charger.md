# T-063 Optional on-board charger field
Role: coordinator (schema) + WS1 + WS2   Lane: packages/schema, pipeline, apps/web   Wave: proposed by overnight 1
Status: todo

## Goal
Decision 034: `ac_kw` = standard on-board charger; add `ac_kw_optional`. Route source values to the right field (field_sources rules per source), cite both where official sources give both, show "7.4 kW (11 kW optional)" in the web app.

## Acceptance criteria
- [ ] Additive schema field `ac_kw_optional` (coordinator)
- [ ] Per-source routing rules in field_sources.yaml; cited standard values win under Decision 028/031
- [ ] Web shows both through `Num` with provenance, EN + NL
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
DECISIONS.md 034, audits/A-06 follow-up table.

## Out of scope
Anything not named above.

## Handoff notes

## Review
