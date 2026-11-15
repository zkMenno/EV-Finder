# T-019 Taxonomy rows + seed data: bidirectional and ports
Role: builder (WS3 curation, WS1 for sources.yaml)   Lane: data/taxonomy, data/seed, data/sources.yaml   Wave: 5
Status: todo (blocked by T-018)

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

## Review
