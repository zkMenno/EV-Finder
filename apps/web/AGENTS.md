# AGENTS.md — apps/web

Lane rules for the Next.js app. Read the root `AGENTS.md` first; this file only adds to it.

## Stack

Next.js 16 (App Router, Turbopack) · React 19 · TypeScript strict · Tailwind 4 · Vitest · Playwright. pnpm workspace package `@ev/web`; types come from `@ev/schema` (generated, never hand-written; type-only imports).

## Rules

1. **Server components by default.** Add `"use client"` only where interaction needs it (Explore, Num, Term, CompareTray, switchers). Pages, layouts and learn pages stay server components.
2. **Every number goes through `<Num>`** (`src/components/Num.tsx`): value + unit + `provenance` from the row. It shows source and confidence on hover, focus and tap, the Decision 009 text badges ("N sources agree", "1 source", "estimate", "claim"), and inline sources at Nerd level. From a server component, pass `labels={numLabels(t)}` (functions can't cross the client boundary). Missing values render "—", never 0.
3. **No third-party browser calls.** No external fonts, CDNs, analytics, images or iframes. The browser talks only to our own origin. The CSP from `src/proxy.ts` (`src/lib/csp.ts`) enforces this and has no `'unsafe-inline'` for scripts (nonce on dynamic pages, hashes from `scripts/csp-hashes.mjs` on static ones): never add an inline `<script>` by hand. The e2e smoke test fails on any foreign request and `e2e/security.spec.ts` on CSP violations.
4. **JS budget: Explore first load < 200 KB gzip; client catalogue < 300 KB gzip.** `node apps/web/scripts/budget.mjs` (after `pnpm build`; CI runs it in the `web` job) sums the gzipped JS chunks `/[country]/[lang]` loads, read from `.next/build-manifest.json` + the `[country]/[lang]/page` client-reference manifest (noModule polyfills reported, not counted), and gzips the client catalogue built from the latest release. Last measured (2026-11-15, T-061): 156.3 KB gzip JS (8 chunks; +39.5 KB polyfills), catalogue 94.3 KB gzip (release 1, 244 rows). Features that Explore doesn't need on first paint load with `import()` on demand (the trip module, `src/components/trip/TripModule.tsx`). No table, state or UI libraries; ask in `QUESTIONS.md` before adding any runtime dependency.
5. **Data access only through `src/lib/catalogue.ts`** (Decision 008): `getCatalogue()` reads `data/releases/<latest>/catalogue.json` (or `CATALOGUE_DIR`) and falls back to the dev fixture. Never read the pipeline's other files directly. One exception: the staff page `/staff/review` reads `data/review/*.csv` via `src/lib/review.ts` (off unless `STAFF_PAGES=1`, Q-035).
6. **Taxonomy is data** (Decision 010): voltage classes, chemistries, cooling types and glossary terms come from `catalogue.taxonomy()`. Adding a row must need no code change. Ids are free strings; `not-disclosed` is valid and never matches a filter choice.
7. **One state shape** (`src/lib/state.ts`, `ExploreState`) for URL, localStorage and later accounts. Add a field there with a URL key, (de)serialisers and a test, or not at all.
8. **localStorage only via `src/lib/storage.ts`** (try/catch, works when storage is missing or throws).
9. **i18n:** strings live in `src/i18n/*.json` (one dictionary per language, page strings included). EN is complete, NL covers the public UI (staff pages are EN only), other languages fall back to EN key by key. Use `t()`; no hard-coded UI text. Client components get `getClientDict(lang)`, which drops the server-only prefixes in `SERVER_ONLY_PREFIXES` (`crumb.`, `model.`, `gen.`, `listings.`, `variant.`, `field.`, `drivetrain.`, `top.`, `staff.`, `charging.`); a test fails if a client component uses one. Client components import `makeT`/types from `@/i18n/t`, never `@/i18n` (that pulls all six dictionaries into the browser bundle, ~14 KB gzip). The brand name comes from `brand.name` in `src/config/site.ts` (`APP_NAME` overrides; working title "EV Shortlist", Decision 018).
10. **Metric units always**; format with `src/lib/format.ts` (Intl, language locale, country currency).
11. **No DC data, no DC behaviour:** `hasDcData(row)` (`src/lib/dc.ts`) decides whether 400 V charger behaviour (`charger_400v_mode`, `charger_400v_kw`, `fast_on_400v`) may be shown; everything that renders or compares those fields goes through it (Q-049).
12. **Accessibility:** visible focus, labels on every control, `aria-sort` on sortable headers, text (not colour alone) for status. Missing values are `<Missing>` ("—" + sr-only text). Disabled-but-explained controls use `aria-disabled` + a description, not `disabled`. In the Explore table only the name link, heart and compare are Tab stops (+ the Nerd "Sources" button); numbers pass `focusable={false}`.

13. **URLs are `/{country}/{lang}/…` (Decision 015).** Build every internal link from `siteBase(country, lang)` (`src/lib/site-paths.ts`) or the route helpers (`modelHref(base, …)`, `variantHref`, `compareHref`, `TermInfo base=`), never `/${country}/…`. Languages per country come from `config/countries/<cc>.yaml` (`languages`, `default_language`; served = those + EN) via `scripts/countries.mjs`. Layouts and static pages never read request headers or cookies (that would make every page dynamic); `generateMetadata` uses `pageMeta()` for canonical + hreflang.
14. **Static pages are built from the release** (model / generation / variant / learn / rankings / about). A new release needs a rebuild (Q-070). `getCatalogue()` throws during `next build` if the release can't be read; the post-build step fails on baked 404s.
15. **Prices in three modes (Decision 017):** `ExploreState.pay`; the loan maths and input rules live in `src/lib/finance.ts` (no APR without a source: ask the user), the UI in `src/components/PriceMode.tsx`, profiles from `data/taxonomy/finance_profiles.yaml` via `scripts/finance.mjs` (server only, `financeProfile()`). Every amount says "estimate", shows its inputs and the CCD2 warning; no finance or lease links for the UK; lease shows no figures.
16. **Colours come from the design tokens** (`docs/design/tokens.json` → `pnpm theme` → `src/app/tokens.generated.css`), light "Day trip" and dark "Night drive". Never paste hex values; use `var(--token)`. The Tailwind palette in use is mapped onto the tokens in `globals.css`; a new palette colour needs a mapping there. axe (`e2e/a11y.spec.ts`) must stay free of critical/serious findings in both themes.

## Shared components other builders reuse

- `Num`, `num-labels`: numbers with provenance.
- `Term` / `TermLabel` / `TermInfo` / `InfoTip`: glossary ⓘ.
- `PriceBand`: used-price band ("Not enough data" below 5 samples).
- `CompareTray` + `src/lib/compare-store.ts`: the compare tray (max 4, persisted). It lives in the root layout `app/[country]/[lang]/layout.tsx`. The compare page itself belongs to T-010; read `?ids=a,b`.
- `PriceMode` (`PayModeToggle`, `LoanBox`, `LeaseNotice`, `PricePanel`): price modes and the loan calculator (T-043).
- `LanguageBanner`: the Accept-Language suggestion (Decision 015).
- `LearnArticle` (`LearnBlocks`) + `src/lib/learn.ts`: /learn guides from `content/learn` (parsed at build time by `scripts/learn.mjs`: front matter, a small Markdown subset, `[[id]]` / `[[id|text]]` → ⓘ). No Markdown library; raw HTML stays text.
- `src/config/countries.ts`: countries, currency, languages from config (`defaultLang`, `served`, `servedPairs()`, `isServed()`), client-safe.
- `src/lib/listings.ts`: `seeListings()` / `listingLinks()` (server only). Patterns live in `config/countries/<country>.yaml` at the repo root; `scripts/listings.mjs` validates them and writes `src/config/listings.generated.json` (run `pnpm listings` after editing; `build`/`dev` run it, and a test fails when the JSON is stale). Public search URLs only (Decision 004), all `verified: false`.
- `/[country]/[lang]/about`: what the site is, method, licences, and credits from the release's `sources` (`src/lib/credits.ts`). Fallback attribution comes from `data/sources.yaml` via `scripts/sources.mjs` → `src/config/sources.generated.json` (same pattern as listings: build/dev run it, a test fails when stale, Docker keeps the committed JSON). Linked from the footer on every country page.
- `Registrations` (`app/[country]/[lang]/ev/_components/Registrations.tsx`): official counts per country (`registrations.<CC>`), one line per count, never summed. A model-level count (RDW shared-year cars, Q-066) follows the generation-level one and reads "generation unknown, shown on all X generations"; list keys come from `registrationItemKey()` (includes `level`).
- `ChargingLinks` + `src/lib/charging-links.ts` (T-026): the "Find a charger / plan a trip" block from `config/countries/<cc>.yaml` `charging_links` (max 5; `scripts/charging-links.mjs` validates them into `src/config/charging-links.generated.json`, build/dev run it, a test fails when stale). Text links, new tab, `noopener` (+ `nofollow` unless `official: true`), our UTM tag unless `utm: false`. Renders nothing without links. Country page, model/generation/variant pages (+ plain ABRP line via `abrpLink()`) and /learn pages. `CHARGING_LINKS_FILE` swaps in a JSON fixture (e2e).
- Trip fit quick check (T-036, behind `TRIP_FIT=1`, `src/config/features.ts`): model in `src/lib/trip-model.ts` (fixture matrix `src/fixtures/consumption-matrix.sample.json` + towns `src/fixtures/towns.sample.json`, both PROVISIONAL), answers in `src/lib/trip-settings.ts` (localStorage `TRIP_KEY`, a town id at most), UI in `src/components/trip/TripModule.tsx` (lazy). Only the on/off filter `trip=1` goes in `ExploreState`/URL.
- `LevelGate` / `LevelNum` (`src/components/LevelGate.tsx`) + `useLevel()` (`src/lib/use-level.ts`): Simple / Detailed / Nerd on static pages (`?level=`, else the level Explore remembered, else detailed). Nerd-only content appears after hydration.
- `LineChart` (`src/components/LineChart.tsx`): hand-written SVG line chart, server component, token colours + dash patterns + legend; always pair it with a data table. Data for the charging page comes from `src/lib/charging-stats.ts` via `catalogue.chargingStats()` (one chart = one definition_id, Decision 012).
- `KnownIssues` and `YearsBadge` (`app/[country]/[lang]/ev/_components/`): RDW APK defect rates per first-registration year (same-year baseline only, Q-078) and the shared generation-year badge (`yearsStatus()` in `ev/_lib/data.ts`).
- Explore rows and cards link to variant pages via `variantHref`/`generationHref` (`app/[country]/[lang]/ev/_lib/routes.ts`, all take the `/{country}/{lang}` base).

## Tests

- `pnpm test`: Vitest units next to the code (`*.test.ts`). Fixtures only, no network.
- `pnpm e2e`: Playwright on a production build (`pnpm build` first), on the published release.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
