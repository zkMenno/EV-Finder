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

## Decision 015: Language and country both in the URL path

**Status:** Accepted (WS0, 2026-11-15)
**Date:** 2026-11-15

**Context:** The SEO plan (docs/growth/seo-plan.md) needs one crawlable URL per country × language for hreflang across six languages and five launch countries. The prototype picks language from request headers, which also blocks static model pages (Q-033/Q-034).

**Decision:** URLs are `/{country}/{lang}/…` (e.g. `/nl/nl/`, `/be/fr/`, `/uk/en/`). Each country has a default language; `/{country}/` redirects to it. Headers only suggest a language on the first visit (a banner, not a redirect loop). Every page emits hreflang for all its country × language pairs plus `x-default`. The language choice is remembered but never overrides an explicit URL.

**Consequences:** Model pages can be static per country × language, which resolves Q-033/Q-034. Five countries × six languages = up to 30 variants per page; the sitemap lists only the pairs we serve (a country's own languages + English) until translations are reviewed.

## Decision 016: Open data release ships at launch

**Status:** Accepted (Menno, 2026-11-15)
**Date:** 2026-11-15

**Context:** The launch plan proposes the CC BY 4.0 dataset (catalogue + our real-range and charging figures) as the launch hook (Show HN, press, AI-search citations). It was tagged Next.

**Decision:** The open dataset is part of launch: each numbered release publishes a downloadable CC BY 4.0 bundle (CSV + JSON) with release number, date, licence and per-source attribution, only from sources that passed the licence gate (Decision 009). ODbL-derived values stay out.

**Consequences:** The licence gate and attribution file must be complete before launch; WS1 adds the bundle to the release job, WS2 a /data page.

## Decision 017: Prices in three modes (outright, loan, lease) from config tables

**Status:** Accepted (Menno's idea, WS0 defaults, 2026-11-15)
**Date:** 2026-11-15

**Context:** Many buyers lease or finance part of the price. Used leasing exists in NL, DE and FR. CCD2 (Directive (EU) 2023/2225) applies from 20 Nov 2026 to credit adverts with cost figures; in the UK, introducing consumers to finance or lease providers is FCA-regulated credit broking. Spec: master-spec-v2 §8 "Ways to pay".

**Decision:** A price mode (outright / loan per month / lease per month) on every price, remembered and in the URL. Loan = browser calculator from price, deposit, term and a typical rate from a new editable `finance_profiles` table (country, product, typical APR, default term and deposit, source, date). Calculator output is labelled an estimate, shows its assumptions, the total over the term and the CCD2 warning. Lease = partner-feed figures only, otherwise a plain labelled link. No finance commission at launch; no UK finance or lease links until the FCA question is answered.

**Consequences:** One small taxonomy (WS3), a price-mode control and calculator (WS2), a lawyer question in R-03. Lease figures stay Next until partner feeds exist.

## Decision 018: Working title "EV Shortlist"

**Status:** Accepted (Menno, 2026-11-15)
**Date:** 2026-11-15

**Context:** Name research in docs/brand/name-shortlist.md (rounds 1–2). evshortlist.com and evshortlist.nl were unregistered on 15 Nov 2026; .eu unchecked.

**Decision:** "EV Shortlist" is the working title in copy, drafts and the site's brand config. EV Field Guide stays the backup; other names and domains remain open. Repo name, package names and code ids stay `ev-finder` (no churn). The name lives only in config (`brand.name`), never hard-coded.

**Consequences:** Not final: no domain bought, no trademark filed, no logo finalised. Outreach still waits for the final name unless Menno says otherwise. Supersedes the "EV Finder" working name in AGENTS.md.
---

## Decision 019: Variant finder: grouped variants, differences only, clues in one data table

**Status:** Accepted (Menno, 2026-11-15)
**Date:** 2026-11-15

**Context:** One card per variant is right, but buyers can't see what differs between variants or match a used ad to the right one (EV Database pain). Silent mid-cycle changes (battery, charger, heat pump) are the costly traps.

**Decision:** Keep one card per variant. Add a "differences only" toggle and a variant change timeline (Core, no new data), a "spot it in an ad" clue box (Core for the 40 hand-checked models, Next for the rest), a "which one is it?" finder and NL plate lookup (Next), and listing-link paste (Later, marketplace terms). Clues are a new config-typed data table (Variant clue + Look-alike group) that also feeds listing matching (§8). Spec tab: docs/spec/variant-finder.md.

**Consequences:** Schema gains two entities (coordinator). WS3 writes clues for the top 40; WS1 owns clue data, look-alike detection and the RDW check; WS2 builds the toggle, timeline, box and later the finder; UX designs a colour-blind-safe diff highlight. No scraping of marketplaces.

## Decision 020: Schema conventions for bidi, charging stats and Trip fit (T-018, T-023, T-030)

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

## Decision 021: Data refresh runs from the CLI now; pg-boss schedules it once the database exists

**Status:** Proposed (provisional, overnight prototype 1, addendum 6 P1–P4)
**Date:** 2026-11-15

**Context:** The update loop is the heart of the product, but there is no database yet, so the pg-boss scheduling of Decisions 003/006 cannot run. Data still has to stay fresh, cheap and undoable.

**Decision:**
- One command, `ev refresh [--sources …] [--dry-run]`, runs every due source (cadence from `data/sources.yaml`): probe → fetch → snapshot → schema fingerprint → normalise → release → blocking QA. It is scheduled by GitHub Actions (`.github/workflows/data-refresh.yml`, weekly + manual) that opens a "Data release N" PR with only the release folder; on the server, the same command later becomes a pg-boss job (nightly window, 1 GB, Decision 006) without code changes.
- Raw fetches go to a content-addressed snapshot store (`$SNAPSHOT_DIR`, local now; S3-compatible behind the same interface, env vars only, not built yet). Unchanged sources (same hash, HTTP 304, same git commit) cost one probe and publish nothing.
- Per-source health (`data/releases/<n>/sources.json`): last success, last change, records vs previous, schema fingerprint. A breaking fingerprint change or a > 50 % record drop fails closed for that source (previous data kept, review item in `data/review/source-health.csv`) until `ev sources accept <id>`.
- `data/releases/latest` switches atomically (temp file + rename) and only after blocking QA passes; `ev release rollback --to <n>` and `ev release diff <a> <b>` undo and explain.

**Consequences:** No database or server needed for fresh data. The workflow's PRs don't start CI by themselves (GITHUB_TOKEN limit) and need the repo setting that lets Actions open PRs (Q-079). When pg-boss arrives, the job calls `ev refresh` and the snapshot backend switches to S3 by env var.

---

## Decision 022: Themes from design tokens, applied before paint without inline scripts

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** Addendum 5 asked for a light "Day trip" and a dark "Night drive" theme. The strict CSP (no inline scripts) rules out the usual inline "apply theme before paint" snippet.

**Decision:** Colours come from `docs/design/tokens.json` (UX chat), generated into `apps/web/src/app/tokens.generated.css` by `scripts/theme.mjs` (a test fails when it is stale). `globals.css` maps the Tailwind colours the app uses onto the tokens. The default follows `prefers-color-scheme`; a header toggle stores the choice in localStorage; a same-origin `/theme-init.js` applies it before paint. Print is always light.

**Consequences:** The UX chat changes colours in one file. axe runs on both themes in CI (0 findings tonight).

---

## Decision 023: NEDC, worst-case WLTP and mass in running order are their own fields

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** R-08 found that the best open source for 2010–2020 EVs is RDW's type-approval data (TGK, CC0), which gives NEDC range, WLTP best and worst bounds and mass in running order (incl. 75 kg driver). Mixing these into WLTP or kerb weight would make numbers look comparable when they aren't.

**Decision:** New FactFields `nedc_range_km`, `nedc_consumption_kwh_100km`, `wltp_range_km_worst`, `wltp_consumption_kwh_100km_worst`, `mass_running_order_kg`, `power_30min_kw`, and optional PublishedVariant columns `nedc_range_km`, `wltp_range_km_worst`, `mass_running_order_kg`. NEDC never fills WLTP; running-order mass never fills kerb weight; 30-minute power never fills peak power. `wltp_range_km` keeps meaning the best case or the single stated value.

**Consequences:** Older cars can show an honest NEDC figure labelled as such. Real range stays derived from WLTP only.

---

## Decision 024: Type-approval values attach only on unique evidence; versions of one source are spread, not conflicts

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** RDW type approvals (rdw-tgk) carry many versions per car. Placing them on our variants needs evidence, and versions of one source that disagree are not a cross-source conflict.

**Decision:**
- A type-approval version attaches to a variant only when exactly one variant fits the evidence (range number in the name, years ±1, battery window from range × consumption, trade-name words, WLTP within 2%). Ties and misfits go to review with a reason; nothing is guessed.
- All versions of a source in `SPREAD_SOURCES` (today rdw-tgk) on one variant count as one vote, cast by the earliest model year's version. Other values are noted as "same-source versions differ" in provenance, not written to conflicts.csv, and can't outvote other sources.
- RDW plate values and RDW type approvals share one origin for agreement counts (Q-087).

**Consequences:** Pre-2020 rows gain NEDC, worst-case WLTP and running-order mass where the evidence is unique. Remaining ties (Zoe Z.E. 40, Honda e, Model 3 LR vs Performance) need more seed evidence (Q-089).

## Decision 025: Agreeing sources outvote one priority value; nameless records need evidence; lone-source DC peaks go to review

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** Review A-05 found RDW model-year records (which blend all trims) landing on base trims and winning over other sources, RDW NEDC columns holding WLTP figures, and a DC peak on a Zoe that has no DC socket (Q-091).

**Decision:**
- A record without a variant name is not "base". It attaches only to a generation's only variant or on unique evidence; otherwise it goes to review.
- In priority fields, 2+ agreeing independent sources outvote a single priority value. Fields can opt out in `data/field_sources.yaml`. RDW stays first for WLTP and consumption.
- NEDC within 1 km of the same version's WLTP is dropped, and NEDC is dropped on 2018/858 approvals first registered after 2020 (inferred rule, logged in the run log).
- Only a source's own vote raises confidence.
- A DC peak that only KilowattApp gives goes to review until a second source or a charge-port field confirms it.

**Consequences:** EX30 base 475 → 341 km; 12 more rows reach "sourced"; 510 more records wait in review; 27 fewer rows show a DC peak until confirmed.

## Decision 026: Seed values can cite a source; git sources clone only from allow-listed GitHub URLs

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** Hand-entered seed values had no per-value source (A-05 F5), and two adapters cloned from GitHub outside the safe fetcher (A-05 L6). Q-092.

**Decision:**
- `data/seed/variants.yaml` takes an optional `cited:` block per value (value, https source URL, retrieval date, locator, confidence). Each cited value becomes its own fact with that source. New seed values should be cited; uncited ones stay "unchecked" (Q-015).
- When a type-approval version still ties, a candidate named after a longer trade name (e.g. "i3s") drops out if the version's own trade name lacks that word.
- Git sources clone only from `https://github.com/<owner>/<repo>` with github.com in that source's `hosts:`; anything else fails closed before git runs.

**Consequences:** BMW i3s gains a cited battery figure and six more RDW versions place correctly. Honda e, Zoe Z.E. 40 and Model 3 gen1 trims still tie: no official figure separates them.

## Decision 027: Battery gate: records that contradict the seed battery go to review

**Status:** Proposed (provisional, overnight prototype 1)
**Date:** 2026-11-15

**Context:** A Zoe Z.E. 22 record (23.3 kWh) landed on the Z.E. 40 R90, an OpenEV Q4 40 (48 kWh) merged into the 77 kWh "40 e-tron", and Mach-E SR records landed on ER AWD. Nothing compared batteries before placing a record.

**Decision:**
- Each seed variant's battery (net, gross, cited, kWh in its name) is an anchor. A record whose battery differs by more than 15% on the same basis, or 20% across net/gross or name figures, never joins that variant; it goes to review with the reason.
- In the attach pass, ruled-out candidates go first; whatever remains still needs its own positive evidence, so the gate can't push a record onto the next-nearest trim.
- If either side has no battery figure, the gate rules nothing out.

**Consequences:** Zoe R90 23.3 → 41 kWh, Q4 40 e-tron 48 → 77 kWh (and 150 kW), Mach-E ER AWD 68 → 88 kWh. About 10 more records wait in review.

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
