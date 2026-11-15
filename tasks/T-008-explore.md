# T-008 Explore
Role: builder   Lane: apps/web (explore)   Wave: 3
Status: review (builder, 2026-11-15)

## Goal
Explore table with filters, cards toggle, URL state, favourites, compare tray.

## Acceptance criteria
- [x] First 25 rows server-rendered
- [x] Client filtering from catalogue JSON
- [x] Compare tray (max 4) survives reload
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**Builder, 2026-11-15 (overnight 1). Branch proto/overnight-1, lane apps/web/.** Includes the coordinator addenda Decision 009 (DC km in 20 min, provenance badges) and Decision 010 (taxonomy filters, glossary ⓘ, display levels, learn stubs).

Acceptance:
- [x] First 25 rows server-rendered: `app/[country]/page.tsx` filters and sorts on the server from `searchParams`, then passes 25 rows to `components/Explore.tsx`.
- [x] Client filtering from the catalogue JSON: Explore fetches `/data/catalogue-<release>.json` (or `catalogue-dev.json` for the fixture) from our origin after first paint. 86 KB raw / ~5 KB gzip with the fixture.
- [x] Compare tray (max 4) survives reload and navigation: `components/CompareTray.tsx` + `lib/compare-store.ts` (localStorage, cross-tab sync), mounted in `app/[country]/layout.tsx`.
- [x] Tests: 59 Vitest units (state, filters, sort, compare store, favourites, i18n, formatters, catalogue loader, taxonomy, levels) + 2 Playwright tests (`e2e/smoke.spec.ts`: filter → 2 to compare → reload → tray 2 → navigate → tray 2, and asserts no request leaves our origin; switchers keep the URL).

What's there:
- Routes: `/` → `/nl` (redirect), `/[country]` Explore, `/[country]/learn/[term]` (stubs from glossary_terms), `/data/[file]` compact catalogue JSON. Unknown country → 404.
- `lib/catalogue.ts`: `Catalogue` interface (release, origin, generatedAt, rows, variant, generation, generations, sources, taxonomy, platforms, batteryPacks). Reads `data/releases/<latest>/catalogue.json` (`latest` can be a number file or a symlink/dir; `CATALOGUE_DIR` overrides), re-reads on mtime change, and falls back to the fixture if the release is missing or broken.
- Fixture `src/fixtures/catalogue.sample.json`: 38 variants, 26 generations, all eras; validates against the current `Catalogue` schema; taxonomy tables copied from `data/taxonomy/*.yaml` plus draft glossary rows (Q-024). Values are approximate and unsourced, and the footer says so.
- `lib/state.ts`: `ExploreState` (filters, sort, dir, view, level) + URL and JSON (de)serialisers. Short URL keys: price, era, seg, body, range, kwh, dc, boot, len, tow, volt, vmin, vmax, chem, cool, fast400, c100, sort (`-key` = desc), view, level. Unknown params (e.g. `lang`) are left alone.
- Filters per brief + Decision 010 (voltage chips, Advanced nominal-V sliders, fast on 400 V, chemistry chips with ⓘ pros/cons/care, cooling, charge to 100% daily). A missing value excludes a row only while that filter is on. The DC column, sort and filter use `dc_km_per_20min`; cards also show 10 min and peak kW (with "claim").
- Levels: Simple (6 columns, plain labels, fewer filters), Detailed (default), Nerd (+ nominal V, 400 V behaviour, cooling, platform, pack, raw values, inline sources/confidence/release date, rung id).
- `components/Num.tsx` (reusable on server pages via `numLabels(t)`), `Term.tsx`, `PriceBand.tsx` ("Not enough data" below 5 samples), `QualityBadge.tsx`, `use-popover.ts` (hover/focus/tap, Esc, fixed position so the table never clips it).
- Table: sticky header, sticky first column, horizontal scroll, sort buttons in `th` with `aria-sort`. Cards view is remembered in localStorage and defaults to cards under 640 px. On mobile the filters collapse behind a button.
- Hearts = local favourites (`lib/favourites.ts`).
- `config/countries.ts`: 5 countries, currency (GBP for UK), default language, "See listings" templates (`verified: false`, Q-028), `listingLinks()` for T-009.
- CSP in `next.config.ts` (`default-src 'self'`); no external fonts, CDNs or analytics.

JS size: Next 16 no longer prints First Load JS, so I measured on `next start`. Explore `/nl` = **~154 KB gzip (513 KB raw)** for modern browsers; 193 KB gzip if you count the `noModule` polyfill chunk, which modern browsers skip. Our own code is ~19 KB of that; the rest is React/Next. HTML is 351 KB raw / 27 KB gzip (25 rows with popovers, RSC payload, taxonomy).

Commands run (all green): `pnpm lint`, `pnpm typecheck`, `pnpm test` (59), `pnpm build`, `pnpm e2e` (2).

Open / for the next builder:
- Questions: Q-024 (glossary ids), Q-025 (no date in FieldProvenance), Q-026 (default level, row links to model pages), Q-027 (`CATALOGUE_DIR` in .env.example), Q-028 (listing URLs unverified). The schema `not-disclosed` oneOf bug is Q-017 (the fixture leaves `Platform.voltage_class_id` out).
- On release 1, the "On 400 V chargers" cell shows "—" when `dc_peak_kw` is missing (no DC data), so cars without DC figures never look like they fast-charge (22 rows affected). `fast_on_400v: null` is treated as unknown: the filter only keeps `true`.
- Release 1 from the pipeline (210 variants) landed at 01:02. It validates against the schema and the app serves it automatically (fixture → release, no code change): client JSON `/data/catalogue-1.json` is 912 KB raw / 34.5 KB gzip, immutable. Unit tests and e2e use the fixture for determinism (`CATALOGUE_DIR=e2e/no-release` in `playwright.config.ts`); `E2E_CATALOGUE_DIR=../../data/releases pnpm e2e` runs the smoke test on the real release (passes too). The raw JSON could shrink a lot by de-duplicating provenance objects, if T-016 wants it.
- Explore rows don't link to model pages yet (route owned by T-009).
- `/[country]/compare` is linked from the nav and tray but owned by T-010; until it lands it 404s.
- The `pnpm-workspace.yaml` `onlyBuiltDependencies` list is unchanged; sharp isn't needed (no next/image).

## Review
