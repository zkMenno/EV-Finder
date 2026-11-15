# @ev/web

The EV Finder website (Next.js). Explore lives at `/{country}` (`nl`, `de`, `fr`, `be`, `uk`); `/` redirects to `/nl`.

## Run

From the repo root, once: `pnpm install`

```sh
cd apps/web
pnpm dev          # http://localhost:3000/nl (regenerates the listings JSON first)
pnpm build        # production build (regenerates the listings JSON first)
pnpm start        # serve the build
pnpm lint
pnpm typecheck
pnpm test         # Vitest units
pnpm listings     # config/countries/*.yaml → src/config/listings.generated.json
pnpm exec playwright install chromium   # once
pnpm e2e          # Playwright smoke test (run `pnpm build` first)
```

From the repo root the same scripts run as `pnpm --filter @ev/web <script>` (CI runs lint, typecheck, test, build).

## Data

The app reads the published catalogue release `../../data/releases/<n>/catalogue.json`, where `<n>` comes from `../../data/releases/latest`. Set `CATALOGUE_DIR` to use another releases directory. With no release, it falls back to the dev fixture `src/fixtures/catalogue.sample.json`. Those values are approximate and unsourced, and the footer says so. Unit tests and e2e use the fixture (`E2E_CATALOGUE_DIR=../../data/releases pnpm e2e` runs the smoke test on the real release).

The browser gets a compact copy for Explore at `/data/catalogue-<release>.json` (cached as immutable) or `/data/catalogue-dev.json` (fixture, no-cache).

"Find a charger / plan a trip" links come from `charging_links` in the same country files (`pnpm charging-links` → `src/config/charging-links.generated.json`); none configured yet means no block.

"See listings" deep links come from `config/countries/<country>.yaml` at the repo root: public search URLs only (Decision 004), all unverified. `pnpm listings` validates them and writes `src/config/listings.generated.json`, which the server imports (no YAML parser at runtime). Commit the regenerated JSON; a unit test fails when it is stale.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `EV Shortlist` | Brand name (working title, Decision 018) |
| `CATALOGUE_DIR` | `../../data/releases` | Releases directory |
| `STAFF_PAGES` | off | `1` turns on `/staff/review`; otherwise it is a 404 |
| `REVIEW_DIR` | `../../data/review` | Folder with the pipeline's review CSVs (staff page) |
| `TRIP_FIT` | off | `1` shows the trip fit quick check on Explore ("Find cars for my trips"); otherwise no trip UI |
| `CHARGING_LINKS_FILE` | unset | Tests only: JSON file replacing the charging link-out config |

## Routes

| Route | What |
|---|---|
| `/` | Redirects to `/nl` |
| `/{country}` | Explore (filters, sort, table/cards, Simple/Detailed/Nerd); rows link to variant pages |
| `/{country}/ev/{make}/{model}` | Model overview: generations, years, RDW count |
| `/{country}/ev/{make}/{model}/{generation}` | Generation: key facts, spec diff across variants, See listings, RDW count |
| `/{country}/ev/{make}/{model}/{generation}/{variant}` | Variant spec sheet, add to compare, See listings |
| `/{country}/compare?ids=a,b` | Compare up to 4 cars (`&diff=1` = only differences; print view); noindex |
| `/{country}/top` | Rankings index |
| `/{country}/top/{list}` | `longest-real-range-under-30k`, `fastest-dc`, `most-available-nl` |
| `/{country}/learn/{term}` | Glossary learn pages (stubs) |
| `/staff/review?file=unmatched\|conflicts&source=…&page=…` | Staff only (`STAFF_PAGES=1`): read-only review queue, 500 rows per page; noindex |
| `/data/catalogue-{release}.json` | Compact client catalogue |
| `/health` | Liveness probe (status, release number, time) |

Any page takes `?lang=en|nl|de|fr|es|it` (also stored in a cookie); otherwise the country's default language is used. All pages render on demand (Q-033, Q-034).

Lane rules for agents: [AGENTS.md](AGENTS.md).
