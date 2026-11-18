# R-41 Catalogue coverage: how many EU EV variants can open sources give us? (T-136)

Question: how many EV variants (trim × battery × motor, by model year) were sold in Europe since ~2011, and how many can we cover from open, licensed sources, before we build anything (staging feedback 2026-11-17 item 5)?

Retrieved 2026-11-17 by WS1 (6th session). Every count below was measured live with the scripts in [R-41-catalogue-coverage/](R-41-catalogue-coverage/), grouped server-side, no per-car rows stored. 🟢 measured, 🟡 reasoned, 🔴 unsure.

## Answer

- 🟢 **The EU sold about 9.1 million new battery-electric cars from 2010 to 2025** (EEA; 342 raw make spellings, 67 of them with ≥ 1,000 cars).
- 🟢 **Our 92 seed models already cover 86.7 % of them** (by make + model name, our own matcher). The gap is mostly **variants**, not models: we have 271 variant rows; the official registers show 570–700 power/type combinations for those same 92 models.
- 🟡 **Expected total: about 900–1,200 buyer-facing variants since 2011** (EEA make × type × power with ≥ 200 cars = 1,024; ≥ 50 cars = 1,480; de-duplication for reporting noise brings it down, see Method). That is the same order as EV Database's ~1,500 (Menno's figure; we did not open their site), which also lists cars never sold in the EU and pre-launch entries.
- 🟡 **Reachable from open sources: ~600 variants covering ~95 % of EU registrations within two build tasks**, then the long tail. The hard part is not the list of cars; it is **battery kWh**, which no official register carries.

## What the official data says (2010–2025, EEA, all EU + EEA reporting countries)

| Key (how a "car" is counted) | Keys | ≥ 10 cars | ≥ 50 | ≥ 200 | ≥ 1,000 |
|---|---|---|---|---|---|
| make + model name (raw spellings) | 4,030 | 1,996 | 1,213 | 797 | 466 |
| make + type (≈ platform / generation) | 2,323 | 741 | 483 | 341 | 219 |
| make + type + variant (Va) | 4,535 | 1,913 | 1,296 | 963 | 634 |
| make + type + variant + version (Ve) | 10,189 | 5,157 | 3,482 | 2,318 | 1,191 |
| make + type + power | – | – | 1,480 | 1,024 | – |

🟢 694 raw make + name spellings cover 99 % of all EU BEV registrations; the rest is grey imports, typos and one-offs.

RDW (NL, all BEVs first registered since 2010, 923,867 cars) shows the same shape: 1,319 make + trade names (300 with ≥ 200 cars), 4,699 type-approval × variant keys (1,063 with ≥ 200).

## Method and why the answer is a range

1. Pulled 16 EEA data years (final 2010–2024, provisional 2025) from Discodata, grouped by make, name, type, variant, version, power, WLTP range, consumption; 219,000 grouped rows, 9.11 M cars (9.08 M with a model name, the base for the coverage share).
2. Ran every (make, name) through the pipeline's own matcher against `data/seed/models.yaml` to measure what we already cover.
3. Calibrated the EEA keys against cars we know by hand:

| Model | Real buyer variants (🟡 our count) | EEA make+type+power ≥ 200 cars | EEA type+variant ≥ 200 |
|---|---|---|---|
| Peugeot e-208 | 3 | 4 | 1 |
| Renault Zoe | ~8 | 8 | 16 |
| VW ID.3 | ~8–10 | 10 | 14 |
| Dacia Spring | 4 | 4 | 1 |
| Tesla Model 3 | ~10–12 | 28 | 39 |

🟢 EEA's power field is reported inconsistently between countries (e-208: 57 kW 30-minute power next to 100 kW peak; Tesla reports many values per car), and makers use variant codes very differently (Peugeot one code for all e-208s, Tesla 39). So no single EEA key equals a buyer variant. For most makes make+type+power is close (1.0–1.3×); Tesla and a few others are ~2.5×. Hence 1,024 → **~900–1,200** after de-duplication. 🟡

## Per source: licence, years, fields, granularity, what it adds

| Source | Licence (status in data/sources.yaml) | Years | Granularity | Fields that matter | Adds |
|---|---|---|---|---|---|
| **EEA CO2 cars** (Reg. 2019/631) | CC BY 4.0 (active) 🟢 | 2010–2025 | type approval (type/variant/version) × country × year | make, name, type codes, power, mass, WLTP range (from 2020, 97 % filled from 2023), consumption, registrations | **The master list**: every model and type sold in the EU, per year and country. Today we use it for counts only. Gaps: no battery kWh, no DC/AC charging, power field unreliable, no range before 2020. |
| **RDW** gekentekende voertuigen + **TGK** type-approval register | CC0 (active) 🟢 | 2010– | type approval × variant × version, NL cars only | trade names per version, WLTP range/consumption bounds, 30-min power, mass, dimensions, seats, NL catalogue price | **Best per-version specs**, already ingested (8,516 TGK records). 🟡 NL is a big early EV market, so most EU models appear. Gaps: no battery kWh, no charging. |
| **Traficom** (FI) open vehicle data | CC BY 4.0 🟢 (not yet in sources.yaml) | fleet in use | per vehicle in use, ~5.3 M rows (all vehicle classes), 202 MB zip | "registration, approval and technical information" (publisher); 🔴 exact EV fields not checked yet | 🟡 Second register to corroborate RDW/EEA and fill pre-2015 cars (Nordic early EVs). Needs a field check before a task. |
| **OpenEV Data** (open-ev-data) | CDLA-Permissive-2.0 (active) 🟢 | 2023–2025 only (149 / 195 / 251 vehicle files) | model × model year × variant; 260 models, 1,189 vehicle files | **battery kWh**, charging, prices | Battery and charging for recent cars. Nothing before 2023. |
| **KilowattApp Open EV Data** | MIT with attribution (active) 🟢 | release years 2010–2025 (90 % 2019+) | 1,321 vehicles (1,282 cars) | **usable/gross battery**, AC/DC kW, consumption, curves | Battery for older cars. 🔴 **22 rows cite ev-database.org as their URL**: those values may be copied from EV Database. Propose: exclude rows whose `url` is ev-database.org, and check provenance with the maintainer. |
| **ADEME Car Labelling** (FR) | Licence Ouverte 2.0 (active) 🟢 | on sale now only (134 BEV versions) | version | WLTP min/max, consumption, FR list price | Current versions and best/worst WLTP. No history. |
| **KBA FZ10** (DE) | dl-de/by-2-0 (active) 🟢 | 2018– | make × model series | registrations only | Popularity in DE. No variants. KBA type-key tables stay blocked (Decision 068). |
| **Wikidata** | CC0 (active, corroboration only) 🟢 | all | model / generation | production years | Generation boundaries check. Never sets a value. |
| **fueleconomy.gov** | US public domain (active) 🟢 | 2011– | US variant × model year | EPA range/consumption | Cross-check for cars sold in both markets. US-only figures. |
| **Maker documents** | single cited facts (Decision 068) 🟢 | any | one figure per document | battery kWh, WLTP, price | Fills battery kWh where open data has none, one cited fact at a time. Slow, manual. |
| Norway (Statens vegvesen) | per-plate API with key; no licence stated 🔴 | – | per plate | technical data | Skip: no bulk, no licence. |
| EV Database, marketplaces | none | – | – | – | Never scraped (task rule, Decision 004). |

## What each source adds to the count

| Step | Variants (🟡) | EU registrations covered |
|---|---|---|
| Today (release 2) | 271 | 86.7 % at model level 🟢 |
| + split our 92 models by RDW TGK / EEA versions | ~450–550 | 86.7 % (same models, every version) |
| + ~40 missing models (list below) | ~600 | ~95 % |
| + long tail (EEA ≥ 50 cars, makes like Aiways, Fisker, NIO, Maxus) | ~900–1,200 | ~99 % |

🟢 Biggest gaps by EU registrations (make in seed, model not matched): VW e-up! (96k), Renault Twingo Electric (89k), Citroën ë-C3 (46k), Tesla Model X (29k), Smart #1 (25k), BMW iX2 (27k incl. xDrive30), Leapmotor T03 (20k), Peugeot e-3008 (20k), Škoda Citigo-e (18k), Mercedes EQE (~59k across names), Kia EV9 (17k), BYD Dolphin Surf / Seal / Dolphin / Seal U / Atto 2 (~60k), Mercedes EQV (16k), Mini Countryman E/SE and Aceman (~42k), XPeng G9 (12k), Citroën C-Zero and Peugeot iOn (22k), Volvo EX90 (11k), Peugeot e-5008 (10k), Opel Frontera (9k), Citroën ë-C3 Aircross / ë-Berlingo, Audi e-tron GT, Peugeot e-Rifter, Fiat Panda. Makes missing entirely: Mazda (MX-30, 41k), Jeep (Avenger, 35k), SEAT (21k; 🟡 probably Cupra Born filed under SEAT: an alias fix, not a new model), Lexus, NIO, Alpine, Abarth, Alfa Romeo, GWM/ORA, Aiways, Maxus, Mitsubishi, Fisker, Lotus.

## Proposal for build tasks (WS0 approves scope and licence first)

All five stay inside launch-scope rules: no new sources without a licence row, no scraping, every value a Fact.

1. **Variant split from type approvals (WS1)**: cluster RDW TGK versions (+ EEA type/variant) per seed model by power, WLTP range band and mass into candidate variants; write them to the review queue, never straight into the release. Needs Q-039's answer (per-type-approval spec rows) and an `estimate`-free rule set. Target: our 92 models at ~450–550 variants.
2. **Missing-model seed (WS3)**: the ~40 models above as seed models/generations with EEA + RDW aliases (SEAT → Cupra check first). Target ~95 % of EU registrations.
3. **Battery kWh coverage (WS1 + WS3)**: Kilowatt + OpenEV for battery, minus Kilowatt rows citing ev-database.org (🔴 licence check with the maintainer, WS5 for the email); maker documents per Decision 068 for the rest. Without battery kWh a variant cannot show range per kWh, consumption or charging time, so this gates how many rows are useful.
4. **Traficom FI adapter (WS1)**: add `traficom` to sources.yaml (CC BY 4.0, credit "Finnish Transport and Communications Agency Traficom"), field check, then corroboration of versions and pre-2015 cars.
5. **Long tail (later, after launch)**: EEA keys with ≥ 50 EU cars not yet in the seed, generated as review-queue candidates.

Not proposed: Norway's plate API (no licence), KBA type keys (blocked), anything from EV Database.

## Risks

- 🔴 KilowattApp provenance: 22 of 1,321 rows link ev-database.org; others may be copied without a link. EU database right applies to substantial extraction. Check before task 3 relies on it.
- 🟡 EEA power and variant codes are not comparable across makes; any automatic split needs a human review queue (AI proposes, rules decide).
- 🟡 Battery kWh is the bottleneck: no official register in this list carries it.
- 🟡 EV Database's 1,500 is Menno's figure; we did not verify it and will not open their catalogue.

## Sources

- EEA, Monitoring of CO2 emissions from passenger cars (Regulation (EU) 2019/631), Discodata SQL `[CO2Emission].[latest].[co2cars]` (2010–2019, Status F, Version_file v2…v20) and `co2cars_2020Fv22` … `co2cars_2024Fv30`, `co2cars_2025Pv31`, CC BY 4.0, https://discodata.eea.europa.eu (retrieved 2026-11-17).
- RDW Open Data, Gekentekende voertuigen `m9d7-ebf2`, CC0, https://opendata.rdw.nl/resource/m9d7-ebf2.json (grouped, retrieved 2026-11-17).
- Traficom, Open data for vehicles, CC BY 4.0, https://tieto.traficom.fi/en/open-data and https://avoindata.suomi.fi/data/en/dataset/ajoneuvojen-avoin-data (retrieved 2026-11-17).
- Statens vegvesen, Kjøretøyopplysninger API, https://data.norge.no/en/datasets/a8533876-cca7-4417-90be-b368f7d9542c (rights for use: not provided; retrieved 2026-11-17).
- open-ev-data/open-ev-data-dataset, CDLA-Permissive-2.0, https://github.com/open-ev-data/open-ev-data-dataset (shallow clone 2026-11-17).
- KilowattApp/open-ev-data, MIT with attribution, https://github.com/KilowattApp/open-ev-data (shallow clone 2026-11-17, `data/v2/models/*.json`).
- Licences of the other sources: `data/sources.yaml` on main.
