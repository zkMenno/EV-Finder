# T-018 Schema: bidirectional capability, charging ports, ISO 15118-20 fact
Role: coordinator   Lane: packages/schema   Wave: 5
Status: todo

## Goal
Add the types from docs/spec/bidirectional-and-connectors.md §3 so data and web lanes can build on them.

## Acceptance criteria
- [ ] `$defs` for BidiMode, BidiRoute, BidiProtocol, BidiCaveat (with optional param), BidiStatus, ConnectorType, BidiEquipment, BidiCapability, ChargingPort; variant Fact `iso15118_20_support`
- [ ] Taxonomy ids are free strings validated against data/taxonomy at release time (same pattern as Decision 010)
- [ ] Valid + invalid fixtures for BidiCapability and ChargingPort; generated TS + Python types updated
- [ ] PublishedVariant carries `bidi[]` and `ports[]` (market + model year keyed)

## Inputs
docs/spec/bidirectional-and-connectors.md, research/R-01-bidirectional-and-connectors.md, Decision 010, 011.

## Out of scope
Seed data, UI.

## Handoff notes

## Review
