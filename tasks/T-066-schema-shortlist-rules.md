# T-066 Schema for shortlist rules, owner picks and missing scoring fields
Role: coordinator   Lane: packages/schema   Wave: 9
Status: todo

## Goal
Give `data/editorial/` a schema so rules and picks are validated and typed (Decision 038).

## Acceptance criteria
- [ ] `ShortlistProfile` (gates, factors with field / poor / great / weight, bonuses, penalties, bands per voltage class) and `EditorialPick` (seed ids, verdict enum shortlist|consider|fallback|ruled_out|unrated, favourite, flags, tier, notes; `sheet_values` marked internal and stripped from any published type)
- [ ] New variant fields the rules need, all optional, `not-disclosed` allowed: `frunk_l`, `one_pedal` (yes / via setting / no), `regen_paddles`, `width_mm`, `ota_updates`
- [ ] Move `data/editorial/shortlist_rules.yaml` to `data/taxonomy/shortlist_rules.yaml`, wire into `validate_taxonomy.py`; update `backtest_rules.py` path
- [ ] Fixtures valid + invalid

## Inputs
`data/editorial/shortlist_rules.yaml`, `data/editorial/menno-picks.yaml`, research/R-32, trip-fit §6 (`usage_profiles`: align factor ids).

## Out of scope
UI, scoring job.
