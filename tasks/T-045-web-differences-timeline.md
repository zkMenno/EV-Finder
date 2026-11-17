# T-045 Differences-only toggle and variant change timeline (Core)
Role: WS2   Lane: apps/web   Wave: 7
Status: merged (PR #24); fresh review via QA A-35; earlier note: WS2, 2026-11-15, branch t-045-differences-only

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
- 2026-11-15 WS2: Compare already had "differences only" (`?diff=1`, T-010) and the generation page already had the change-marker timeline. Added: the same toggle on generation pages (`DiffOnly`, client, `?diff=1`, CSS hides `tr[data-same]`; nothing reloads, static page stays static) and a "What changes from one version to the next" list from published values (`variantDeltas` in `src/lib/spec-diff.ts`: usable battery, real range, km in 20 min, power), with a note that real range is our estimate. Differing cells keep the existing ▲ + tint + sr-only text (colour-blind safe); UX's own diff style can replace it later.
- Winter-range deltas wait for a winter field in the release (asked WS1). Works at 360 px (screenshot checked). e2e/diff-only.spec.ts.

## Review
