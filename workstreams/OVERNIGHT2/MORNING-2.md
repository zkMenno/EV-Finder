# Overnight 2 — morning report

Branch `proto/overnight-2` · research + review lane (START.md). Last updated 2026-11-15 05:05 UTC.

**Headline.** All 12 queue items plus the three extras have a file. Research ran in parallel and used up this session's web-search budget (200 searches per turn, shared by every agent) within ~20 minutes, so R-21, R-22 and R-23 are partial: the gaps are marked 🔴 in each file and listed below for a follow-up run. A-20 delta pass at overnight 1's `d06535a`: **no blocker any more** (B1 fixed, all suites green); three new should-fixes (D1 RDW credit vs Q-037, D2 `ev release` on a fresh checkout still publishes a crippled release, D3 Known-issues plate sample likely misses 2008–2015 plates 🟡).

| Item | State | File | Key finding |
|---|---|---|---|
| R-20 Finance rates | done | [research/R-20-finance-rates.md](../../research/R-20-finance-rates.md) | 🟢 ECB MIR consumer-credit APRC, Sep 2026: DE 8.91 %, FR 6.11 %, BE 6.24 %; UK BoE IUMHPTL 7.11 % (Oct 2026). 🟡 NL has no current official series (proxy 7.29 %, legal cap 12 %). No source publishes term/deposit: defaults 48 months / 10 % 🟡. CCD2 applies from 20 Nov 2026 |
| R-21 Heat pump fitment | partial | [research/R-21-heat-pump-fitment.md](../../research/R-21-heat-pump-fitment.md) | 73-row CSV; ~20 models still `not_disclosed`. MEB = option 🟢; Model 3 standard from 2021 refresh; Leaf **has** a heat pump on many trims since 2013; VW delivered 2022–23 cars without the ordered heat pump |
| R-22 Variant clues | partial | [research/R-22-variant-clues-top20.md](../../research/R-22-variant-clues-top20.md) | 66 clue rows, 16 of 20 models; no FR/BE list. Q4 "45 e-tron" name trap: only kW on the papers tells old/new apart. 5 seed conflicts sent to WS3 |
| R-23 VIN + RDW plate | partial | [research/R-23-vin-and-plate-lookup.md](../../research/R-23-vin-and-plate-lookup.md) | 🟢 RDW m9d7-ebf2 → type-approval tables join works; RDW has **no battery kWh field**. CC0, but the bijsluiter says don't state the data comes from RDW (ties to Q-037). VIN gives battery only for a few US-market VINs (Leaf, EV6, Ioniq 5/Kona); EU VINs unknown 🔴. Design: plate lookup in the browser only, never on our server |
| R-24 ABRP deep links | done | [research/R-24-abrp-deep-links.md](../../research/R-24-abrp-deep-links.md) | 🟢 param is `car_model` (e.g. `kia:ev6:22:77`); free, no key; link text must say "ABRP". Key-less model list returned 401 today → need ABRP's list. contact@iternio.com |
| R-25 Bidirectional 🔴 items | done | [research/R-25-bidirectional-red-items.md](../../research/R-25-bidirectional-red-items.md) | 🟢 SAE J3400 does include V2G/backup power (R-01 wrong). 🟢 Ford Explorer V2H in DE/AT/CH; Kia EV2 V2G listed on Kia UK; BYD Dolphin V2G UK bundle only 🟡. ISO 15118-20 car-side: only VW (says -2) official; rest not disclosed |
| R-26 Charging licences | done | [research/R-26-charging-data-licences.md](../../research/R-26-charging-data-licences.md) | 🟢 BNetzA CC BY 4.0, DfT OGL v3, NDW CC0, AFDC free use. EAFO 🟡 → blocked until confirmed. BE + NZ no licence 🔴. NEVI/NSW/AFIR card-payment rules cited |
| R-27 Climate + towns | done | [research/R-27-climate-and-town-licences.md](../../research/R-27-climate-and-town-licences.md) | 🟢 Meteostat CC BY 4.0 (not NC); ERA5/ERA5-Land CC BY 4.0 since Jul 2025 → recommend as primary; GeoNames CC BY 4.0; GISCO + E-OBS non-commercial → skip |
| R-28 US + AU sources | done | [research/R-28-us-australia-sources.md](../../research/R-28-us-australia-sources.md) | 🟢 fueleconomy.gov public domain; BEV range is column `range`. WA registrations ODbL; CA CEC no commercial use 🔴; QLD/VIC CC BY 4.0; Green Vehicle Guide + EV Council not open 🔴 |
| A-20 Review overnight 1 | done (8b48bd7 + delta d06535a) | [audits/A-20-overnight-1-review.md](../../audits/A-20-overnight-1-review.md) | Mergeable as draft at d06535a: 1113 pipeline + 281 web tests green. Open: S1/S2/S3/S6/S7/S9 + D1–D3. Finance values match R-20 exactly; EPA uses `range` as R-28 found |
| Growth keywords | done | [docs/growth/keywords.md](../../docs/growth/keywords.md) | 🟡 relative demand only (Trends blocked). Build first: generation + used-price pages, "best used EV under €X", 4 learn articles per country |
| Outreach translations | done | [docs/outreach/drafts/](../../docs/outreach/drafts/) | `fastned.nl.md`, `ev-database.nl.md`, `marketplace-local.md` (DE/NL/FR). All `status: draft` |
| R-29 Competitors | done | [research/R-29-competitor-teardown.md](../../research/R-29-competitor-teardown.md) | 🟡 nobody combines old generations + used price per country + battery context. 🟢 none offer reusable open data |
| R-30 Normie test plan | done | [research/R-30-normie-test-plan.md](../../research/R-30-normie-test-plan.md) | 5 testers, 4 tasks, free video call, "stuck for 2+ → fix before launch" |
| R-31 Türkiye + Korea | done | [research/R-31-turkiye-korea-readiness.md](../../research/R-31-turkiye-korea-readiness.md) | Neither ready; Türkiye first. No open per-model data in either 🔴 |

## For WS0

**Questions for Menno (add to QUESTIONS.md, one popup each):**
1. **Free accounts for data access**: Copernicus CDS (ERA5-Land, likely needed), CEDA (MIDAS Open), NLR/AFDC API key, ABRP telemetry key (for the model list). All free. Recommended: yes to CDS and ABRP only, now; the rest later.
2. **Emails to send in your name** (drafts to be written by WS5): EAFO licence confirmation, RDW attribution question (pairs with Q-037), Green Vehicle Guide licence (Phase 4). Recommended: EAFO + RDW now.

**Decisions to log:**
- Plate lookup design: browser-side call to opendata.rdw.nl, allow-listed fields only, plate never sent to our server, logs, URLs or analytics (R-23 §5). Reversible, privacy-safe default.
- Washington DOL (ODbL): internal use only; any public use goes to a separate ODbL output later (R-28, Data rule 3).
- EAFO `blocked` until EAFO confirms in writing; Belgium charging counts wait (R-26).
- Climate: ERA5-Land daily 1991–2020 primary, Meteostat + national services second; GeoNames for towns (R-27).
- Finance: ECB MIR APRC series as the source for euro countries; NL proxy labelled 🟡; defaults 48 months / 10 % (R-20).

**Schema requests (WS0 owns packages/schema):**
- FinanceProfile: add `series_id`, `reference_period` (R-20 table).
- Bidirectional caveats: `bundle_only`, `ccs_hw_required`, `order_date_from` (R-25 §8).
- `consumption_epa_kwh_100km` separate from WLTP consumption; optional EPA city/highway range, 240 V full-charge time (R-28).
- Clue types: `dc_charge_kw`, `in_car_menu`, `vehicle_mass_kg` (R-22 §3).
- `abrp_typecode` + `replaced_by` on variant (R-24).

**Corrections to research/R-01 and spec docs (WS0-owned):**
- R-01: J3400 does cover bidirectional power; Tesla Model 3/Y V2H is for cars **ordered** from 1 Oct 2026 (US/PR); Ford Explorer V2H is confirmed (DE/AT/CH); "Volvo EX30 is -20 ready" isn't backed by Volvo's press release.
- docs/spec/data-sources.md: CEC 🟢 → 🔴 (no commercial use); Washington "Public" → ODbL; fueleconomy 🟡 → 🟢 public domain.
- docs/spec/charging-buildout.md: EAFO 29 Oct 2026 gives 1,176,554 EU27 public points (newer than 1,155,861).
- data/sources.yaml (WS1): fueleconomy should drop out of 0–100 fallbacks (no such field).

**Task updates:**
- Overnight 1 / its reviewer: B1 fixed at d06535a. Still open before going public: S1 + D1 (RDW named as source while Q-037 is open), D2 (guard `ev release` against missing staging), S3 (140 of 244 rows rest on hand-entered seed values: Menno's call whether they go in the CC BY bundle). Finance: keep NL blank (better than R-20's proxy); set ECB licence to 'free reuse with "Source: ECB statistics"' per R-20.
- New follow-up research run (fresh search budget): R-21 gap models, R-22 remaining 9 models + FR/BE lists, R-23 EU VIN rules and AP guidance. Could be an "R-21b/R-22b" item for the next research chat.
- T-029: needs ABRP's model list (account or ABRP's help) before import.

## Retro (5 lines)
- Worked: 11 research agents in parallel finished the whole queue in ~25 minutes, each with import tables.
- Didn't: the shared 200-searches-per-turn budget ran out mid-run, leaving three items partial. Next time, stagger agents and give each a search budget (e.g. 15).
- Some page fetches hit a permission prompt nobody answered at night; those pages are listed as blocked in each file.
- A-20 ran twice (02:00 and 05:00 UTC); the delta pass showed overnight 1 fixed the blocker on its own. Independent agreement on finance rates (R-20 vs overnight 1) is a nice cross-check.
- Rule proposal for the project instructions: "Overnight research: max ~6 parallel agents, ~15 searches each; list blocked URLs for a daytime retry."
