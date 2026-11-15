# T-050 Country + language URLs, static pages again
Role: builder   Lane: apps/web (+ config/countries/*.yaml language keys)   Wave: overnight 1 (addendum 5 item 1)
Status: review

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

## Review
