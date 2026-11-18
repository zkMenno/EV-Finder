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
- [ ] **Backups** (AppInfra #93): before live, or before staging gets real users, AppInfra adds EV's data to the nightly backup + off-site copy.
  - Not needed yet (checked 2026-11-17): at launch EV stores nothing that can't be rebuilt. The catalogue is release files (git + GitHub Releases), the web containers are read-only, no database is in use (Decision 008), and `/srv/ev/data` holds only pipeline working files rebuilt from git and object storage. Staging runs the same image with public catalogue data only, so it is not backed up.
  - Trigger: the first data only the server holds (the `ev` Postgres database getting real rows, e.g. accounts, favourites or alerts, all after launch; uploaded files; or real users on staging). Then open an AppInfra issue, label `handoff`, "From: EV Shortlist: add EV data to the nightly backup" (what, container/volume/database name, expected size, staging yes/no). AppInfra's `scripts/backup.sh` only dumps databases it names, so a new `ev` database is **not** backed up by default.
  - Privacy page (when EV gets one): backup copies are kept at most 32 days (AppInfra README, "How long backups are kept").
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

Also Core: charging buildout (link-outs, /learn "Charging in 2026", country pages) and bidirectional charging + plugs (phase 1: schema, EU plug data, "buying a wallbox from 2027" learn section; phase 2: V2H/V2G filters, caveat badges, model-page "Power out" block). See docs/spec/bidirectional-and-connectors.md, Decision 011.

## Phases 3–5 — Next `status: idea`

Listing feeds, price bands, Gem Score, alerts, battery-health context, PHEVs with 80 km+ electric range, US and Australia (incl. CCS1/NACS ports per model year and the Supercharger filter, T-022), then the rest of Europe.

## Parking lot `status: parked`

- Owner range logs and reviews
- TCO, import-cost and range-simulator tools
- Paid B2B API and widgets
- Vans
- China market
- Catalogue long tail: rare models, ~900–1,200 variants in total (R-41 task 5; WS0 2026-11-18: after launch)

## Decided

- **Agent scaffold and workflow** → Decision 001
- **Public repo, AGPL + CC BY** → Decision 002
- **Lean monolith + pipeline** → Decision 003, hosting → Decision 006
- **Secrets and sampling config out of repo** → Decision 004

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
