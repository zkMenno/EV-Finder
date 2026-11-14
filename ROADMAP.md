# Roadmap — EV Finder

Where this project is going. The full plan, with phase gates and durations, lives in section 16 of the Master spec v2 (linked in DECISIONS.md). This file tracks the engineering side and keeps ideas from leaking into code.

**Scope guard:** every feature is **Core** (phases 0–2, the first complete version), **Next** (phases 3–5, once the data or users exist) or **Later** (parked until there's demand and revenue). Adding a Core item means removing one.

**Statuses:** `active` · `idea` · `parked` · `decided` (see DECISIONS.md)

---

## Phase 0 — Foundations `status: active`

Repo and infrastructure:
- [x] GitHub repo, licences, agent scaffold, CI skeleton, issue templates
- [ ] Monorepo skeleton: `apps/web`, `pipeline`, `packages/schema`, `infra`, each with a nested `AGENTS.md`
- [ ] Deploy on the AppInfra server: database + login in shared Postgres, Caddy route, staging, watchdog `/health` (Decision 006)
- [ ] Off-site backups confirmed working before launch (AppInfra #482)
- [ ] CI builds arm64 images and preview deploys per branch

Data:
- [ ] JSON Schema for Make → Model → Generation → Variant → Market variant → Fact
- [ ] Pipeline v0: OpenEV import, Bjørn Nyland sheet import, merge, validate, publish a release
- [ ] Real-range fallback model and back-test report
- [ ] Generations defined for every model, with change markers; top 40 used models hand-checked
- [ ] Country config for NL, DE, FR, BE, UK; UI strings in EN, NL, DE, FR, ES, IT

App:
- [ ] Staff area v0: vehicle editor and review queue

Non-code (Menno):
- [ ] Working name and domain
- [ ] Permission emails: Bjørn Nyland, NAF/Motor, Spritmonitor, EV Database
- [ ] Open-data coverage check for the full catalogue (~1,500 variants, incl. pre-2020)
- [ ] Affiliate programmes and pre-filled search URLs per launch country
- [ ] Book a legal check on automated price sampling (layer 3)
- [ ] Draft partner pitch: Autonex, Adevinta, Vend, OLX Group

## Phases 1–2 — Core product `status: idea`

Explore table, generation pages, compare tray, rankings, "See listings" links, light accounts. See spec §2–9.

## Phases 3–5 — Next `status: idea`

Listing feeds, price bands, Gem Score, alerts, battery-health context, PHEVs with 80 km+ electric range, US and Australia, then the rest of Europe.

## Parking lot `status: parked`

- Owner range logs and reviews
- TCO, import-cost and range-simulator tools
- Paid B2B API and widgets
- Vans
- China market

## Decided

- **Agent scaffold and workflow** → Decision 001
- **Public repo, AGPL + CC BY** → Decision 002
- **Lean monolith + pipeline** → Decision 003, hosting → Decision 006
- **Secrets and sampling config out of repo** → Decision 004

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
