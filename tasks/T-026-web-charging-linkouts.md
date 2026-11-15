# T-026 Charging link-out block + plain ABRP link
Role: WS2   Lane: apps/web   Wave: 6
Status: review (builder, 2026-11-15)

## Goal
Show the per-country "Find a charger / plan a trip" block on country, model and /learn pages (Core 1).

## Acceptance criteria
- [ ] Reads config/countries charging links; no API calls
- [ ] Text links, new tab, rel=noopener, UTM tag
- [ ] Model page footer has a plain ABRP link (car pre-selection waits for T-029)
- [ ] Works at 360 px; i18n keys for all labels

## Inputs
docs/spec/charging-buildout.md (What we build, Link rules), T-024.

## Out of scope
Country charts (T-028).

## Handoff notes
- **Config:** `charging_links` in `config/countries/<cc>.yaml` (T-024 wrote them for all five countries during this run; the generated JSON is regenerated and committed-ready). Up to 5 rows: `job`, `label`, `url` (https), `order`, optional `tool`, `official`, `utm`, `deep_link_template`. `apps/web/scripts/charging-links.mjs` validates (max 5, https, no partner/affiliate/secret keys, no duplicates) and writes `src/config/charging-links.generated.json`; `build`/`dev` run it and a unit test fails when it is stale. `scripts/listings.mjs` now accepts the `charging_links` key. Location vs Decision 012's `country_charging_links`: Q-056.
- **Render:** `src/lib/charging-links.ts` + `src/components/ChargingLinks.tsx` (server component, no JS). Text links only, new tab, `rel="nofollow noopener"` (`noopener` only for `official: true`), UTM `utm_source=evfinder&utm_medium=referral&utm_campaign=charging_links` (unless `utm: false` or the URL already has one). Job descriptions come from i18n `charging.job.<job>` when the key exists (official-map, local-app, map, route-planner, price-compare: the schema's `CountryChargingLink.job` values).
- **Where:** below Explore on the country page, at the end of /learn pages, and in the footer of model, generation and variant pages. Model pages drop ABRP from the block and add a plain ABRP line (`abrpLink()`, https://abetterrouteplanner.com/ + UTM, no car pre-selection until T-029).
- **i18n:** `charging.*` in EN + NL (server-only prefix). 360 px checked in e2e (block width and no page overflow on a model page).
- **Tests:** `src/lib/charging-links.test.ts` (rules, max 5, ABRP de-dupe, validation, drift guard, override file), `e2e/charging-links.spec.ts` using `e2e/fixtures/charging-links.json` through `CHARGING_LINKS_FILE` (set in `playwright.config.ts`); Germany empty → no block.
- No internal paths are built in the new code (ready for the Decision 015 route move).

## Review
