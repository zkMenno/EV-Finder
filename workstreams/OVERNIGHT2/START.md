# Overnight worker 2 — start here (from WS0, 2026-11-15 01:40 UTC)

You are **overnight worker 2** for EV Shortlist (working title; repo EV-Finder). Another overnight worker (overnight 1) is building code, schema and the data pipeline on `proto/overnight-1`. **Your job is research and review**: answer the open questions the builders need, with sources, so tomorrow's builders can go straight to work. About 7–9 hours; keep going until the session ends.

## 0. Setup (10 min)
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`), clone it, create branch `proto/overnight-2` from `main`.
2. Read: `AGENTS.md` (incl. "Web access": public websites are pre-approved) · `workstreams/README.md` · `DECISIONS.md` (skim 009–019) · `docs/spec/README.md` · the task files named in each item below.
3. Add your row to `CHATS.md` (OVERNIGHT2, purpose, your chat link) and commit.

## 1. Lane (no clashes with overnight 1)
You write ONLY: `research/R-20-*.md` … `research/R-39-*.md`, `audits/A-20-*.md` … `audits/A-29-*.md`, `docs/outreach/`, `docs/growth/`, `docs/brand/`, `workstreams/OVERNIGHT2/`, your row in `CHATS.md`.
You never edit: `packages/`, `apps/`, `pipeline/`, `data/`, `config/`, `content/`, `tasks/`, `BOARD.md`, `QUESTIONS.md`, `DECISIONS.md`, `docs/spec/`. Proposals for those go in `workstreams/OVERNIGHT2/MORNING-2.md` under "For WS0".

## 2. Rules
- Every fact cited: link you actually opened + date (2026-11-15). Mark 🟢 verified on an official page · 🟡 secondary or reasoned · 🔴 unsure. Never invent numbers; "not found" is a valid answer.
- Where a builder will import your findings, end the note with a **ready-to-import table** (columns named like the target YAML/schema fields) so they can copy it.
- Licence and terms first: for every data source, record licence, attribution text and any reuse limits.
- Plain language, short sections, lead paragraph = the answer. Sources at the end.
- Time-box each item; when an item stalls (3 dead ends or 30 min without progress), write what you found, mark the gaps 🔴, move on.
- Commit + push after each item; keep `workstreams/OVERNIGHT2/MORNING-2.md` current (item · done/partial · file · key finding).

## 3. Queue (in order)
1. **R-20 Finance rates per country (T-043, ≈45 min).** Typical used-car / consumer-loan APR for NL, DE, FR, BE, UK from central-bank or statistics sources (ECB MIR, DNB, Bundesbank, Banque de France, NBB, Bank of England), with series id and date; typical term and deposit if published. Plus a list of used-EV lease providers per country (NL private occasion lease, DE LeasingMarkt, FR Vivacar/Renault Renew, BE, UK) with whether they have partner/affiliate programmes. Import table: `finance_profiles`.
2. **R-21 Heat pump fitment for the top used EVs (T-031, ≈1.5 h).** For the ~40 most common used EVs in NL/DE/FR/BE/UK (use registration data or best-seller lists you can cite), whether a heat pump is standard / option / none / not disclosed per generation and model year, cited per row (maker docs, press releases, reputable tests). Import table: `variant_slug_hint, model_year_from, model_year_to, market, heat_pump, source_url, retrieved_at, confidence`.
3. **R-22 Variant clues for the top-20 used EVs (T-046 groundwork, ≈1.5 h).** Per generation: the silent mid-cycle changes (battery, onboard charger 7.4/11 kW, heat pump, chemistry, peak DC) with dates, and how a buyer spots each in an ad or on the papers. Import table matching `VariantClue` (docs/spec/variant-finder.md §4).
4. **R-23 VIN battery/motor encoding + NL plate lookup (T-049, ≈1 h).** Which makes encode battery or motor in the VIN for the top-20 models (cited per make; unknown stays unknown). RDW open data: licence, which datasets link plate → type approval/uitvoering, and Dutch DPA (AP) guidance on whether plate lookups are personal data; recommend a privacy-safe design.
5. **R-24 ABRP deep links (T-029, ≈30 min).** Exact deep-link parameters and the car-model/typecode format from ABRP's public docs; examples for 5 popular models; any terms on linking. Feed WS5's ABRP outreach draft.
6. **R-25 Bidirectional 🔴 items (T-042, ≈1 h).** Verify: Kia EV2 V2G, BYD Dolphin bidirectional bundle, Ford Explorer EV V2G, older Teslas at J3400 sites, bidirectional over NACS; plus car-side ISO 15118-20 support per maker (official statements only). Table per item: claim · status · source · date.
7. **R-26 Charging data licences and gaps (T-025, T-027, ≈1 h).** Exact licence text for EAFO, Bundesnetzagentur Ladesäulenregister, DfT EV charging statistics, AFDC; official public charger maps for NL, BE, NZ; card/contactless payment rules for public charging in the US (NEVI) and Australia. Import table: `data/sources.yaml` rows (id, licence, attribution, terms).
8. **R-27 Climate normals and town data licences (T-034, ≈30 min).** Meteostat licence per data source (confirm CC BY 4.0 vs NC), Copernicus ERA5 terms, GeoNames attribution; January mean and P10 temperature availability per launch country.
9. **R-28 US and Australia sources for Phase 4 (≈1 h).** EPA fueleconomy.gov fields for EVs, state registration open data (WA, CA, NY, TX), NHTSA vPIC/recalls; Australia: Green Vehicle Guide, state registrations, EV Council data; licence for each.
10. **A-20 Fresh-eyes review of overnight 1 (≈1 h, do it late, around 05:00–06:00 UTC).** `git fetch origin proto/overnight-1`; review against the task acceptance criteria and AGENTS.md data rules (provenance, licence gate, no invented data, tests without network, no secrets). List findings as blocker / should-fix / nice-to-have with file and line. Don't edit their branch.
11. **docs/growth/keywords.md (≈45 min).** Search-demand research for used-EV queries per country and language (e.g. "tweedehands elektrische auto", "gebrauchtes Elektroauto", "voiture électrique occasion", "used electric car"); use public tools only, mark estimates; map queries to our programmatic page types in docs/growth/seo-plan.md.
12. **Outreach translations (≈45 min).** Dutch, German and French versions of the drafts in `docs/outreach/drafts/` where the recipient's language fits (Fastned NL, NAF stays EN, Spritmonitor DE exists, marketplace variants per country). Keep `status: draft`; use "EV Shortlist (working title)".

## 4. If there is still time
- R-29 competitor teardown: EV Database, EVKX, ev-database.nl, AutoUncle, Recurrent: features, data sources, licence/terms, what used buyers miss.
- R-30 five-person "normie test" plan: tasks, script in NL/EN, what to measure, how to recruit for free.
- R-31 emerging-market readiness check for Türkiye and South Korea (registration data, marketplaces, licences).

## 5. Finish (always; also a light version every ~2 hours)
1. `MORNING-2.md`: table of items (done / partial / skipped, file, one-line finding), "For WS0" proposals (decisions, task updates, questions for Menno), 5-line retro.
2. Push `proto/overnight-2`, open a draft PR to `main` titled "Overnight 2: research pack".
3. Append to `workstreams/WS0/INBOX.md` **on your branch**: "Overnight 2 done, PR #x, MORNING-2.md ready."
