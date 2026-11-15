# @ev/web

The EV Finder website (Next.js). Every page lives at `/{country}/{lang}/…` (Decision 015): countries `nl`, `de`, `fr`, `be`, `uk`; each serves its own languages plus English (from `config/countries/<cc>.yaml` `languages` / `default_language`): `/nl/nl`, `/nl/en`, `/de/de`, `/de/en`, `/fr/fr`, `/fr/en`, `/be/nl`, `/be/fr`, `/be/de`, `/be/en`, `/uk/en`. Explore is `/{country}/{lang}`; `/` and `/{country}` redirect.

## Run

From the repo root, once: `pnpm install`

```sh
cd apps/web
pnpm dev          # http://localhost:3000/nl/nl (regenerates the generated config JSON first)
pnpm build        # production build: generated JSON, next build, then the CSP hash manifest
pnpm start        # serve the build
pnpm lint
pnpm typecheck
pnpm test         # Vitest units
pnpm listings     # config/countries/*.yaml → src/config/listings.generated.json
pnpm countries    # config/countries/*.yaml languages → src/config/countries.generated.json
pnpm finance      # data/taxonomy/finance_profiles.yaml → src/config/finance.generated.json
pnpm learn        # content/learn/**.md → src/config/learn.generated.json (front matter + Markdown subset)
pnpm theme        # docs/design/tokens.json → src/app/tokens.generated.css (both themes)
pnpm exec playwright install chromium   # once
pnpm e2e          # Playwright: flows + axe accessibility check (run `pnpm build` first)
AXE_REPORT=1 pnpm exec playwright test e2e/a11y.spec.ts   # print every axe finding, moderate ones too
```

From the repo root the same scripts run as `pnpm --filter @ev/web <script>` (CI runs lint, typecheck, test, build).

## Data

Model, generation, variant, learn, rankings and about pages are **static** (built once per release, ~4,200 pages): a new release needs a new build/image (Q-070). `next build` fails if `data/releases/latest` exists but can't be read, and the post-build CSP step fails if a catalogue page came out as a 404. Explore and Compare render on demand.

The app reads the published catalogue release `../../data/releases/<n>/catalogue.json`, where `<n>` comes from `../../data/releases/latest`. Set `CATALOGUE_DIR` to use another releases directory. With no release, it falls back to the dev fixture `src/fixtures/catalogue.sample.json`. Those values are approximate and unsourced, and the footer says so. Unit tests use the fixture where they need fixed data; e2e runs on the published release (the same data the static pages are built from; `E2E_CATALOGUE_DIR` overrides).

The browser gets a compact copy for Explore at `/data/catalogue-<release>.json` (cached as immutable) or `/data/catalogue-dev.json` (fixture, no-cache).

"Find a charger / plan a trip" links come from `charging_links` in the same country files (`pnpm charging-links` → `src/config/charging-links.generated.json`); none configured yet means no block.

"See listings" deep links come from `config/countries/<country>.yaml` at the repo root: public search URLs only (Decision 004), all unverified. `pnpm listings` validates them and writes `src/config/listings.generated.json`, which the server imports (no YAML parser at runtime). Commit the regenerated JSON; a unit test fails when it is stale.

## Themes

Two themes from the design system (`docs/design/tokens.json`): light **Day trip** and dark **Night drive**. `pnpm theme` (also run by `dev` and `build`) writes the colour tokens as CSS variables into `src/app/tokens.generated.css`; commit it (a unit test fails when it is stale; the Docker build has no `docs/` and keeps the committed file). `src/app/globals.css` points Tailwind's slate / blue / amber / green / red / white palette at the tokens, so existing classes follow the theme. In new code, use the tokens directly (`bg-[var(--surface)]`, `text-[var(--ink-2)]`) and never paste hex values.

- Default: the system setting (`prefers-color-scheme`).
- The "Night drive" button in the header (`src/components/ThemeToggle.tsx`) remembers the choice in localStorage (`ev-finder:theme:v1`, `src/lib/theme.ts`).
- `/theme-init.js` (a same-origin route, `src/app/theme-init.js/route.ts`) applies the stored choice before first paint. It is a file, not an inline script, so the CSP needs no change.
- Print always uses the light theme.

## Accessibility

`e2e/a11y.spec.ts` runs axe-core (`@axe-core/playwright`) on Explore (table, cards, Nerd), a generation page, a variant page, Compare, a /learn guide and a ranking list, in both themes. It fails on critical and serious violations. Results and what is not covered yet: `audits/A-04-accessibility.md`. Keyboard order and focus rings: `e2e/polish.spec.ts`, `e2e/review.spec.ts`.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `EV Shortlist` | Brand name (working title, Decision 018) |
| `APP_URL` | `http://localhost:3000` | Canonical origin for hreflang and `sitemap.xml` (read at build time for static pages) |
| `CATALOGUE_DIR` | `../../data/releases` | Releases directory |
| `STAFF_PAGES` | off | `1` turns on `/staff/review`; otherwise it is a 404 |
| `STAFF_BASIC_AUTH` | unset | `user:pass` required (HTTP Basic) on `/staff/*` when `STAFF_PAGES=1`; unset = always 401 |
| `REVIEW_DIR` | `../../data/review` | Folder with the pipeline's review CSVs (staff page) |
| `TRIP_FIT` | off | `1` shows the trip fit quick check on Explore ("Find cars for my trips"); otherwise no trip UI |
| `CHARGING_LINKS_FILE` | unset | Tests only: JSON file replacing the charging link-out config |

## Routes

`{base}` = `/{country}/{lang}` (a served pair). SSG = static, built per release; ƒ = on demand.

| Route | What |
|---|---|
| `/` | 307 → `/nl/{remembered language or nl}` |
| `/{country}` | 307 → `/{country}/{remembered language if served, else default_language}` |
| `/{country}/…` (old, no language) | 308 → same page in `?lang=` if served, else the default language |
| `/{country}/{unserved lang}/…` | 308 → the default language |
| `{base}` | Explore (filters, sort, table/cards, Simple/Detailed/Nerd, price mode); ƒ |
| `{base}/ev/{make}/{model}` | Model overview: generations, years, RDW count; SSG |
| `{base}/ev/{make}/{model}/{generation}` | Generation: key facts, spec diff, price mode + loan calculator, See listings; SSG |
| `{base}/ev/{make}/{model}/{generation}/{variant}` | Variant spec sheet, price mode + loan calculator, add to compare, See listings; SSG |
| `{base}/compare?ids=a,b` | Compare up to 4 cars (`&diff=1`, `&pay=loan`, print view); noindex; ƒ |
| `{base}/top`, `{base}/top/{list}` | Rankings; SSG. `best-used-under-15k/20k/25k` exist only where at least 5 generations have a sourced used price (none in release 1: 404, not linked) |
| `{base}/learn` | Learn index: guides (`content/learn/index.yaml`) + glossary A–Z; SSG |
| `{base}/learn/{slug}` | A guide from `content/learn/<slug>/<lang>.md` (EN fallback with a notice, draft banner, sources, ⓘ terms) or a glossary term; SSG |
| `{base}/about` | About, method, licences, credits; SSG |
| `/staff/review?file=…` | Staff only (`STAFF_PAGES=1` + `STAFF_BASIC_AUTH`); noindex |
| `/sitemap.xml`, `/robots.txt` | Served pairs × indexable pages (no compare, no staff) |
| `/data/catalogue-{release}.json` | Compact client catalogue |
| `/health` | Liveness probe (status, release number, time) |
| `/theme-init.js` | Applies the remembered theme before first paint |

Every page has canonical + hreflang for all 11 served pairs + `x-default` (`/nl/en/…`). The browser language (`Accept-Language`) never redirects; a dismissible banner suggests a served language. The language switcher keeps the path and query (filters) and remembers the choice in a cookie used only by the `/{country}` redirect.

Query keys Explore owns are in `src/lib/state.ts` (`ExploreState`), including `pay=loan|lease` (price mode, Decision 017; also remembered in localStorage).

## Security

`src/proxy.ts` sets the Content-Security-Policy per request (`src/lib/csp.ts`): no `'unsafe-inline'` for scripts; a fresh nonce on dynamic pages, and on static pages the sha256 hashes of their inline scripts from `.next/server/csp-hashes.json` (written by `scripts/csp-hashes.mjs` at the end of `pnpm build`). Other headers are in `next.config.ts`.

Lane rules for agents: [AGENTS.md](AGENTS.md).
