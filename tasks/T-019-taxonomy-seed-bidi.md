# T-019 Taxonomy rows + seed data: bidirectional and ports
Role: builder (WS3 curation, WS1 for sources.yaml)   Lane: data/taxonomy, data/seed, data/sources.yaml   Wave: 5
Status: merged (PR #1); fresh review via QA A-35; earlier note: partial — taxonomies only; overnight builder 2026-11-15. BidiCapability / ChargingPort seed still todo for WS3

## Goal
Fill the new taxonomies and seed BidiCapability + ChargingPort for the top-40 used models and every 2025–26 model that offers V2H/V2G.

## Acceptance criteria
- [ ] Taxonomy files for every table in spec §3.1, EN + NL strings minimum, 6 languages before launch; validate_taxonomy.py extended
- [ ] bidi_equipment rows at least: Mobilize PowerBox Verso, BMW Wallbox Professional, Hager/E3DC S10 E Compact, Elli/TMH ChargeLine BiDi, Sun2Wheel Two-Way-20, Wallbox Quasar 1/2, E3/DC Edison V2H, Ford Charge Station Pro, GM PowerShift + V2H kit, Tesla Powerwall 3, dcbel Ara (price band, markets, source)
- [ ] Seed rows (R-01 §4) for: VW group MEB (77 kWh + SW ≥3.5 conditions, discharge cap), Renault 5/4/A290, BMW iX3, Mercedes GLC/C EQ/CLA, Nissan Leaf gen 1–2 (CHAdeMO legacy) and gen 3, Mitsubishi Outlander PHEV only if PHEVs are in scope (else skip), Hyundai/Kia E-GMP (V2L live, V2H/V2G not offered in EU), Kia EV9/Ioniq 9 (NL pilot, US V2H), Tesla (EU not offered; US Cybertruck + 3/Y built ≥2026-10-01 with Powerwall 3), Volvo EX90, Polestar 3, Ford, GM
- [ ] Every row: 2 sources where possible (maker page first), retrieval date, confidence; 🔴 items in R-01 stay low confidence or out until verified
- [ ] EU ChargingPort for the top-40 (CCS2/Type 2/CHAdeMO/tesla_eu_legacy)
- [ ] sources.yaml: maker eligibility pages + The Mobility House list + E.ON/Octopus/Elli/Vattenfall pages, licence/terms noted (facts only, no copying tables)

## Inputs
docs/spec/bidirectional-and-connectors.md, research/R-01-bidirectional-and-connectors.md

## Out of scope
US ChargingPort per model year (T-022, phase 4).

## Handoff notes
Overnight builder, 2026-11-15, **coordinator half only (taxonomies)**. No git commands run.

**Done.** `data/taxonomy/bidi_modes.yaml` (4: v2l, v2h, v2g, v2b), `bidi_routes.yaml` (4: ac-onboard, dc-offboard, chademo-dc, proprietary), `bidi_protocols.yaml` (5), `bidi_caveats.yaml` (12, the §2.2 list with `{param}` + `param_kind`, severity), `bidi_status.yaml` (6, with `filter_group`), `connector_types.yaml` (9: type2, ccs2, chademo, tesla-eu-legacy, type1-j1772, ccs1, nacs-j3400, gbt-ac, gbt-dc), `bidi_equipment.yaml` (12: every box named above). Ids hyphenated per Decision 020. EN + NL label and short on every row (other languages absent, fall back to EN). Plug standard names are general knowledge; check before Nerd mode shows them.

**bidi_equipment = low confidence, R-01 only.** No maker page opened. `max_kw` is `not-disclosed` everywhere (R-01 gives kW for the car route, not the box). Prices only where R-01 gives euros: BMW Wallbox Professional €2,095; Elli ChargeLine BiDi €1,990–2,990 (intro/list). Quasar 2 (~£6,100) and dcbel Ara (US$9,999) not converted: `price_band: not-disclosed`, price in `notes`. Markets only where R-01 names them. Route for GM PowerShift and Tesla Powerwall 3 not in R-01, so `proprietary` with a note. Sources sit in `data/taxonomy/taxonomy_sources.yaml`; none is releasable in `data/sources.yaml`, so the release holds all 12 rows back (logged in the run log as `taxonomy_rows_held_back`) until WS1 registers them (Q-008, Q-057).

**Not done (WS3 / WS1):** per-car `BidiCapability` seed rows (R-01 §4 list), EU `ChargingPort` for the top-40, `data/sources.yaml` entries for maker eligibility pages, The Mobility House, E.ON / Octopus / Elli / Vattenfall, and the remaining four languages. The release already validates and ships the taxonomy tables, so the seed can reference these ids directly.

**Checks:** see T-024 handoff (validator 0 errors, self-test 22/22, pipeline 457 tests green, gz catalogue 153 KB).

## Review
