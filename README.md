# EV Shortlist

Find the right used EV, then the right car.

EV Shortlist is a free, independent catalogue of electric cars built for people buying second-hand. It groups every model by generation and shows new and used prices side by side, along with real-world range and charging speed that we work out ourselves from public tests and owner data. It covers several countries, starting with the Netherlands, Germany, France, Belgium and the UK.

It is a finder, not a marketplace. We don't host listings. We link you to them.

> **Status:** working prototype, **not live**. The web app runs locally on a published catalogue release (release 1, 40 seed models); the pipeline builds releases from seven open sources. Nothing is deployed yet (see [infra/README.md](infra/README.md)). Phase 0 is in progress: [ROADMAP.md](ROADMAP.md).

## Quick start

Needs Node 22+ with pnpm (via `corepack enable`), Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
pnpm install --frozen-lockfile        # web app + schema package (pnpm workspace)
pnpm --filter @ev/schema test         # JSON Schema checks
pnpm --filter @ev/web dev             # web app on http://localhost:3000, reads data/releases/<latest>

cd pipeline && uv sync && uv run pytest -q    # pipeline tests (no network)
uv run ev release --dry-run                   # build a release in memory, write nothing
```

More: [pipeline/README.md](pipeline/README.md) (run, test, release, add a source),
[apps/web/README.md](apps/web/README.md), [infra/README.md](infra/README.md) (deploy, not applied).
Local settings: copy `.env.example` to `.env`; never commit it.

## What it does

- **Explore:** one fast, filterable table of every EV, grouped Model → Generation → Variant. No sign-up needed.
- **Real numbers:** real-world range (mild, winter, motorway) and charging in km added per 10 minutes, each with its source and a confidence level.
- **Used market:** typical used price per generation and country, with "See listings" links to the big marketplaces.
- **Compare and shortlist:** compare up to four cars side by side and save shortlists. Nothing resets.

## Principles

- **Every number is traceable.** Each value carries its source, date and confidence.
- **Independent.** Money never buys a ranking position or a score.
- **Open where it helps.** Summary data is published under CC BY 4.0.
- **Boring tech.** One web app, one database, one data pipeline, hosted in the EU.

Stack: Next.js + TypeScript · Python pipeline (uv) · JSON Schema for shared types · later Postgres + PostGIS · shared Hetzner Arm server in the EU. Why: [DECISIONS.md](DECISIONS.md).

## Repo map

| Path | What it is |
|---|---|
| `apps/web/` | Next.js web app (URLs `/{country}/{lang}/…`, Decision 015) |
| `pipeline/` | Python data pipeline: `ev fetch / normalise / release` |
| `packages/schema/` | JSON Schema, the single source for TypeScript and Python types |
| `infra/` | Deploy config for the shared AppInfra server (not applied yet) |
| `data/` | `seed/` (hand-curated models and variants), `taxonomy/` (lookup tables), `sources.yaml` + [`SOURCES.md`](data/SOURCES.md) (source registry and licences), `field_sources.yaml` (which source wins per field), `releases/<n>/` (published catalogue), `review/` (unmatched, conflicts, dropped values). `raw/`, `staging/`, `local/` are git-ignored. |
| `config/` | `brand.yaml` (working name, change it only here), `countries/` (per-country settings), `price-index/` (placeholder) |
| `content/learn/` | Plain-language /learn articles, one Markdown file per language |
| `docs/` | `spec/` (mirror of the product spec; builders read this), `growth/`, `outreach/`, `brand/` |
| `research/` | Research notes (below) |
| `audits/` | Performance and security audits (A-01, A-02) |
| `workstreams/` | One folder per long-running chat (WS0–WS5, UX, OVERNIGHT): `START.md`, `STATUS.md`, `INBOX.md` |
| `tasks/` | One file per task |
| `AGENTS.md`, `CLAUDE.md` | Rules for AI agents (and humans) working here |
| `BOARD.md`, `QUESTIONS.md`, `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `CHATS.md` | Board, open questions for the maintainer, decisions, phases, what shipped, chat list |

### Research

- [R-01](research/R-01-bidirectional-and-connectors.md): bidirectional charging (V2L/V2H/V2G) and plug standards
- [R-02](research/R-02-official-ev-sources.md): official open EV data for NL, DE, FR, BE, UK and the EU
- [R-03](research/R-03-price-sampling-legal-brief.md): legal brief on used-price sampling
- [R-04](research/R-04-privacy-gdpr.md): privacy and GDPR
- [R-05](research/R-05-data-qa-plan.md): data QA, back-tests and release checks
- [R-06](research/R-06-official-ev-sources-future-markets.md): official EV data sources, future markets
- [R-07](research/R-07-official-ev-sources-europe-expansion.md): official EV data sources, European expansion

## Licences

- **Code:** [GNU AGPL-3.0](LICENSE). If you run a modified version as a public service, you must share your changes.
- **Published data:** [CC BY 4.0](DATA_LICENSE.md). Reuse it freely, with credit. Each release ships an open bundle in `data/releases/<n>/open/`.
- **Third-party data** keeps its own licence; see [data/SOURCES.md](data/SOURCES.md) and [DATA_LICENSE.md](DATA_LICENSE.md). ODbL data never enters CC BY output.

## Contributing

Found a wrong number? [Report a data issue](../../issues/new?template=data-issue.yml). For anything else, see [CONTRIBUTING.md](CONTRIBUTING.md).

Security issues: see [SECURITY.md](SECURITY.md). Please don't open public issues for them.

Architecture overview (system map, data model, tech board): https://claude.ai/artifact/9wDnjtwg7iFcFtfSAoATKH
