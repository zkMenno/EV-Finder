# AGENTS.md — apps/web

Lane rules for the Next.js app. Read the root `AGENTS.md` first; this file only adds to it.

## Stack

Next.js 16 (App Router, Turbopack) · React 19 · TypeScript strict · Tailwind 4 · Vitest · Playwright. pnpm workspace package `@ev/web`; types come from `@ev/schema` (generated, never hand-written; type-only imports).

## Rules

1. **Server components by default.** Add `"use client"` only where interaction needs it (Explore, Num, Term, CompareTray, switchers). Pages, layouts and learn pages stay server components.
2. **Every number goes through `<Num>`** (`src/components/Num.tsx`): value + unit + `provenance` from the row. It shows source and confidence on hover, focus and tap, the Decision 009 text badges ("N sources agree", "1 source", "estimate", "claim"), and inline sources at Nerd level. From a server component, pass `labels={numLabels(t)}` (functions can't cross the client boundary). Missing values render "—", never 0.
3. **No third-party browser calls.** No external fonts, CDNs, analytics, images or iframes. The browser talks only to our own origin. A CSP in `next.config.ts` enforces this, and the e2e smoke test fails on any foreign request.
4. **JS budget: Explore first load < 200 KB gzip; client catalogue < 300 KB gzip.** `node apps/web/scripts/budget.mjs` (after `pnpm build`; CI runs it in the `web` job) sums the gzipped JS chunks `/[country]` loads, read from `.next/build-manifest.json` + the `[country]/page` client-reference manifest (noModule polyfills reported, not counted), and gzips the client catalogue built from the latest release. Last measured (2026-11-15): 162.1 KB gzip JS (9 chunks; +39.5 KB polyfills), catalogue 34.9 KB gzip (release 1). No table, state or UI libraries; ask in `QUESTIONS.md` before adding any runtime dependency.
5. **Data access only through `src/lib/catalogue.ts`** (Decision 008): `getCatalogue()` reads `data/releases/<latest>/catalogue.json` (or `CATALOGUE_DIR`) and falls back to the dev fixture. Never read the pipeline's other files directly. One exception: the staff page `/staff/review` reads `data/review/*.csv` via `src/lib/review.ts` (off unless `STAFF_PAGES=1`, Q-035).
6. **Taxonomy is data** (Decision 010): voltage classes, chemistries, cooling types and glossary terms come from `catalogue.taxonomy()`. Adding a row must need no code change. Ids are free strings; `not-disclosed` is valid and never matches a filter choice.
7. **One state shape** (`src/lib/state.ts`, `ExploreState`) for URL, localStorage and later accounts. Add a field there with a URL key, (de)serialisers and a test, or not at all.
8. **localStorage only via `src/lib/storage.ts`** (try/catch, works when storage is missing or throws).
9. **i18n:** strings live in `src/i18n/*.json` (one dictionary per language, page strings included). EN is complete, NL covers the public UI (staff pages are EN only), other languages fall back to EN key by key. Use `t()`; no hard-coded UI text. Client components get `getClientDict(lang)`, which drops the server-only prefixes in `SERVER_ONLY_PREFIXES` (`crumb.`, `model.`, `gen.`, `listings.`, `variant.`, `field.`, `drivetrain.`, `top.`, `staff.`); a test fails if a client component uses one. The brand name comes from `APP_NAME` (`src/config/site.ts`).
10. **Metric units always**; format with `src/lib/format.ts` (Intl, language locale, country currency).
11. **No DC data, no DC behaviour:** `hasDcData(row)` (`src/lib/dc.ts`) decides whether 400 V charger behaviour (`charger_400v_mode`, `charger_400v_kw`, `fast_on_400v`) may be shown; everything that renders or compares those fields goes through it (Q-049).
12. **Accessibility:** visible focus, labels on every control, `aria-sort` on sortable headers, text (not colour alone) for status. Missing values are `<Missing>` ("—" + sr-only text). Disabled-but-explained controls use `aria-disabled` + a description, not `disabled`. In the Explore table only the name link, heart and compare are Tab stops (+ the Nerd "Sources" button); numbers pass `focusable={false}`.

## Shared components other builders reuse

- `Num`, `num-labels`: numbers with provenance.
- `Term` / `TermLabel` / `TermInfo` / `InfoTip`: glossary ⓘ.
- `PriceBand`: used-price band ("Not enough data" below 5 samples).
- `CompareTray` + `src/lib/compare-store.ts`: the compare tray (max 4, persisted). It lives in `app/[country]/layout.tsx`. The compare page itself belongs to T-010; read `?ids=a,b`.
- `src/config/countries.ts`: countries, currency, default language (client-safe).
- `src/lib/listings.ts`: `seeListings()` / `listingLinks()` (server only). Patterns live in `config/countries/<country>.yaml` at the repo root; `scripts/listings.mjs` validates them and writes `src/config/listings.generated.json` (run `pnpm listings` after editing; `build`/`dev` run it, and a test fails when the JSON is stale). Public search URLs only (Decision 004), all `verified: false`.
- `/[country]/about`: what the site is, method, licences, and credits from the release's `sources` (`src/lib/credits.ts`). Fallback attribution comes from `data/sources.yaml` via `scripts/sources.mjs` → `src/config/sources.generated.json` (same pattern as listings: build/dev run it, a test fails when stale, Docker keeps the committed JSON). Linked from the footer on every country page.
- `Registrations` (`app/[country]/ev/_components/Registrations.tsx`): official counts per country (`registrations.<CC>`), one line per count, never summed.
- Explore rows and cards link to variant pages via `variantHref`/`generationHref` (`app/[country]/ev/_lib/routes.ts`).

## Tests

- `pnpm test`: Vitest units next to the code (`*.test.ts`). Fixtures only, no network.
- `pnpm e2e`: Playwright smoke test on a production build (`pnpm build` first).
