# T-023 Schema: charging stats, charging taxonomies, abrp_typecode
Role: coordinator (WS0)   Lane: packages/schema   Wave: 6
Status: todo

## Goal
Add the types from Decision 012 so WS1 and WS3 can build on them.

## Acceptance criteria
- [ ] `$defs` ChargingStat, ChargingMetric, ChargingDefinition, PowerBand, CountryChargingLink
- [ ] Variant field `abrp_typecode` (nullable string)
- [ ] Valid + invalid fixtures; generated TS + Python types updated
- [ ] Taxonomy ids validated against data/taxonomy at release time (Decision 010 pattern)

## Inputs
docs/spec/charging-buildout.md (Data model), Decision 012.

## Out of scope
Seed rows, ingest, UI.

## Handoff notes

## Review
