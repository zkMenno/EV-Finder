# T-009 Model pages
Role: builder   Lane: apps/web (ev pages)   Wave: 3
Status: review (builder, overnight 2026-11-15)

## Goal
Make/model/generation/variant pages with spec diff, See listings, sources.

## Acceptance criteria
- [x] Source + confidence on every number
- [x] See listings per country
- [x] RDW count for NL
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
Built (all server components; each has `generateStaticParams` for the 5 countries):
- `/[country]/ev/[make]/[model]`: model overview. Lists generations with years, a "years not yet checked" badge when `uncertain`, variant count and the NL RDW count (Num).
- `/[country]/ev/[make]/[model]/[generation]`: key facts (voltage class, chemistry, 400 V behaviour, cooling, each with a Term ⓘ; "differs by variant" when variants disagree), RDW count labelled "registered in NL (RDW)" via Num, PriceBand (shows "Not enough data"), See listings for the page's country, a change-marker timeline and a spec diff table. In the table, columns are variants in timeline order and rows are `DIFF_KEYS`; cells that differ from the column to their left get ▲ plus sr-only "changed" text.
- `/[country]/ev/[make]/[model]/[generation]/[variant]`: full spec sheet in 7 groups (range, battery, charging, performance, dimensions, practicality, price & availability). Every number goes through Num. Also add-to-compare + heart (`_components/VariantActions.tsx` imports `compareStore`/`favouriteStore`/`useListStore`, unchanged), See listings, and sibling variants.
- Slugs: `app/[country]/ev/_lib/routes.ts`. A segment is the id minus `<parent id>-` when that is clean, else the full id (e.g. `/nl/ev/audi/e-tron/ge/50`, `/de/ev/volkswagen/vw-e-golf/...` in the fixture). Release 1 has 0 unclean ids and 0 collisions (40 models, 56 generations, 210 variants). Unknown → `notFound()`.
- See listings: `src/lib/listings.ts` wraps `listingLinks()`, links are `rel="nofollow noopener"` `target="_blank"`, nothing is fetched, and the patterns are marked unverified (Q-028).
- Shared: `_components/SpecValue.tsx` (renders one field via Num or the taxonomy label), `_lib/context.ts` (per-request ctx; passes Num only the source names it needs), `_lib/data.ts`. Strings are in `src/i18n/pages.{en,nl}.json` via `src/lib/pages-i18n.ts` (EN fallback).

Checks: `pnpm --filter @ev/web lint`, `typecheck`, `test` (15 files, 110 tests) and `build` all pass; `pnpm e2e` smoke (2 tests) passes. Pages checked by hand against release 1 with `next start` (200s for known ids; 404 for an unknown country, model, generation, variant or list).

For the Explore/i18n owner (I did not edit these files):
- Explore rows can now link to `variantHref(country, row)` / `generationHref` from `app/[country]/ev/_lib/routes.ts` (Q-026 part 2).
- The header nav could link `/[country]/top` (Rankings).
- When the main dictionaries are free, `pages.*.json` can be merged into `en.json`/`nl.json`.
- Glossary: no term fits the RDW count, power, accel, length or weight, so they show without ⓘ. A `registrations-nl` term (already drafted in Q-024) would fit.

Open: Q-033 (pages render on demand because the layout reads headers()).

## Review
