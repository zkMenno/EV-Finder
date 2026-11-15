# Decisions — EV Finder

Engineering decisions for this repo, in a light ADR (Architectural Decision Record) format. Each entry has a number, status, date, context, decision and consequences. Never edit an accepted decision; supersede it with a new one.

**Product decisions** (scope, markets, business) live in the project decisions log and the Master spec v2: https://claude.ai/artifact/3HiNR86a22Fnm2kHxpfctx. This file records the ones that shape the code.

**Statuses:** Proposed · Accepted · Superseded by NNN

---

## Decision 001: Adopted agentic scaffold and the agent workflow

**Status:** Accepted
**Date:** 2026-11-15

**Context:** The project is built by one person with many AI agents. Chats and sessions forget; files don't. Agents need shared rules, clear lanes and a place to hand off work.

**Decision:** Use the Agentic Scaffold pattern (AGENTS.md as canon, CLAUDE.md as wrapper, DECISIONS, CHANGELOG, ROADMAP) plus the workflow from the spec's Workflow tab: `BOARD.md`, `QUESTIONS.md`, `tasks/`, `research/`, `audits/`, five roles, one lane per builder.

**Consequences:**
- Agents have clear instructions from session one.
- Menno touches three things: `QUESTIONS.md`, the daily digest and phase gates.
- A few extra files, each with one job.

**Alternatives considered:** README only (not enough for agents); a project-management tool outside the repo (agents can't read it reliably).

---

## Decision 002: Public repo; AGPL-3.0 for code, CC BY 4.0 for published data

**Status:** Accepted
**Date:** 2026-11-15

**Context:** A public repo gets GitHub Actions minutes free on standard runners, plus free secret scanning. The project is mission-driven and open-source-first, but a closed clone of the hosted site would undercut it.

**Decision:**
- Repo is public.
- Code is licensed under **GNU AGPL-3.0** (`LICENSE`): anyone running a modified version as a network service must publish their changes.
- Data we publish openly is licensed under **CC BY 4.0** (`DATA_LICENSE.md`). Third-party inputs keep their own licences; ODbL inputs are never mixed into CC BY sets.
- Outside contributions require agreeing to the relicensing clause in `CONTRIBUTING.md`, so the maintainer can still change the licence later.

**Consequences:**
- Free CI and security tooling.
- Competitors can read the code, but can't run a closed fork as a service.
- Strategy-sensitive config must stay out of the repo (see 004).

**Alternatives considered:** MIT (allows closed SaaS clones); FSL/BSL source-available (not OSI open source, less community goodwill); no licence (blocks contributions).

---

## Decision 003: Lean monolith + separate data pipeline, one EU server

**Status:** Superseded by 006 (hosting and pipeline tooling); the monolith shape still holds
**Date:** 2026-11-15 (product decision 2026-11-14)

**Context:** A solo builder with AI agents must be able to understand, run and fix everything.

**Decision:** One monorepo with `apps/web` (Next.js + TypeScript), `pipeline/` (Python + Dagster, DuckDB + Parquet), `packages/schema` (JSON Schema → generated TS and Python types) and `infra/`. One Postgres database. pg-boss for jobs (no Redis). Better Auth for passkeys and magic links. Hosted on Hetzner via Coolify, Bunny CDN, S3-compatible object storage for raw fetches. Self-hosted Umami, GlitchTip and Uptime Kuma.

**Consequences:**
- The pipeline writes catalogue releases; the web app only reads them (and writes user data).
- Scale steps happen only on triggers (spec §13): Meilisearch above ~100k listings, a read replica above ~60% DB CPU, the pipeline on its own server if runs collide with traffic.

---

## Decision 004: Keep sampling targets and partner secrets out of the public repo

**Status:** Accepted
**Date:** 2026-11-15

**Context:** Automated used-price sampling (layer 3) carries ToS and EU database-right risk and needs a legal check before going live. Publishing exactly which sites we sample, and how often, adds risk and gives away strategy. Affiliate and partner credentials are secrets.

**Decision:** The code for sampling is generic and public. Target sites, URL templates for sampling, rates, kill-switch state and all partner/affiliate credentials live in runtime config (Coolify environment, or a private config repo), never in this repo. "See listings" deep-link templates (public, user-facing links) may live in the country config.

**Consequences:** `.env.example` documents variable names only. Reviewers reject PRs that hard-code targets or keys. GitHub secret scanning and push protection are on.

---

## Decision 005: Build images in GitHub Actions, not on the server

**Status:** Accepted (deploy details in 006)
**Date:** 2026-11-15

**Context:** The app will share an existing Hetzner Arm server. Building Next.js on the server peaks at 2–4 GB RAM and can starve other services. Public repos get free Actions minutes, including arm64 runners.

**Decision:** CI builds arm64 Docker images for `apps/web` and `pipeline`, pushes them to GitHub Container Registry, and the server pulls and runs them (SSH deploy, see 006).

**Consequences:** Likely no server upgrade at launch (to be confirmed once current free RAM is known). Adds a deploy workflow in Phase 0 (`infra` lane).


---

## Decision 006: Host on the shared AppInfra server; drop Coolify, Dagster and Brevo

**Status:** Accepted (limits to confirm with the capacity check, Q-001)
**Date:** 2026-11-15
**Source:** advice from AppInfra, agreed in the project chat; spec §13 updated to match.

**Context:** Menno already runs a Hetzner CAX31 (Arm, 8 cores, 16 GB) with Caddy, an image-based deploy, backups, a watchdog, Umami and staging for GardenLayer and Dungeon Tracker. Reusing that is cheaper and simpler than a new Coolify setup. Dagster's always-on services cost about 1–1.5 GB, too much on a shared server.

**Decision:**
- **Server:** the shared AppInfra server. Reuse Caddy, CI → Arm image → SSH deploy, backups, the `/health` watchdog, Umami, Scaleway email, the Sveltia editor and the staging setup. No Coolify.
- **Database:** EV Finder gets its own database, login and private network inside the shared Postgres 17 + PostGIS. No separate Postgres container. Connection pool: about 10 live, 3 staging, 3 jobs, out of the server's 100.
- **Pipeline:** Python jobs queued and scheduled through pg-boss. No Dagster. Raw snapshots go to Scaleway Object Storage.
- **Limits:** `ev-web` 768 MB / 1 CPU; `ev-web-staging` 256 MB / 0.5 CPU; `ev-jobs` 1 GB / 1 CPU at low priority, nightly only (🟡 00:30–02:30 UTC, to confirm).
- **Fit:** about 13.8 GB of 16 GB in limits by day, about 14.8 GB in the job window. Works while the paused Cahier app stays off.
- **When to grow:** upgrade, or move GardenLayer to its own server, once busy evenings show more than 70% RAM or CPU for weeks.
- "Coolify environment" in Decision 004 now means the server's env files.

**Consequences:**
- Provenance no longer comes from Dagster lineage. Every Fact stores source and date itself, and each job writes a run log (AGENTS.md, Python conventions).
- The shared Postgres has no CPU limit, so heavy imports run at night at low priority. Big one-off imports run on a temporary machine.
- 🔴 Off-site backups on the server may not be running. Fix that (AppInfra #482) before launch; it affects the other apps too.

---

## Decision 007: pnpm for the web app, uv for the pipeline

**Status:** Proposed (provisional, pending Q-002)
**Date:** 2026-11-15

**Context:** The overnight prototype needed a package manager before Q-002 was answered.

**Decision:** pnpm workspace at the root (`apps/*`, `packages/*`); uv for `pipeline/` (Python 3.12+). CI keeps a pip fallback so the existing auto-detect job still works.

**Consequences:** Easy to swap back to npm/pip if Q-002 says so: only lockfiles and CI install lines change.

---

## Decision 008: Prototype reads a published catalogue JSON, not Postgres

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** No database tonight. The web app still needs a stable read path that Postgres can replace later.

**Decision:** The pipeline writes `data/releases/<n>/catalogue.json` (one wide `PublishedVariant` row per variant) plus Parquet. The web app reads it through one `Catalogue` interface in `apps/web/src/lib/catalogue.ts`; a Postgres/Drizzle implementation can sit behind the same interface. Release numbers are integers counting up from 1 (`data/releases/1/`), with `data/releases/latest` naming the current one.

**Consequences:** Releases are plain files, so rollback means pointing `latest` back. Small releases live in git for now; move them to object storage once they grow.

---

## Decision 009: Source registry, per-field source rules, conflicts, coverage and charge curves

**Status:** Proposed (provisional, from the latest spec decisions, 2026-11-15 00:45)
**Date:** 2026-11-15

**Context:** Merging needs explicit rules per field, and we must be able to prove which sources may reach a public release.

**Decision:**
- `data/sources.yaml` lists every source: id, owner, licence, access (api | bulk | manual), cadence, terms note, status (active | waiting_permission | blocked). Only `active` sources with a named licence or written permission reach a public release.
- `data/field_sources.yaml` says, per field, which 1–2 primary sources to use, the fallbacks in order, the tolerance and the merge rule (priority | median | newest).
- Values that agree within tolerance raise confidence and count towards "N sources agree" (`FieldProvenance.agreeing_sources`). Conflicts outside tolerance go to `data/review/conflicts.csv` and are never averaged.
- Each release writes `coverage.md`: per field, the share of variants with ≥2 agreeing sources, 1 source, estimate only, or missing.
- DC charge curves are a Fact whose value is a `ChargeCurve`: (state of charge %, kW) points, conditions (battery temp, preconditioned, ambient temp, charger kW, software version) and a status of measured, estimated or default. From it we derive the average kW and minutes from 10 to 80%, km added in 10 and 20 minutes at motorway consumption, minutes above 90% of peak, and claim vs measured.
- The DC ranking uses km added in 20 minutes, not peak kW.
- Provisional estimates: motorway consumption = WLTP × 1.30; a generic default curve shape when no curve exists. Both are labelled "estimate".

**Consequences:** Most fields tonight have one source or an estimate, and coverage.md shows that honestly. Maker documents stay `blocked` until Q-008 is answered.

---

## Decision 010: Platforms, battery packs, taxonomy tables and display levels

**Status:** Proposed (provisional, addendum 3, 2026-11-15 00:48)
**Date:** 2026-11-15

**Context:** Voltage, chemistry and cooling matter to used buyers (fast charging on older chargers, daily charging to 100%) but are poorly explained elsewhere. Many variants share one pack, so pack facts should live in one place.

**Decision:**
- New entities `Platform` and `BatteryPack`. A Variant points to one of each. Pack facts (supplier, chemistry, cathode detail, cell format, cell-to-pack, gross/usable kWh, nominal and max V, cooling, warranty) are inherited by its variants unless the variant has its own measured fact.
- Taxonomies are data files in `data/taxonomy/`, not enums: `voltage_classes` (400 V ~300–550, 800 V ~550–850, 900 V+ ~850–1,100), `chemistries` (NMC, NCA, LFP, LMFP, LMO/NMC blend, sodium-ion, semi-solid, all-solid-state, LMR), `cooling_types` (liquid, refrigerant, air, passive) and `glossary_terms`, all with per-language strings. Filters, tooltips and learn pages read them, so adding a row needs no code change. The schema ids are free strings validated against these files at release time.
- Per variant: stated nominal/max voltage, marketing label, derived class, switchable flag and "400 V charger behaviour" (native | booster kW | limited kW). `not-disclosed` is a valid value everywhere.
- The UI has a Simple / Detailed / Nerd switch (localStorage + URL). Nerd shows raw values, sources with date and confidence, and the fallback rung. Every glossary term gets an ⓘ tooltip; labels are plain language with the technical name underneath; `/learn/[term]` pages are stubs tonight.

**Consequences:** The catalogue JSON ships the taxonomy tables, which adds a few KB. Most pack facts tonight come from hand-entered seed data (confidence low) or are `not-disclosed`.

---

## Decision 011: Bidirectional charging and plug standards as country-aware, conditional facts

**Status:** Accepted (WS0, 2026-11-15)
**Date:** 2026-11-15

**Context:** Menno asked for filters on which cars support V2G/V2H, which work with the EU 2027 protocol, and with which caveats; plus CCS/NACS filters for the US. Research R-01: from 1 Jan 2027 AFIR (Delegated Regulation (EU) 2025/656) requires ISO 15118-20 on every new or renovated EU charging point, private ones included, but that is a protocol duty, not a bidirectional-hardware duty. Whether a car can actually do V2H/V2G depends on software version, battery size, build date, wallbox route (AC vs expensive DC box), energy contract and country. US ports switch from CCS1 to NACS by model year.

**Decision:**
- New taxonomies: `bidi_modes`, `bidi_routes`, `bidi_protocols`, `bidi_caveats`, `bidi_status`, `connector_types`, `bidi_equipment` (data rows, per-language strings).
- New entities `BidiCapability` (per variant or platform, with per-country status and conditions) and `ChargingPort` (per variant, market and model year). New variant Fact `iso15118_20_support` (default `not_disclosed`, never inferred).
- Filters default to "live in your selected country". Conditional eligibility is shown as conditions, never as a plain tick. Caveats come from the taxonomy, never free text.
- Copy rule: never say new 2027 chargers "are bidirectional"; say they "speak the standard that allows it".
- Bidi facts expire: older than 90 days shows "may be out of date".
- Phasing in docs/spec/bidirectional-and-connectors.md §4 (schema + EU ports + learn section Core 1; bidi filters Core 2; US ports/NACS Next).

**Consequences:** More rows per variant and a monthly re-check job for bidi facts. Most cars will show "not offered" or "not disclosed" for ISO 15118-20 at first, which is honest.

## Decision 012: Charging infrastructure as aggregate statistics with one definition per series

**Status:** Accepted (WS0, 2026-11-15)
**Date:** 2026-11-15

**Context:** Spec tab "Charging buildout" (docs/spec/charging-buildout.md): buyers still picture the 2019 network. Countries count charging points, devices, locations and connectors differently (Belgium: ~22k fully public vs ~126k public + semi-public). Open Charge Map's per-location CC BY-SA licences clash with our CC BY 4.0 output.

**Decision:**
- Aggregates only (counts, power, per-capita), never point-level charger data, and no charger map of our own.
- New table `charging_stats` (country, region?, period_end, metric, power_band, value, unit, source_id, definition_id, confidence, entered_by) plus taxonomies `charging_metrics`, `charging_definitions`, `power_bands`, and config `country_charging_links`. Variant field `abrp_typecode` (nullable).
- A chart draws exactly one `definition_id`; a definition change starts a new series with a marked break. Cross-country comparison uses EAFO (Europe) or IEA (world) only.
- One official primary per country; PDF-only sources are entered by staff in `data/manual/charging/*.yaml` with a source URL. Monthly job inside the night window; release diff flags month-on-month changes above 15 % or any drop.
- Phasing: link-outs + /learn "Charging in 2026" = Core 1; country pages + ABRP car deep link = Core 2; EAFO comparison and "how this car fits the network" = Next.

**Consequences:** A small separate fact table and five taxonomies; definitions need curation (WS3). Some countries will show fewer metrics than others, which is honest.

## Decision 013: Trip fit routing on a separate Valhalla box; scoring in the browser

**Status:** Accepted (WS0, 2026-11-15)
**Date:** 2026-11-15

**Context:** Spec tab "Trip fit" (docs/spec/trip-fit.md) needs routes split into road bands with climb per trip. The shared CAX31 is already ~1 GB over its worst-case budget in the job window (Decision 006). Free hosted routing plans (openrouteservice, GraphHopper) are non-commercial. Nominatim for Europe needs ~64 GB RAM.

**Decision:**
- Routing = self-hosted Valhalla (OpenStreetMap) on its own small Hetzner Arm box (~€5–15/month after a sizing test for NL+BE+LU+DE+FR+UK), not on the shared CAX31. Monthly tile rebuild.
- Hosted free routing APIs only for prototypes and staging.
- No Nominatim: town search from GeoNames cities (CC BY 4.0) plus a map pin.
- The server returns a route summary per trip (km per road band, climb, descent, starts); the browser multiplies it with a static per-variant consumption matrix (variants × 3 road bands × 5 temperature bands) published with each release. Re-ranking is instant and server load is one route call per trip edit.
- Privacy: addresses never reach the server; coordinates rounded to ~200 m before routing; no request logging on the route endpoint; accounts store trip names and summaries only; share links carry summaries, never places.
- Consumption model: per-road-band consumption × temperature curve per heater type + warm-up per cold start + climb; fallback ladder measured → platform → physics → WLTP ratio; P10–P90 band. Launch gate: back-test median error < 10 % on the top-40 used models.
- OSM-derived route data is ODbL: only per-trip summaries computed on the fly reach users; nothing OSM-derived enters the CC BY release.

**Consequences:** One more small server for WS4 to run and back up (tiles are rebuildable, so no backup of tiles). Quick check without routes (Core 1) can ship before the box exists.

## Decision 014: Workstreams coordinate through repo files; one owner per path

**Status:** Accepted (WS0, 2026-11-15)
**Date:** 2026-11-15

**Context:** The first build chat lost time to two chats editing the same decisions file and to Menno relaying messages by hand.

**Decision:** Up to six long-running workstreams (WS0 coordinator, WS1 pipeline, WS2 web, WS3 curation, WS4 infra, WS5 partnerships). Each has `workstreams/<ws>/START.md`, `STATUS.md` and an append-only `INBOX.md`. Every path has one owning workstream (table in workstreams/README.md and BOARD.md); others write to the owner's INBOX. Read right before writing; small edits. The spec is mirrored into `docs/spec/` and the repo copy wins for builders. Research and audit numbers (R-NN, A-NN) are handed out by WS0 to avoid clashes.

**Consequences:** Slightly more files, far fewer overwrites and no human relay. AGENTS.md's role table still holds; workstreams are the long-running chats that fill those roles.

---

## Decision 015: Schema conventions for bidi, charging stats and Trip fit (T-018, T-023, T-030)

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** Addendum 4 added 37 schema defs. A few conventions differ from the spec text and need to be shared.

**Decision:**
- Taxonomy ids use hyphens (`ac-onboard`, `iso15118-20`, `dc-150-349`), not underscores, because every id must match the `Id` pattern (Decision 010). Seed tasks T-019, T-024 and T-031 write ids this way.
- New entities use `CountryCode` (any two-letter code, `UK` not `GB`), so US/AU rows need no schema change. The five-value `Country` enum stays for existing launch-market fields.
- No separate `usable_kwh` fact: `battery_kwh_net` is usable capacity. New fact names carry units (`frontal_area_m2`, `kerb_mass_kg`, `wheel_size_in`).
- Allowed values for `iso15118_20_support`, `heat_pump` and `drag_coefficient` facts are checked at release time (WS1), not in the schema, because a conditional schema rule broke the generated TypeScript `Fact` type.
- `CountryChargingLink`, `ChargingStat`, `ConsumptionModel` and `ClimateNormal` are defined but not yet part of `Catalogue`; WS1 decides how they ship.

**Consequences:** All additions are optional, so release 1 still validates. Details in Q-054.

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
