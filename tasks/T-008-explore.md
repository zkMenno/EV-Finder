# T-008 Explore
Role: builder   Lane: apps/web (explore)   Wave: 3
Status: merged (PR #1); fresh review via QA A-35; earlier note: builder, 2026-11-15

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

## Integration (wave 4)

**Builder, 2026-11-15 (overnight 1, wave 4). Branch proto/overnight-1. Owns all of apps/web, plus config/countries/, config/price-index/ and .env.example (names only).**

Done:
1. **Integration.**
   - Explore links: the car name in table rows and cards links to the variant page (`variantHref`), and the Generation column links to the generation page (`generationHref`). `make_id` is now in the compact Explore rows (`EXPLORE_FIELDS`) so the client can build the href. Unit test: every fixture row's Explore href resolves back to the same variant.
   - Header nav: Explore · Rankings (`/[country]/top`, new key `nav.rankings`) · Compare.
   - i18n: `pages.{en,nl}.json` merged into `en.json` / `nl.json` (no key collisions); `src/lib/pages-i18n.ts` and its test removed; pages use the normal `t()`, and `hasMsgKey()` (in `src/i18n/index.ts`) replaces `hasPageKey()`. The 12 page strings NL lacked are translated now. de/fr/es/it still fall back to EN key by key (tested). To keep the Explore payload small, client components get `getClientDict()`, which leaves out the server-only prefixes; a test scans the `"use client"` components for those keys.
   - RDW count: the `registrations-nl` Term ⓘ is on the generation page (key facts), the model page (per generation) and every spec table (variant page, compare) via the `registered_count_nl` spec field. Explore already had it.
2. **Q-033 (static pages): skipped, see Q-034.** It needs the language as a route segment (root layout owns `<html lang>`), and static output would bake in the catalogue at build time, which clashes with runtime release swaps (Decision 008) and with the Docker build stage having no `data/releases`. A concrete design is in Q-034; it needs a Decision entry first. Language switcher and e2e unchanged.
3. **Stretch.**
   - a. `/staff/review` (`src/app/staff/review/page.tsx`, `src/lib/review.ts`): read-only tables for `unmatched.csv` / `conflicts.csv`, server-side read with an RFC 4180 parser, filter by `source_id` (GET form, no JS), 500 rows per page with prev/next links, file mtime shown. 404 unless `STAFF_PAGES=1`; `robots: noindex` plus an `X-Robots-Tag` header in `next.config.ts`. `REVIEW_DIR` overrides the folder. EN-only strings (`staff.*`). `STAFF_PAGES` and `REVIEW_DIR` added to `.env.example`. Exception to lane rule 5 noted in `apps/web/AGENTS.md` (Q-035). Checked by hand with release data: 1,411 unmatched rows (3 pages), conflicts filter `openev` = 151 of 489.
   - b. Listing links moved to `config/countries/{nl,de,fr,be,uk}.yaml` (site, label, url_template, filters map, slug_overrides, priority, verified: false). `apps/web/scripts/listings.mjs` validates them at build time (https only, known placeholders and filters, no duplicate ids, and it rejects keys/query names that look like rates, sampling, affiliate ids or secrets, per Decision 004) and writes `src/config/listings.generated.json`, which `src/lib/listings.ts` imports. `build` and `dev` run it; `pnpm listings` runs it alone; `--check` fails on a stale JSON, and a unit test does the same in CI. `js-yaml` 4.3.2 added as a **devDependency** (already in the lockfile through ESLint; build-time only, so no YAML code in any bundle; checked in `.next`). `src/config/countries.ts` no longer holds listings and stays client-safe. URLs are unchanged except mobile.de, where `ft=ELECTRICITY` now comes after `q=`.
   - c. `config/price-index/README.md` + `apps/web/src/lib/price-index.ts` (`PRICE_INDEX`: NL/DE/FR/BE/UK → 2010–2026 → `null`, `priceIndex()`), with a test. Not used in the UI.
4. `apps/web/README.md` (all routes, commands, env) and `apps/web/AGENTS.md` (i18n, listings, rule 5 exception, JS size) updated.

Checks (from the repo root, each separately): `pnpm --filter @ev/web lint`, `typecheck`, `test` (16 files, 123 tests), `build`, `e2e` (4 tests: the 2 earlier ones, plus Explore row → variant page with the Rankings/Compare nav links, and `/staff/review` 404 by default). All green.

Size: Explore `/nl` first load **~156 KB gzip** for modern browsers (519 KB raw; 9 scripts), 195 KB including the 38.6 KB noModule polyfills. Was ~154 KB; the 2 KB is `next/link` in Explore. HTML on release 1: 414 KB raw / 28.7 KB gzip.

For the coordinator:
- Q-034 (static pages), Q-035 (staff page, no auth).
- Docker: `.dockerignore` (not my lane) leaves `config/` out of the build context, so the image build uses the committed `listings.generated.json` (the script warns and keeps it). To regenerate in the image, allow `!config/countries/` and add `COPY config/countries config/countries` to the build stage.
- Any edit to `config/countries/*.yaml` must be followed by `pnpm --filter @ev/web listings` and committing the JSON, or the unit test fails.

## Review

**Reviewer, 2026-11-15 (fresh agent, proto/overnight-1). Verdict: pass, with minor follow-ups.**

Checked against the acceptance criteria and the brief's quality bar, on the fixture (e2e) and on release 1 (`next start`).

- [x] First 25 rows server-rendered; client filtering from `/data/catalogue-1.json` (same origin, immutable, 34.7 KB gz).
- [x] Compare tray survives reload, navigation **and a country switch** (`/nl` → `/de`; store is not keyed by country, the tray link uses the new country). New e2e: `e2e/review.spec.ts` "compare tray survives a country switch".
- [x] URL state round-trips: `/nl?range=200&sort=-range&view=cards&level=nerd` survives hydration and reload (new e2e). `state.test.ts` round-trips URL and JSON.
- [x] Every number goes through `Num` (`num()` / `priceCell()` in `src/components/Explore.tsx:541-585`). Years (`formatYears`) are rendered raw, but release 1 carries no provenance for `year_start`/`year_end` at all (210/161 rows), so that is a pipeline/schema gap, not a UI bypass.
- [x] No DC shown for cars without DC data: `charger400()` (`Explore.tsx:590-592`) returns "—" when `dc_peak_kw` is missing; release 1 has 0 rows with a derived DC figure but no peak. New e2e checks the Zoe R240 row (DC and "On older chargers" both "—").
- [x] Keyboard: skip link is the first Tab stop and gets the 3 px outline; sort buttons work with Enter and `aria-sort` follows; compare toggle works with Space; tray "×" works with Enter (new e2e).
- [x] Contrast (Tailwind 4 oklch → sRGB, WCAG 2.x): body/secondary text slate-700 on white 10.3:1, notes slate-600 7.6:1, missing "—" slate-500 4.8:1 (4.55:1 on the hovered slate-50 row — passes AA, barely), links blue-800 8.8:1, quality badges 8.3 / 8.5 / 13.5:1, white on blue-800 8.8:1. All AA.
- [x] No `<img>`; icons (heart SVG, ✓/+, ↕) are `aria-hidden` with text labels.

Changes requested (minor, none block):
1. `Explore.tsx:623`: at Nerd level the chemistry cell appends the raw `cell_format`, so release 1 shows "· not-disclosed" for 3 rows. Run it through `named()` / `t("notDisclosed")`.
2. `Explore.tsx:229-236`: the "show more" button's accessible name is just "+ 13". Add a label ("Show 13 more").
3. `Num.tsx:65`: the missing-value "—" has no text for screen readers (read as "dash" or skipped). Add sr-only "no data".
4. `Explore.tsx:800`: when the tray is full the compare toggle is `disabled`, so keyboard users can't reach it to hear why. Prefer `aria-disabled` + the existing "full" label.
5. Keyboard cost: every number is a `<button>` (popover), so a 25-row Detailed table has about 200 Tab stops before the "show more" button. Acceptable for the prototype; consider a "skip table" link or one Tab stop per row later.
6. `PriceBand.tsx:44`: once samples exist, the price band will print money outside `Num` (no provenance). It always says "Not enough data" today; route it through `Num` before price sampling lands.
