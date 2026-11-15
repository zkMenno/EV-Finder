# EV Shortlist (working title)

Find the right used EV, then the right car.

EV Shortlist (repo: EV-Finder) is a free, independent catalogue of electric cars built for people buying second-hand. It groups every model by generation and shows new and used prices side by side, along with real-world range and charging speed that we work out ourselves from public tests and owner data. It covers several countries, starting with the Netherlands, Germany, France, Belgium and the UK.

It is a finder, not a marketplace. We don't host listings. We link you to them.

> **Status:** pre-alpha. Nothing to run yet. Phase 0 (foundations) is in progress; see [ROADMAP.md](ROADMAP.md).

## What it will do

- **Explore:** one fast, filterable table of every EV, grouped Model → Generation → Variant. No sign-up needed.
- **Real numbers:** real-world range (mild, winter, motorway) and charging in km added per 10 minutes, each with its source and a confidence level.
- **Used market:** typical used price per generation and country, with "See listings" links to the big marketplaces.
- **Compare and shortlist:** compare up to four cars side by side and save shortlists. Nothing resets.

## Principles

- **Every number is traceable.** Each value carries its source, date and confidence.
- **Independent.** Money never buys a ranking position or a score.
- **Open where it helps.** Summary data is published under CC BY 4.0.
- **Boring tech.** One web app, one database, one data pipeline, hosted in the EU.

## Stack (planned)

Next.js + TypeScript · Postgres + PostGIS · Python data jobs · hosted in the EU on Hetzner. Details: [DECISIONS.md](DECISIONS.md).

## Repo layout

| Path | What it is |
|---|---|
| `AGENTS.md` | Rules for AI coding agents (and humans) working here |
| `BOARD.md` | What's happening now, next, blocked and done |
| `QUESTIONS.md` | Open questions for the maintainer |
| `DECISIONS.md` | Every architectural decision, with reasons |
| `ROADMAP.md` | Phases and ideas |
| `tasks/` | One file per task |
| `research/`, `audits/` | Research notes and audit reports |
| `apps/web/`, `pipeline/`, `packages/schema/`, `infra/` | Code (arrives in Phase 0) |

## Licences

- **Code:** [GNU AGPL-3.0](LICENSE). If you run a modified version as a public service, you must share your changes.
- **Published data:** [CC BY 4.0](DATA_LICENSE.md). Reuse it freely, with credit.
- **Third-party data** keeps its own licence. See [DATA_LICENSE.md](DATA_LICENSE.md).

## Contributing

Found a wrong number? [Report a data issue](../../issues/new?template=data-issue.yml). For anything else, see [CONTRIBUTING.md](CONTRIBUTING.md).

Security issues: see [SECURITY.md](SECURITY.md). Please don't open public issues for them.
