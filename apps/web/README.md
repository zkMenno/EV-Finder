# @ev/web

The EV Finder website (Next.js). Explore lives at `/{country}` (`nl`, `de`, `fr`, `be`, `uk`); `/` redirects to `/nl`.

## Run

From the repo root, once: `pnpm install`

```sh
cd apps/web
pnpm dev          # http://localhost:3000/nl
pnpm build        # production build
pnpm start        # serve the build
pnpm lint
pnpm typecheck
pnpm test         # Vitest units
pnpm exec playwright install chromium   # once
pnpm e2e          # Playwright smoke test (run `pnpm build` first)
```

## Data

The app reads the published catalogue release `../../data/releases/<n>/catalogue.json`, where `<n>` comes from `../../data/releases/latest`. Set `CATALOGUE_DIR` to use another releases directory. With no release, it falls back to the dev fixture `src/fixtures/catalogue.sample.json`. Those values are approximate and unsourced, and the footer says so.

The browser gets a compact copy for Explore at `/data/catalogue-<release>.json` (cached as immutable) or `/data/catalogue-dev.json` (fixture, no-cache).

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `EV Finder` | Brand name (still open) |
| `CATALOGUE_DIR` | `../../data/releases` | Releases directory |

## Routes

| Route | What |
|---|---|
| `/{country}` | Explore (filters, sort, table/cards, Simple/Detailed/Nerd) |
| `/{country}/learn/{term}` | Glossary learn pages (stubs) |
| `/{country}/compare?ids=a,b` | Compare (T-010, other builder) |
| `/data/catalogue-{release}.json` | Compact client catalogue |

Lane rules for agents: [AGENTS.md](AGENTS.md).
