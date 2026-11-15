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

**Reviewer, 2026-11-15 (fresh agent). Verdict: changes needed (one honesty bug), otherwise pass.**

- [x] Source + confidence on every number: all numeric spec fields go through `SpecValue` → `Num` (`app/[country]/ev/_components/SpecValue.tsx:59-92`); RDW count via `Num` on model and generation pages. Model years are raw text (no provenance exists for years in release 1, see T-008 review).
- [x] See listings per country: links come from `config/countries/*.yaml`, render `rel="nofollow noopener" target="_blank"` (checked on `/nl/ev/tesla/model-3/gen1`), nothing is fetched, "unverified" note shown.
- [x] RDW count for NL with the `registrations-nl` ⓘ.
- [x] `not-disclosed` renders "not disclosed" (`SpecValue.tsx:35`).
- [x] Unknown country/model/generation/variant → 404; no foreign requests from model, generation or variant pages (new e2e `T-017: every page talks only to our own origin`).

Changes needed:
1. **No DC data, but the spec sheet still describes DC behaviour.** Explore hides "On 400 V chargers" when `dc_peak_kw` is missing (coordinator rule, `Explore.tsx:592`), but `SpecValue` has no such rule: `textValue()` (`SpecValue.tsx:43`) prints the `charger_400v_mode` and the numeric path (`SpecValue.tsx:75`) prints `charger_400v_kw`. On release 1, 22 cars without any DC figure show "On 400 V chargers: native", and `hyundai-ioniq-6-gen1-53kwh-rwd` shows "booster" + "50 kW" with no DC peak. The generation key facts (`[generation]/page.tsx:55`) and the spec diff (`DIFF_KEYS` includes `charger_400v_mode`) inherit it. Fix: one shared helper (e.g. `hasDcData(row)` in `lib/spec-diff.ts`) used by Explore, `SpecValue`, `cellValue()` and the key facts, so `charger_400v_mode`/`charger_400v_kw`/`fast_on_400v` read as missing when there is no DC data. The e2e `T-009/T-010: spec sheets show no 400 V charger behaviour…` in `e2e/review.spec.ts` is marked `test.fail()` and documents this; remove the marker once fixed.
