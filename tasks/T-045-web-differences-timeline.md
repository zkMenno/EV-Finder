# T-045 Differences-only toggle and variant change timeline (Core)
Role: WS2   Lane: apps/web   Wave: 7
Status: todo

## Goal
Show what actually differs between variants of a generation, and when it changed.

## Acceptance criteria
- [ ] Toggle on generation pages and Compare hides specs all variants share; differing cells highlighted colour-blind safe (shape or weight, not colour alone; UX supplies the style)
- [ ] Plain-language deltas ("+13 kWh, about +70 km winter range") using our own range model, labelled estimate
- [ ] Timeline strip from generation change markers ("heat pump standard from 03/2021")
- [ ] Toggle state in the URL; works at 360 px; computed at build time, no new data

## Inputs
docs/spec/variant-finder.md §2 features 1–2.

## Out of scope
Clue box (T-048).

## Handoff notes

## Review
