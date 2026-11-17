# T-050 Country + language URLs, static pages again
Role: builder   Lane: apps/web (+ config/countries/*.yaml language keys)   Wave: overnight 1 (addendum 5 item 1)
Status: merged (PR #1); fresh review via QA A-35

## Goal
Every page lives at `/{country}/{lang}/…` (Decision 015), so each country × language has one crawlable URL with hreflang, and model / generation / variant / learn pages are static again (closes Q-033 / Q-034).

## Acceptance criteria
- [x] Routes are `/{country}/{lang}/…`; `/{country}/` redirects to the country's default language, taken from `config/countries/<cc>.yaml` (`languages`, `default_language`), not from code
- [x] Languages served per country = its own languages + EN; other pairs are never rendered (redirect to the default language) and never listed
- [x] hreflang on every page for every served country × language pair + `x-default`
- [x] `sitemap.xml` lists only served pairs, built from the release's model / generation / variant ids (compare and staff pages left out)
- [x] `Accept-Language` never redirects; it only suggests a language in a small, dismissible banner
- [x] Model / generation / variant / learn pages are SSG (`generateStaticParams` over served pairs), layouts read no request headers, `<html lang>` is right per route
- [x] Old `/{country}/…` URLs keep working via 308 redirects to the default language (or `?lang=` when that language is served)
- [x] Q-033 and Q-034 answered and moved to Closed
- [x] Playwright: the language switch keeps filters (URL) and the compare tray (localStorage); redirects, `<html lang>`, hreflang, banner and sitemap are checked
- [x] Unit tests for routing, served pairs, hreflang, sitemap and the YAML language keys (drift guard on the generated JSON)
- [x] `apps/web/README.md` and `apps/web/AGENTS.md` updated

## Inputs
Decision 015, docs/growth/seo-plan.md, Q-033, Q-034, workstreams/OVERNIGHT/ADDENDUM-5.md item 1.

## Out of scope
Translating DE/FR/ES/IT beyond the existing fallback; ISR or on-demand revalidation (Q-070).

## Handoff notes
**2026-11-15, web builder (overnight, proto/overnight-1).**

What was done:
- Config: `config/countries/<cc>.yaml` got `languages` + `default_language` (NL `[nl]`, DE `[de]`, FR `[fr]`, BE `[nl, fr, de]` default `nl`, UK `[en]`). `apps/web/scripts/countries.mjs` validates them into `src/config/countries.generated.json` (build/dev run it; a unit test fails when stale). `src/config/countries.ts` exposes `defaultLang`, `languages`, `served`, `isServed()`, `servedPairs()` (11 pairs), `hreflangTag()`.
- Routes: everything moved from `app/[country]/…` to `app/[country]/[lang]/…`. The root layout is now `app/[country]/[lang]/layout.tsx` (renders `<html lang={lang}>`, `generateStaticParams` = served pairs, `dynamicParams = false`); staff pages have their own root layout (`app/staff/layout.tsx`); unmatched URLs use `app/global-not-found.tsx` (`experimental.globalNotFound`). `src/lib/request-lang.ts` is gone.
- Links: one prefix, `siteBase(country, lang)` = `/{country}/{lang}` (`src/lib/site-paths.ts`); route helpers (`modelHref`, `variantHref`, `compareHref`, `compareUrl`, `TermInfo base=`) take that base. `swapLang` / `swapCountry` keep the rest of the path and the query; a country switch keeps the language if the target serves it.
- Redirects in `src/proxy.ts` via the pure `routeLang()` (`src/lib/lang.ts`): `/` and `/{country}` → 307 to the remembered language (cookie from the switcher, if served) or the config default; old URLs → 308; unserved language → 308 to the default.
- SEO: `pageMeta()` (in `ev/_lib/context.ts`) sets canonical + `alternates.languages` (11 hreflang + x-default = `/nl/en/…`, Q-071) on every page; `app/sitemap.ts` (via `src/lib/sitemap.ts`) and `app/robots.ts`; absolute URLs from `APP_URL`.
- Banner: `src/components/LanguageBanner.tsx` reads `navigator.languages` after hydration, suggests a served language in that language, dismissal stored in localStorage.
- Static generation: build output (release 1, 197 variants, 88 glossary terms): about 11, rankings index 11, ranking lists 33, models 440, generations 605, variants 2,167, learn 968 = **4,235 SSG pages (●)**; Explore `/[country]/[lang]` and Compare stay ƒ (they render from the query string).
- Data safety (found tonight): the pipeline rewrote `data/releases/1` during a build, the loader briefly saw no release and baked 540 pages as 404s from the fixture. Now `getCatalogue()` throws during `next build` if `data/releases/latest` exists but can't be read, and `scripts/csp-hashes.mjs` fails the build if any prerendered `/ev`, `/learn` or `/top` page is a 404. The Docker build stage copies the latest release in before `next build`.
- e2e now runs on the published release (`CATALOGUE_DIR=../../data/releases`), the same data the static pages are built from; fixture-specific ids in review.spec.ts were switched to release ids (Zoe `ph1-r240`, `ph2-r135`). The webServer readiness URL is `/health`.
- Budget script follows the new route (`app/[country]/[lang]/page`): Explore 153.6 KB gzip JS, catalogue 54 KB gzip.

Also done tonight (coordinator follow-ups after the three items):
- (b) Explore's chemistry ⓘ link now uses the language segment (`ctx.base`).
- (c) /learn guides: `scripts/learn.mjs` → `src/config/learn.generated.json`; `{base}/learn` index and `{base}/learn/<slug>` articles (draft banner for `review: needed`, sources list with "checked" dates, EN fallback with a notice, `<article lang>`), in the sitemap and a "Learn" nav link. Static: +66 pages (4,301 total). Tests: `src/lib/learn.test.ts`, `e2e/learn.spec.ts`.
- (a) Glossary sweep "For the web builder": done 1 (platform, battery-pack columns), 2 partly (trip column header + card label; not the TripBar filter/chip), 3 (detail-level ⓘ on the Explore level switch), 4 (ⓘ on every card item + used-price, dc-km-10min, platform, battery-pack), 5 (spec-diff ids incl. charge-to-100, dc-km-10min and the rest; `voltage_label` / `fast_on_400v` are not spec rows), 6 (used-price on generation + variant pages, registrations-nl on the variant row), 9 (rankings metric + price headers), 11 (price-mode, apr, deposit, loan-term, estimate on the calculator), 13 (the link bug). Not done: 7 (Num popover badges), 8 (badges), 10 (TripModule), 12 (bidi block not built yet).

Left / for others:
- Q-070: a release swap now needs a new image (WS4 runbook). Q-071: x-default, Belgium + DE, remembered-language redirect.
- The `/learn` article rendering from `content/learn/` (coordinator follow-up (c)) and the glossary sweep wiring (follow-up (a)) are separate.

### Wave 5 polish (2026-11-15, web builder, overnight)

All checks green after the last change: `lint`, `typecheck`, `test` (229 unit tests), `build` (5,258 static pages, release 1 at 244 rows), `e2e` (53 passed, 1 skipped: the `TRIP_FIT=0` variant), `budget.mjs` (Explore 156.3 KB gzip JS, catalogue 71.6 KB gzip; both under budget).

1. **Glossary wiring leftovers** (data/review/glossary-sweep.md items 2, 7, 8, 10):
   - Item 7: the `<Num>` popover links its words to /learn: "N sources agree" → `sources-agree`, "1 source" → `quality-tier`, estimate, claim, "Calculated by us" → `derived`, Confidence → `confidence`, and a new "Data release: {date}" line → `data-release`. The real-range method note → `real-range-rung`. "not disclosed" on spec pages gets a `not-disclosed` ⓘ. `numLabels(t, { base, terms })` builds the hrefs, only for terms that exist (`NUM_TERMS` in `num-labels.ts`). The links render only while the popover is open, so table rows keep 3 Tab stops.
   - Item 8: "years not yet checked" → `model-years` ⓘ (model, generation and variant pages); the quality badge → `quality-tier` ⓘ (variant page, Explore cards). There is no era badge or timeline yet (Q-085 point 3).
   - Item 2: the TripBar filter and the "Find cars for my trips" button → `trip-fit`.
   - Item 10: TripModule result title → `range-you-need`, ≈ WLTP → `wltp-equivalent`, temperatures and home town → `climate-normal`, road bands → `road-band`, the assumptions line → `start-charge`, `trip-margin`, `soh`; Nerd → `uncertainty-band`, `real-range-rung` (`TripUi.gloss`).
   - The rankings estimates note → `estimate`.
2. **axe in Playwright** (`e2e/a11y.spec.ts`). `@axe-core/playwright` was added as a **devDependency**: it runs Deque's axe-core rules inside the real page in the e2e browser, the standard automated WCAG check. It is test-only, never reaches the browser bundle, and has no runtime cost. It covers 8 pages × 2 themes and fails on critical or serious findings. Before: 2 serious (sort-button names, Nerd target size) + 1 moderate (duplicate nav label). After: 0 of any level. Details are in `audits/A-04-accessibility.md`.
3. **Dark theme**: tokens from `docs/design/tokens.json` (design system v2) → `scripts/theme.mjs` → `src/app/tokens.generated.css` (light "Day trip", dark "Night drive", system default via `prefers-color-scheme`, print = light). `globals.css` maps the Tailwind palette in use onto the tokens. The header toggle (`ThemeToggle`, `aria-pressed`) is remembered in localStorage (`src/lib/theme.ts`) and applied before first paint by the same-origin `/theme-init.js` (CSP unchanged). AA in both themes: axe reports no contrast findings. The light theme now also uses the design palette (navy ink, design link colour).
4. **Explore polish**: cards at 360 px are checked for no sideways scroll at all three levels. Header row: sticky (it already was) and tested. Keyboard: the scroll area is a Tab stop, every stop shows the 3 px focus ring, and headers come before row controls (tested). Empty state: "No cars match: remove the "{filter}" filter to see {n}." with a remove button and a reset button. `mostRestrictive()` in `src/lib/filters.ts` tries removing each active filter group (trip fit included), picks the one that brings back the most cars, and names values for chip filters. **Bug fixed:** sr-only text escaped the table scroll areas, so the whole page scrolled sideways to 2,817 px at 1280 px. The scroll containers are now `relative`.
5. **Compare**: e2e covers the share link (the clipboard gets the exact URL, status says copied), "differences only" (fewer rows, every row differs, and back) and print view (no header, nav, tray or buttons; table fits). **Bug fixed:** the differences toggle and the remove links dropped `pay=loan|lease` from the URL. `compareUrl()` now keeps it.
6. **Rankings "best used EV under €15k / €20k / €25k"**: `src/lib/used-rankings.ts`, rendered by `top/[list]`. Ranked by km of real range per €1,000 of the typical used price, one row per generation. Only sourced bands with ≥ 5 samples count. The pages are **hidden tonight**: release 1 has no used prices, so they are not generated (404), not on /top and not in the sitemap, with the reason in code comments. `src/lib/used-rankings.test.ts` proves they appear with a fixture release holding 5 priced generations (page list, sitemap, NL only). The data comes from an optional `used_prices` array in catalogue.json via `catalogue.usedPrices()`; the schema field is the coordinator's call (Q-085).

Also: breadcrumbs have their own landmark label (`crumb.label`), the sort buttons have no aria-label (sr-only "Sort by"), Nerd targets are ≥ 24 px, and the lane AGENTS.md has rule 16 (colours from tokens) and new budget figures. New strings are in EN + NL (`theme.*`, `num.release`, `crumb.label`, `filters.vrange`, `explore.noResults.*`, `top.used.*`); other languages fall back.

Left / for others: Q-085 (used-price schema field; log the theme approach as a decision; era badge). The axe follow-ups are in A-04 (model page, /learn index, trip panel open, popovers open, manual screen-reader pass). Components still use Tailwind palette names through the bridge; moving them to token classes is cosmetic and can happen with the UX chat's component pass (fonts from `docs/design/fonts` are not wired yet).

## Review
