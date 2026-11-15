# T-047 Look-alike groups and clue validation in the pipeline
Role: WS1   Lane: pipeline   Wave: 7
Status: todo

## Goal
Build look-alike groups automatically and check clues at release time.

## Acceptance criteria
- [ ] Groups from overlapping specs within a generation, same badge, or same marketing name across markets; staff overrides in data/manual
- [ ] Release checks: every clue's rules_out variants exist and share its group; a decisive clue really separates its variants (values don't overlap)
- [ ] Clues shipped in the release; the same clue rules exposed as a matching function for listing matching later (§8)

## Inputs
docs/spec/variant-finder.md §4, T-044, T-046.

## Out of scope
Listing feeds.

## Handoff notes

## Review
