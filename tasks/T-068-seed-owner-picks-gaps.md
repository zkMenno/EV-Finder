# T-068 Seed the models in Menno's picks that the catalogue lacks
Role: builder   Lane: data/seed   Wave: 9
Status: doing (WS3, 2026-11-15)

## Goal
Every car in `data/editorial/menno-picks.yaml` maps to a seed generation.

## Acceptance criteria
- [ ] Add models/generations (sourced years, aliases): XPENG G6 (2024 v1.1 / 2025 v1.3 as change marker or generation), P7, P7+, L03, L05 (announced), Zeekr 001, 7X, 7GT, X, Volvo EX60, EX50, EC40/C40, Kia EV4, Hyundai IONIQ 3, VW ID.5, Polestar 4, MG IM6, MG5, MGS5, Marvel R, BYD Sealion 7, Renault 4, Peugeot e-308 (+SW), Opel Astra Electric (+ST), Nissan Ariya, Opel Ampera-e, DS3 E-Tense, Fiat 600e, Smart #3, Genesis GV60, Ford Capri, Leapmotor B05, Lynk & Co 02, Audi A2 e-tron (announced), Geely E5, Subaru Uncharted
- [ ] EV6 and IONIQ 5 2024 updates (84 kWh, V1.2) as distinct variants or a generation split (his tiers treat them as different cars); decide and log
- [ ] Check years where his sheet and the seed disagree: Skoda Elroq (2024 vs 2025), Renault Scenic E-Tech (2023 vs 2024)
- [ ] Fill `MODEL_MAP` in `data/editorial/import_menno_sheet.py`, re-run, no `seed_model_id: null` left for released makes
- [ ] validate_seed.py + validate_variants.py pass

## Inputs
Decision 038, research/R-32. EV Database car ids in the picks file help matching only; never copy its data.
