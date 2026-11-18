# T-141 Ariakit for complex widgets; first use: hero brand picker
Role: builder   Lane: apps/web   Wave: launch
Status: review (Ariakit chat, 2026-11-18; asked directly by Menno)

## Goal
Adopt Ariakit (Decision 056) and replace the hero's long brand button lists with a type-to-search multi-select.

## Acceptance criteria
- [x] `@ariakit/react` in apps/web; Decision 056 logged
- [x] "Only these brands" / "Leave out these brands" are Ariakit comboboxes: type to narrow, pick several, remove as chips; same `make` / `xmake` URL params
- [x] Loaded on demand (only when "More filters" opens); Explore first load stays < 200 KB gzip
- [x] Works by keyboard (type, Enter picks the first match, Escape closes); axe clean in light and dark
- [x] Unit test for brand matching (case and accents); feature-map flow `hero-brand-picker`
- [ ] Gate PR: apps/web/AGENTS.md rule 4 wording (separate, gate-only)

## Inputs
Decision 056, docs/spec/launch-scope.md §1 step 4 (optional refine: brands to include or exclude), https://ariakit.com/guide/getting-started

## Out of scope
Migrating `use-popover.ts` (Num, Term ⓘ, Explore): see Decision 056 consequences.

## Handoff notes
- `src/components/BrandPicker.tsx` (+ test), wired in `Hero.tsx` via `next/dynamic` and the refine `<details>` `onToggle`.
- Bug found while verifying: `useDeferredValue` let Enter pick a stale first row (typed "tes", got BMW). Now filters synchronously with `autoSelect`.
- Pre-existing, not from this task: the `tooltip` verify flow fails on main too (a0f5a8b): no ⓘ button inside hero cards. Told WS2.
- New strings `hero.refine.brandSearch|brandRemove|brandNone` in all six dictionaries.

## Review
