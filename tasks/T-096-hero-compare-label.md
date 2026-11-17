# T-096 Hero compare button: visible text inside its accessible name; hero results in the a11y suite
Role: WS2   Lane: apps/web   Wave: launch polish
Status: todo

## Goal
Screen-reader and voice-control users can name the hero's compare button by what they see (WCAG 2.5.3 Label in Name).

## Acceptance criteria
- [ ] The hero card's compare button's accessible name starts with (or contains) its visible text in every language ("Vergelijken" → "Vergelijken: Skoda Enyaq 85", not "Add Skoda Enyaq 85 to compare")
- [ ] `e2e/a11y.spec.ts` checks a hero page with answers (e.g. `/nl/nl?role=only&trips=monthly&level=nerd`) at 360 and 1280 px, light and dark, with no critical/serious axe findings
- [ ] Same check on Explore's compare toggles if they share the pattern

## Inputs
Found by the fresh review of PR #50 (2026-11-17): axe `label-content-name-mismatch`, 50 nodes at 360 px, both themes; pre-existing on main. The a11y suite has no hero page with answers, so CI never saw it.

## Out of scope
Other hero layout changes.

## Handoff notes

## Review
