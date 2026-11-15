# R-22 Variant clues for the top-20 used EVs (NL / DE / FR / BE / UK)

Researched 2026-11-15 for WS3 (feeds T-046, schema T-044, spec `docs/spec/variant-finder.md`). Time-boxed (~1.5 h). Partial: the web-search budget ran out mid-task, and several pages were blocked (listed in §5).
Legend: 🟢 maker source or 2+ independent sources · 🟡 one reputable outlet or forum, or reasoned from a source · 🔴 unknown or unverified. Nothing here is invented. Unknown stays 🔴.

Data rules: every row in §4 carries `source_url` + `retrieved_at` + `confidence`. ev-database.org pages showed up in search results but are **not** used as sources (competitor, Data rule 2).

---

## 1. Which top-20 list (and its limits)

No single public "top used EVs in NL/DE/FR/BE/UK" list exists. Below is the union of three cited national lists, merged in order of how often each model appears.

| Market | List used | Metric | Models (rank order) |
|---|---|---|---|
| DE 🟢 | AutoScout24 "Jahresrückblick 2025" (autoscout24.de/unternehmen/daten/jahresrueckblick-2025-elektro-gebrauchtwagenmarkt-waechst/) | purchase enquiries on AutoScout24, 2025 | Model 3, Zoe, Q4 e-tron, ID.3, Model Y, smart fortwo, ID.4, Audi e-tron, Porsche Taycan, Kona |
| NL 🟡 | TopGear NL, 7 Jan 2026 (topgear.nl/autonieuws/populairste-gebruikte-ev-van-2025-is-toevallig-ook-een-exportfavoriet/); data provider not named | used units sold in NL, 2025 | Model 3 (11,338), ID.3, Audi e-tron, Kia Niro, Model Y, Kona, Peugeot 208, Volvo XC40, Enyaq, Zoe |
| UK 🟡 | cinch sales data Q1 2025 (cinch.co.uk/news/used-ev-sales-up-39-percent) | sales on one retailer, Jan–Mar 2025 | Model 3, Leaf, MINI (Cooper SE), Kona Electric, Corsa-e, e-Niro, Zoe, ID.3, I-PACE, Mokka-e |
| FR 🔴 | Automobile Propre "modèles les plus vendus en occasion en 2025" (blocked, see §5) | n/a | not read |
| BE 🔴 | none found within the time box | n/a | n/a |

**Working top-20:** Tesla Model 3, Tesla Model Y, Renault Zoe, VW ID.3, VW ID.4, Audi Q4 e-tron, Audi e-tron (GE), Hyundai Kona Electric, Kia (e-)Niro EV, Peugeot e-208, Opel/Vauxhall Corsa-e, Volvo XC40 Recharge, Škoda Enyaq, Nissan Leaf, MINI Cooper SE, smart EQ fortwo, Porsche Taycan, Jaguar I-PACE, Opel Mokka-e, Hyundai Ioniq 5 (Ioniq 5 is from cinch's "fastest-selling" list, not its volume list).
**Also researched (from the brief's list):** BMW i3, Hyundai Ioniq Electric, MG ZS EV, MG4.
**Not researched yet 🔴:** Taycan, I-PACE, Mokka-e, MINI Cooper SE, smart EQ fortwo, Corsa-e (beyond its e-208 sibling), Polestar 2, Kia EV6, Fiat 500e, VW e-Golf, VW e-up!. The search budget ran out before these.

---

## 2. Silent changes per generation, and how a buyer spots each one

Each change comes with a "spot it" line: where a buyer can see it (ad, papers, car, VIN, menu).

### Tesla Model 3 (gen1, `tesla-model-3-gen1`)
- **HW2.5 → HW3 (FSD computer), about 12 Apr 2019** 🟡. A TMC forum thread quotes reports of HW3 in "all new Model 3 vehicles … starting around April 12th". Posters note the cutover "may not have been clean", and that "for Europe there are different parts". *Spot it:* the hardware cover behind the glovebox: check the serial-number prefix against the parts catalogue. Build date is a **weak** clue near the cutover. Source: teslamotorsclub.com/tmc/threads/definite-guide-find-out-if-you-have-hw3-0-or-hw2-5.154750/
- **"2021 refresh", announced 16 Oct 2020** 🟡. New heat pump system, chrome delete, double-pane windows, powered trunk, new 18"/19"/20" wheels (Electrek). *Spot it:* black window trim instead of chrome is a **strong** visual proxy for a heat-pump car. Wheel design is supporting. The EU build cutover date is 🔴: Fremont and Shanghai timing was not verified. Source: electrek.co/2020/10/16/tesla-launches-model-3-2021-refresh-range-features/
- **Shanghai SR+ with LFP cells shipped to Europe from late Oct 2020** 🟡. Electrive says the export cars are "exclusively the Standard Range Plus" with LFP cells, but the battery type comes from community data, not from Tesla. ⚠ **This conflicts with the seed**: `tesla-model-3-gen1-sr-plus-lfp` notes say "LFP from late 2021". WS3 must recheck before publishing. *Spot it:* VIN position 11 = `C` (Shanghai) on an SR+ is a **strong** clue. Source: electrive.com/2020/10/19/tesla-starts-exporting-chinese-model-3-units/
- **VIN positions (Model 3/Y)** 🟡. Position 11 = plant (F Fremont, A Austin, B Berlin, C Shanghai). Position 8 = motor/drive unit (Model 3: A/B/C, Model Y: D/E/F), *not* battery. Position 7 = fuel type, with `F` = "Electric – Lithium Iron Phosphate" **from model year 2024**. Position 10 = model year (N 2022, P 2023, R 2024). How LFP was coded before MY2024 is 🔴. Sources: insideevs.com/news/561819/identify-tesla-origin-vin-decoder/ ; teslatap.com/vin-decoder/ (year letters L=2020 … T=2026, "model year, not manufacturing year").
- **Highland (HW4), 2023+**: 🔴, no source read in time.

### Tesla Model Y (gen1, `tesla-model-y-gen1`)
- **Berlin vs Shanghai build** 🟡. Berlin cars had different front seats, audio and suspension, and no 4680 cells (InsideEVs, 7 Jul 2022). *Spot it:* VIN position 11 `B` vs `C` is **decisive for the plant**, but only a **weak** clue for the spec. Source: insideevs.com/news/596857/tesla-model-y-berlin-vs-shanghai-compared/
- **Berlin RWD with BYD LFP structural pack, volume production reported May 2023** 🟡. 55 kWh usable (BYD) vs 60 kWh (CATL, Shanghai). WLTP 440 vs 455 km. Kerb weight 2,087 vs 2,153 kg. ⚠ The seed `tesla-model-y-gen1-rwd` has a single 57.5 kWh value; this is really two packs. *Spot it:* plant `B` + RWD → BYD pack (**strong**). Mass on the papers (2,087 vs 2,153 kg) is a candidate clue, but the documents' mass definitions may differ (🟡). Source: autoevolution.com/news/tesla-adds-a-new-model-y-variant-at-giga-berlin-with-byd-structural-battery-packs-214520.html
- **HW3 → HW4 at Giga Berlin, about mid-May 2024** 🟢 for the visual cue. "There will likely still be a few Model Ys built with HW3" during the transition. *Spot it:* HW4 camera lenses "have a red tint" (two sources), **strong** in photos. Fremont switched in about May 2023 (around VIN F789400). Shanghai timing is 🔴. Sources: driveteslacanada.ca/model-y/tesla-phases-out-hw3-as-giga-berlin-starts-model-y-production-with-hw4/ ; cleantechnica.com/2023/05/30/tesla-quietly-introduces-hardware-4-suite-on-new-model-y-cars/

### Renault Zoe
- **Ph2 Z.E. 50 (revealed Jun 2019)** 🟡. 52 kWh, new R135 motor (100 kW) on GT Line, R110 carried over, 22 kW AC kept. The car "can also feature a CCS inlet" for up to 50 kW DC. Whether CCS was standard or optional is 🔴. *Spot it:* a CCS socket under the front flap → Ph2 (**decisive** that it is Ph2; reasoned, because CCS is presented as new on the ZE50). 135 hp / 100 kW on the papers → R135 (**decisive** within Ph2). Source: zapmap.com/news/renault-reveals-new-zoe-z-e-50
- **Ph1 Q-motor vs R-motor (AC 43 vs 22 kW), battery rental vs owned**: 🔴, no source text read. The seed has the variants, but they are unchecked.

### Volkswagen ID.3 (gen1)
- **58 kWh Pro: DC 100 → 120 kW; 45 kWh Pure: 50 kW standard, 110 kW optional (configurator, May 2021)** 🟡. No production week is given. Source: insideevs.de/news/509225/vw-id3-ladeleistung-konfigurator/
- **77 kWh: DC 125 → 135 kW with software 3.0 (Mar 2022)** 🟢. New cars came with 3.0 from the factory, and older cars got it over the air from Q2 2022. *Spot it:* only a **weak** clue (an update, not hardware). Ask the seller for the software version. Sources: electrek.co/2022/03/21/volkswagen-announces-generation-3-0-software-update-for-id-evs-including-assisted-driving-and-charging-improvements/ ; insideevs.de/news/554811/volkswagen-id-modelle-mehr-ladeleistung/
- **Facelift (from 1 Mar 2023)** 🟡. 12" screen standard (was 10"), body-colour bonnet with no black strip under the windscreen, redesigned bumper intakes, software 3.5. Heat pump still optional (about €1,000). Pro S 77 kWh up to 170 kW DC, Pro 58 kWh up to 120 kW (VW newsroom). *Spot it:* bonnet and bumper in photos (**decisive** pre/post facelift). Heat pump: ask the seller or check the option list. Sources: electrive.net/2023/09/26/vw-id-3-im-test-was-hat-die-modellpflege-gebracht/ ; volkswagen-newsroom.com/en/the-new-id3-valuable-likeable-digital-15490/drive-battery-and-charging-15493

### Volkswagen ID.4 (gen1)
- **77 kWh: DC 125 → 135 kW (software 3.0, 2022). ID.4 Pure stays at 110 kW** 🟢. Same sources as ID.3. The 2023/24 upgrade (new drive motor and infotainment) is 🔴: only the press-release title was seen (volkswagen-newsroom.com/en/press-releases/upgrade-for-the-id4-and-id5-…-17728), not read.

### Audi Q4 e-tron (gen1)
- **Big name trap. MY24 update, orders from 26 Sep 2023** 🟢. Before: **35** (52 kWh, dropped autumn 2022), **40** (RWD 150 kW), **45 quattro** (190 kW, dropped), **50 quattro** (220 kW). After: **45** (RWD *or* quattro, 210 kW) and **55 quattro** (250 kW), all 77 kWh net / 82 gross. DC 175 kW (quattro) or 135 kW (RWD). New rear PSM motor. *Spot it:* a "45 e-tron" in an ad can be the old 190 kW quattro or a new 210 kW RWD/quattro. **kW on the papers is decisive** (150 / 190 / 220 old vs 210 / 250 new). Sources: audi-mediacenter.com/en/press-releases/update-for-the-audi-q4-e-tron-more-range-more-efficiency-more-emotions-15594 ; electrive.com/2023/09/21/audi-fits-q4-e-tron-with-new-electric-motor/
  - ⚠ The seed has no post-update variants. Proposed new ids: `audi-q4-e-tron-gen1-45-my24`, `audi-q4-e-tron-gen1-45-quattro-my24`, `audi-q4-e-tron-gen1-55-quattro-my24`, and the pre-update `audi-q4-e-tron-gen1-45-quattro`.

### Audi e-tron (GE) 55
- **Usable battery 83.6 → 86.5 kWh (gross 95)** 🟢. Built in the factory from late 2019 / early 2020 (with +25 km WLTP, to 436 km). Cars built **mid-Sep 2018 to end of Nov 2019 (MY2019/20, about 34,000 cars)** can get it as a free **workshop-only** update. *Spot it:* first registration before about Dec 2019 → ask whether the update was done (**strong** for "early car"; the result depends on the update). Sources: audi-mediacenter.com/en/press-releases/better-efficiency-and-longer-range-technical-update-for-the-audi-e-tron-12382 ; electrive.com/2021/10/28/audi-releases-range-update-for-older-e-tron-models

### Hyundai Kona Electric (OS)
- **On-board charger 7.2 kW single-phase → 11 kW three-phase, MY2020, deliveries in "many European markets" from end of 2019** 🟢. Which battery and which countries is not stated. *Spot it:* first registration from about 2020 is a **strong** (not decisive) clue. The ad's "11 kW" line or the charger sticker is decisive. Sources: electrive.net/2019/05/09/hyundai-kona-elektro-erhaelt-dreiphasigen-ac-lader-11-kw/ ; insideevs.com/news/348727/hyundai-3-phase-charger-kona-europe/
- 2021 facelift and battery recall: 🔴 not read.

### Kia e-Niro (DE)
- **UK, June 2020:** 11 kW three-phase only on the **4+** trim (64 kWh). Trims **2** and **3** stay at 7 kW. 39 kWh new to the UK on trim **2**. All versions 100 kW DC 🟢 (two UK sources). *Spot it (GB only):* trim name decides the AC charger. Trim "2" → 39 kWh. Other markets 🔴. Sources: zapmap.com/news/kia-adds-e-niro-39-kwh-and-faster-charging-to-range ; greencarguide.co.uk/2020/06/kia-e-niro-gains-new-battery-and-new-trim-levels/
- Heat pump by trim: 🔴.

### Peugeot e-208 (P21), and Corsa-e by extension 🔴
- **2023 powertrain: 115 kW motor, 51 kWh gross / 48.1 net, WLTP up to 400 km (was 362)** 🟢 (Stellantis release, 27 Sep 2022). AC 7.4 kW single-phase standard, 11 kW three-phase optional. **Heat pump introduced in the 2021 "optimisation"**. *Spot it:* 115 kW on the papers (P.2 / RDW) → new powertrain (**decisive**). First registration from 2021 is only **weak** for the heat pump (it was an option or trim feature, 🔴). The 11 kW charger is optional on both versions: check the ad or sticker. Source: media.stellantis.com/em-en/peugeot/press/new-100-electric-peugeot-e-208-more-powerful-more-efficient-and-up-to-400-km-in-range
- Corsa-e: same e-CMP platform, so likely the same change (🟡 reasoned). Dates not verified 🔴.

### Volvo XC40 Recharge
- **Announced 16 Jan 2023:** single motor switched from FWD to **RWD**. 69 kWh kept. New 82 kWh "extended range" RWD. 82 kWh DC 150 → 200 kW. Twin AWD +62 km WLTP 🟡. US/AU coverage labels this MY2024. *Spot it:* "RWD" or "Extended Range" in the trim name. kW on the papers is 🔴 (not read). Source: insideevs.com/news/631329/volvo-xc40-c40-recharge-go-rwd-get-range-charging-boost/

### Škoda Enyaq (gen1)
- **MY24 (production from early Nov 2023):** 80 → **85** (rear motor 150 → **210 kW**), 80x → **85x**. 85x and vRS DC 175 kW (+40 kW). MY23 table: 80 = 135 kW, 60 = 120 kW DC. 60 = 58 kWh net, 85/85x/vRS = 77 kWh 🟢 (two Škoda sources). *Spot it:* 150 vs 210 kW on the papers is **decisive** for 80 vs 85. ⚠ The seed `skoda-enyaq-gen1-80` has dc_peak 125 kW, but Škoda UK says 135 kW (MY23). Sources: skoda-storyboard.com/en/emobility/the-improved-enyaq-is-here-with-more-power-and-longer-range/ ; skoda.co.uk/news/details/enhanced-enyaq-delivers-faster-charging-more-equipment-and-more-range

### Nissan Leaf
- **ZE0 30 kWh, on sale Dec 2015, UK Acenta and Tekna only. Visia stays 24 kWh** 🟡. *Spot it (GB):* Visia → 24 kWh (**decisive** in GB). Acenta/Tekna → ask. Source: whatcar.com/news/2016-nissan-leaf-gets-increased-155-mile-range-new-battery/
- **ZE1 e+ (62 kWh), orders Jan 2019, deliveries summer 2019. 160 kW motor, CHAdeMO 100 kW peak, launch edition "3.ZERO e+"** 🟡. *Spot it:* 160 kW on the papers → e+ (**decisive**; the seed gives 110 kW for the 40 kWh, unchecked). Source: electrive.com/2019/01/09/nissan-leaf-with-62-kwh-battery-now-up-for-order
- Heat pump by trim and 3.6 vs 6.6 kW on-board charger: 🔴.

### Hyundai Ioniq 5 (gen1)
- **MY2023 (Europe H2 2022; German dealers autumn 2022): 72.6 → 77.4 kWh. 58 kWh unchanged. Outputs 125 / 168 / 239 kW. Optional digital side mirrors (first in Europe). Battery conditioning** 🟢. *Spot it:* cameras instead of door mirrors → MY2023+ (**decisive** when present; absence proves nothing). Battery kWh in the ad (73 vs 77). Sources: hyundai.news/eu/articles/press-releases/updated-ioniq-5-with-new-battery-and-digital-mirrors.html ; insideevs.com/news/566583/europe-2023-hyundai-ioniq5-enhancements/ ; hyundai.news/de/articles/press-releases/hyundai-ioniq-5-mehr-leistung-groessere-batterie-und-reichweite.html
- 2024 facelift (84 kWh): 🔴 not read.

### BMW i3 (I01)
- **60 Ah 22.6 kWh (2013) → 94 Ah 33 kWh (2016) → 120 Ah 42.2 kWh (market launch Nov 2018)**. With 120 Ah, 11 kW three-phase AC and 50 kW CCS became standard 🟡. *Spot it:* first registration from Nov 2018 is a **strong** clue for 120 Ah (cars built after 1 Nov 2018 got it). Ad text "120Ah" is decisive. Source: electrive.com/2018/09/28/new-120-ah-battery-cells-bmw-boosts-i3-and-i3s-range

### Hyundai Ioniq Electric
- **Facelift Sept 2019: 28 → 38.3 kWh; on-board charger 6.6 → 7.2 kW** 🟢. *Spot it:* new closed-grille pattern, redesigned LED DRLs and lights, redesigned 16" wheels (**decisive** in photos). Source: hyundai.news/uk/press-kit-archive/ioniq-2019/new-ioniq-electric-gets-important-enhancements.html

### MG ZS EV
- **Facelift (Oct 2021): Standard 51 kWh, Long Range 72 kWh, DC up to 76 kW, AC 7 kW. Smooth front bumper with no conventional grille** 🟡. ⚠ Fleet News says the old pack was "41.5 kWh"; the seed says 44.5 gross. Unresolved 🔴. Chemistry not stated 🔴. *Spot it:* no grille → facelift (**decisive**). Source: fleetnews.co.uk/news/manufacturer-news/2021/10/08/mg-unveils-facelifted-zs-ev-with-longer-range

### MG4 (gen1)
- **DC peak by battery: 51 kWh 117 kW, 64 kWh 135 kW, XPower 64 kWh 140 kW, 77 kWh 144 kW** 🟡. LFP/NMC by version, on-board charger by trim and heat pump by trim: 🔴 (the Swedish spec PDF's markers were unreadable). Source: drivingelectric.com/mg/4/41633/mg4-ev-range-battery-charging

---

## 3. Registration papers and open data (for clue types)
- FR carte grise **P.2** (kW) and **D.2** (version) are taken from the spec §3 as given (🟡). Not re-checked here.
- NL RDW: dataset field names (e.g. battery, range, version) could **not** be confirmed. The RDW API pages were blocked (§5). WS1 should check the "Gekentekende voertuigen brandstof" (`8ys7-d773`) and "Gekentekende voertuigen" (`m9d7-ebf2`) column lists directly. RDW datasets are marked Public Domain / CC0 (seen on the rupsbanden dataset `3xwf-ince`) 🟡. **Whether RDW holds battery kWh at all is 🔴.**

### Proposed extra clue types for `data/taxonomy/clue_types.yaml` (T-046)
- `dc_charge_kw`: peak DC kW from the ad (VW ID, Enyaq, Q4).
- `in_car_menu`: software version or "Additional vehicle information" screens (Tesla HW, VW software 3.x).
- `vehicle_mass_kg`: mass on the registration papers (Model Y BYD vs CATL). Low weight until the definitions are checked.
- `vin_position` must allow plant (Tesla pos 11) as well as motor/fuel positions.

---

## 4. Ready-to-import table (VariantClue, T-044 / spec §4)

Column notes:
- `value` holds a single value or a range (`A..B`, dates `YYYY-MM`). `rules_out` is `;`-separated.
- `source` is a short label, with `source_url` beside it.
- `market` is ISO 3166 alpha-2, or `global`.
- `retrieved_at` = 2026-11-15 for every row.
- `confidence` uses the schema's words: high = 🟢, medium = 🟡, low = 🔴.
- ids marked `(new)` are proposed variant ids that are not in the seed yet.

| variant_id | clue_type | market | value | strength | rules_out | source | source_url | retrieved_at | confidence |
|---|---|---|---|---|---|---|---|---|---|
| tesla-model-3-gen1-sr-plus-lfp | vin_position | global | pos11=C (Shanghai) | strong | tesla-model-3-gen1-sr-plus | Electrive + InsideEVs VIN guide | https://www.electrive.com/2020/10/19/tesla-starts-exporting-chinese-model-3-units/ | 2026-11-15 | medium |
| tesla-model-3-gen1-sr-plus-lfp | build_date_range | global | 2020-10.. | weak | tesla-model-3-gen1-sr-plus | Electrive | https://www.electrive.com/2020/10/19/tesla-starts-exporting-chinese-model-3-units/ | 2026-11-15 | medium |
| tesla-model-3-gen1-sr-plus-lfp | vin_position | global | pos7=F (LFP), MY2024+ only | decisive | tesla-model-3-gen1-sr-plus;tesla-model-3-gen1-long-range;tesla-model-3-gen1-performance | InsideEVs VIN decoder | https://insideevs.com/news/561819/identify-tesla-origin-vin-decoder/ | 2026-11-15 | medium |
| tesla-model-3-gen1-long-range | visible_feature | global | black (chrome-delete) window trim = 2021 refresh with heat pump | strong | | Electrek | https://electrek.co/2020/10/16/tesla-launches-model-3-2021-refresh-range-features/ | 2026-11-15 | medium |
| tesla-model-3-gen1-long-range | build_date_range | global | HW3 from 2019-04-12 (approx) | weak | | TMC forum | https://teslamotorsclub.com/tmc/threads/definite-guide-find-out-if-you-have-hw3-0-or-hw2-5.154750/ | 2026-11-15 | medium |
| tesla-model-3-gen1-long-range | in_car_menu | global | glovebox hardware cover serial prefix vs parts catalogue = HW2.5/HW3 | decisive | | TMC forum | https://teslamotorsclub.com/tmc/threads/definite-guide-find-out-if-you-have-hw3-0-or-hw2-5.154750/ | 2026-11-15 | medium |
| tesla-model-y-gen1-rwd | vin_position | global | pos11=B (Berlin) + RWD = BYD LFP 55 kWh usable | strong | | autoevolution | https://www.autoevolution.com/news/tesla-adds-a-new-model-y-variant-at-giga-berlin-with-byd-structural-battery-packs-214520.html | 2026-11-15 | medium |
| tesla-model-y-gen1-rwd | vin_position | global | pos11=C (Shanghai) + RWD = CATL LFP 60 kWh | strong | | autoevolution | https://www.autoevolution.com/news/tesla-adds-a-new-model-y-variant-at-giga-berlin-with-byd-structural-battery-packs-214520.html | 2026-11-15 | medium |
| tesla-model-y-gen1-rwd | vehicle_mass_kg | global | 2087 (BYD) vs 2153 (CATL) | weak | | autoevolution | https://www.autoevolution.com/news/tesla-adds-a-new-model-y-variant-at-giga-berlin-with-byd-structural-battery-packs-214520.html | 2026-11-15 | medium |
| tesla-model-y-gen1-long-range | visible_feature | global | red-tinted camera lenses = HW4 | strong | | Drive Tesla Canada + CleanTechnica | https://driveteslacanada.ca/model-y/tesla-phases-out-hw3-as-giga-berlin-starts-model-y-production-with-hw4/ | 2026-11-15 | high |
| tesla-model-y-gen1-long-range | build_date_range | DE | Berlin HW4 from 2024-05 (approx, mixed during transition) | weak | | Drive Tesla Canada | https://driveteslacanada.ca/model-y/tesla-phases-out-hw3-as-giga-berlin-starts-model-y-production-with-hw4/ | 2026-11-15 | medium |
| renault-zoe-ph2-r135 | power_kw | global | 100 | decisive | renault-zoe-ph2-r110 | Zapmap | https://www.zapmap.com/index%2ephp/news/renault-reveals-new-zoe-z-e-50 | 2026-11-15 | medium |
| renault-zoe-ph2-r110 | visible_feature | global | CCS inlet under front flap = Ph2 | decisive | renault-zoe-ph1-q210;renault-zoe-ph1-r240;renault-zoe-ph1-q90;renault-zoe-ph1-r90;renault-zoe-ph1-r110 | Zapmap | https://www.zapmap.com/index%2ephp/news/renault-reveals-new-zoe-z-e-50 | 2026-11-15 | medium |
| renault-zoe-ph2-r110 | battery_kwh | global | 52 | strong | renault-zoe-ph1-q90;renault-zoe-ph1-r90;renault-zoe-ph1-r110 | Zapmap | https://www.zapmap.com/index%2ephp/news/renault-reveals-new-zoe-z-e-50 | 2026-11-15 | medium |
| volkswagen-id3-gen1-pro | dc_charge_kw | global | 120 (from 2021-05 configurator) | weak | | InsideEVs DE | https://insideevs.de/news/509225/vw-id3-ladeleistung-konfigurator/ | 2026-11-15 | medium |
| volkswagen-id3-gen1-pure | dc_charge_kw | global | 50 std; 110 option (2021-05) | weak | | InsideEVs DE | https://insideevs.de/news/509225/vw-id3-ladeleistung-konfigurator/ | 2026-11-15 | medium |
| volkswagen-id3-gen1-pro-s | in_car_menu | global | software >=3.0 = 135 kW DC (was 125) | weak | | Electrek + InsideEVs DE | https://electrek.co/2022/03/21/volkswagen-announces-generation-3-0-software-update-for-id-evs-including-assisted-driving-and-charging-improvements/ | 2026-11-15 | high |
| volkswagen-id3-gen1-pro-s | visible_feature | global | body-colour bonnet, no black strip under windscreen = facelift (2023-03+) | decisive | | Electrive DE | https://www.electrive.net/2023/09/26/vw-id-3-im-test-was-hat-die-modellpflege-gebracht/ | 2026-11-15 | medium |
| volkswagen-id3-gen1-pro-s | visible_feature | global | 12-inch centre screen = facelift; 10-inch = pre-facelift | strong | | Electrive DE | https://www.electrive.net/2023/09/26/vw-id-3-im-test-was-hat-die-modellpflege-gebracht/ | 2026-11-15 | medium |
| volkswagen-id3-gen1-pro-s | dc_charge_kw | global | 170 (facelift, VW) | strong | | VW newsroom | https://www.volkswagen-newsroom.com/en/the-new-id3-valuable-likeable-digital-15490/drive-battery-and-charging-15493 | 2026-11-15 | high |
| volkswagen-id4-gen1-pro | in_car_menu | global | software >=3.0 = 135 kW DC (was 125) | weak | | Electrek + InsideEVs DE | https://insideevs.de/news/554811/volkswagen-id-modelle-mehr-ladeleistung/ | 2026-11-15 | high |
| volkswagen-id4-gen1-pure | dc_charge_kw | global | 110 | strong | volkswagen-id4-gen1-pro;volkswagen-id4-gen1-gtx | InsideEVs DE | https://insideevs.de/news/554811/volkswagen-id-modelle-mehr-ladeleistung/ | 2026-11-15 | medium |
| audi-q4-e-tron-gen1-40 | power_kw | global | 150 | decisive | audi-q4-e-tron-gen1-45-my24 (new);audi-q4-e-tron-gen1-50-quattro | Audi MediaCenter + Electrive | https://www.electrive.com/2023/09/21/audi-fits-q4-e-tron-with-new-electric-motor/ | 2026-11-15 | high |
| audi-q4-e-tron-gen1-50-quattro | power_kw | global | 220 | decisive | audi-q4-e-tron-gen1-55-quattro-my24 (new) | Electrive | https://www.electrive.com/2023/09/21/audi-fits-q4-e-tron-with-new-electric-motor/ | 2026-11-15 | high |
| audi-q4-e-tron-gen1-45-quattro (new) | power_kw | global | 190 | decisive | audi-q4-e-tron-gen1-45-my24 (new);audi-q4-e-tron-gen1-45-quattro-my24 (new) | Electrive | https://www.electrive.com/2023/09/21/audi-fits-q4-e-tron-with-new-electric-motor/ | 2026-11-15 | high |
| audi-q4-e-tron-gen1-45-my24 (new) | power_kw | global | 210 | decisive | audi-q4-e-tron-gen1-40;audi-q4-e-tron-gen1-45-quattro (new) | Audi MediaCenter | https://www.audi-mediacenter.com/en/press-releases/update-for-the-audi-q4-e-tron-more-range-more-efficiency-more-emotions-15594 | 2026-11-15 | high |
| audi-q4-e-tron-gen1-45-my24 (new) | build_date_range | global | orders from 2023-09-26 | strong | audi-q4-e-tron-gen1-40;audi-q4-e-tron-gen1-45-quattro (new) | Audi MediaCenter | https://www.audi-mediacenter.com/en/press-releases/update-for-the-audi-q4-e-tron-more-range-more-efficiency-more-emotions-15594 | 2026-11-15 | high |
| audi-q4-e-tron-gen1-45-my24 (new) | dc_charge_kw | global | 135 (RWD) | strong | audi-q4-e-tron-gen1-45-quattro-my24 (new) | Audi MediaCenter | https://www.audi-mediacenter.com/en/press-releases/update-for-the-audi-q4-e-tron-more-range-more-efficiency-more-emotions-15594 | 2026-11-15 | high |
| audi-q4-e-tron-gen1-55-quattro-my24 (new) | power_kw | global | 250 | decisive | audi-q4-e-tron-gen1-50-quattro | Audi MediaCenter | https://www.audi-mediacenter.com/en/press-releases/update-for-the-audi-q4-e-tron-more-range-more-efficiency-more-emotions-15594 | 2026-11-15 | high |
| audi-q4-e-tron-gen1-35 | battery_kwh | global | 52 net (dropped autumn 2022) | decisive | audi-q4-e-tron-gen1-40;audi-q4-e-tron-gen1-50-quattro | Electrive | https://www.electrive.com/2023/09/21/audi-fits-q4-e-tron-with-new-electric-motor/ | 2026-11-15 | high |
| audi-e-tron-ge-55 | build_date_range | global | 2018-09..2019-11 = 83.6 kWh usable unless workshop update done | strong | | Electrive | https://www.electrive.com/2021/10/28/audi-releases-range-update-for-older-e-tron-models | 2026-11-15 | high |
| audi-e-tron-ge-55 | battery_kwh | global | 86.5 net (95 gross) after update / later builds | strong | | Audi MediaCenter | https://audi-mediacenter.com/en/press-releases/better-efficiency-and-longer-range-technical-update-for-the-audi-e-tron-12382 | 2026-11-15 | high |
| hyundai-kona-electric-os-64kwh | onboard_charger | global | 7.2 kW 1-ph (pre-MY2020) / 11 kW 3-ph (MY2020+) | decisive | | Electrive DE + InsideEVs | https://www.electrive.net/2019/05/09/hyundai-kona-elektro-erhaelt-dreiphasigen-ac-lader-11-kw/ | 2026-11-15 | high |
| hyundai-kona-electric-os-64kwh | build_date_range | global | 11 kW from deliveries end-2019 (many EU markets) | strong | | InsideEVs | https://insideevs.com/news/348727/hyundai-3-phase-charger-kona-europe/ | 2026-11-15 | high |
| kia-niro-ev-de-64kwh | trim_name | GB | "4+" = 11 kW 3-ph AC; "3" = 7 kW (from 2020-06) | decisive | | Zapmap + Green Car Guide | https://www.zapmap.com/news/kia-adds-e-niro-39-kwh-and-faster-charging-to-range | 2026-11-15 | high |
| kia-niro-ev-de-39kwh | trim_name | GB | "2" = 39 kWh (from 2020-06) | decisive | kia-niro-ev-de-64kwh | Zapmap + Green Car Guide | https://www.greencarguide.co.uk/2020/06/kia-e-niro-gains-new-battery-and-new-trim-levels/ | 2026-11-15 | high |
| peugeot-e-208-p21-51kwh | power_kw | global | 115 | decisive | peugeot-e-208-p21-50kwh | Stellantis press | https://www.media.stellantis.com/em-en/peugeot/press/new-100-electric-peugeot-e-208-more-powerful-more-efficient-and-up-to-400-km-in-range | 2026-11-15 | high |
| peugeot-e-208-p21-51kwh | battery_kwh | global | 51 gross / 48.1 net | strong | peugeot-e-208-p21-50kwh | Stellantis press | https://www.media.stellantis.com/em-en/peugeot/press/new-100-electric-peugeot-e-208-more-powerful-more-efficient-and-up-to-400-km-in-range | 2026-11-15 | high |
| peugeot-e-208-p21-50kwh | onboard_charger | global | 7.4 kW 1-ph std; 11 kW 3-ph option (ask seller) | weak | | Stellantis press | https://www.media.stellantis.com/em-en/peugeot/press/new-100-electric-peugeot-e-208-more-powerful-more-efficient-and-up-to-400-km-in-range | 2026-11-15 | high |
| peugeot-e-208-p21-50kwh | build_date_range | global | heat pump introduced 2021 optimisation (fitment per trim unknown) | weak | | Stellantis press | https://www.media.stellantis.com/em-en/peugeot/press/new-100-electric-peugeot-e-208-more-powerful-more-efficient-and-up-to-400-km-in-range | 2026-11-15 | medium |
| volvo-xc40-recharge-gen1-single-rwd-my24 | trim_name | global | "Single Motor" RWD / "Extended Range" (82 kWh) from 2023-01 | strong | volvo-xc40-recharge-gen1-p6-single-fwd | InsideEVs | https://insideevs.com/news/631329/volvo-xc40-c40-recharge-go-rwd-get-range-charging-boost/ | 2026-11-15 | medium |
| volvo-xc40-recharge-gen1-single-rwd-my24 | dc_charge_kw | global | 200 (82 kWh RWD; was 150) | strong | volvo-xc40-recharge-gen1-p6-single-fwd | InsideEVs | https://insideevs.com/news/631329/volvo-xc40-c40-recharge-go-rwd-get-range-charging-boost/ | 2026-11-15 | medium |
| skoda-enyaq-gen1-80 | power_kw | global | 150 | decisive | skoda-enyaq-gen1-85 | Škoda Storyboard | https://www.skoda-storyboard.com/en/emobility/the-improved-enyaq-is-here-with-more-power-and-longer-range/ | 2026-11-15 | high |
| skoda-enyaq-gen1-85 | power_kw | global | 210 | decisive | skoda-enyaq-gen1-80 | Škoda Storyboard | https://www.skoda-storyboard.com/en/emobility/the-improved-enyaq-is-here-with-more-power-and-longer-range/ | 2026-11-15 | high |
| skoda-enyaq-gen1-85 | build_date_range | global | production from 2023-11 | strong | skoda-enyaq-gen1-80 | Škoda Storyboard | https://www.skoda-storyboard.com/en/emobility/the-improved-enyaq-is-here-with-more-power-and-longer-range/ | 2026-11-15 | high |
| skoda-enyaq-gen1-80x-rs | dc_charge_kw | GB | 175 on 85x/vRS MY24 (+40 kW) | strong | | Škoda UK | https://www.skoda.co.uk/news/details/enhanced-enyaq-delivers-faster-charging-more-equipment-and-more-range | 2026-11-15 | medium |
| nissan-leaf-ze0-24kwh | trim_name | GB | "Visia" = 24 kWh only (from 2015-12) | decisive | nissan-leaf-ze0-30kwh | What Car? | https://www.whatcar.com/news/2016-nissan-leaf-gets-increased-155-mile-range-new-battery/ | 2026-11-15 | medium |
| nissan-leaf-ze0-30kwh | build_date_range | GB | 2015-12.. (Acenta/Tekna) | weak | | What Car? | https://www.whatcar.com/news/2016-nissan-leaf-gets-increased-155-mile-range-new-battery/ | 2026-11-15 | medium |
| nissan-leaf-ze1-e-plus-62kwh | power_kw | global | 160 | decisive | nissan-leaf-ze1-40kwh | Electrive | https://www.electrive.com/2019/01/09/nissan-leaf-with-62-kwh-battery-now-up-for-order | 2026-11-15 | medium |
| nissan-leaf-ze1-e-plus-62kwh | trim_name | global | "3.ZERO e+" (launch edition 2019) | strong | nissan-leaf-ze1-40kwh | Electrive | https://www.electrive.com/2019/01/09/nissan-leaf-with-62-kwh-battery-now-up-for-order | 2026-11-15 | medium |
| hyundai-ioniq-5-gen1-77kwh-rwd | battery_kwh | global | 77.4 (MY2023, EU H2 2022) | decisive | hyundai-ioniq-5-gen1-73kwh-rwd | Hyundai EU press + InsideEVs | https://www.hyundai.news/eu/articles/press-releases/updated-ioniq-5-with-new-battery-and-digital-mirrors.html | 2026-11-15 | high |
| hyundai-ioniq-5-gen1-77kwh-rwd | power_kw | DE | 168 | strong | hyundai-ioniq-5-gen1-58kwh-rwd | Hyundai DE press | https://www.hyundai.news/de/articles/press-releases/hyundai-ioniq-5-mehr-leistung-groessere-batterie-und-reichweite.html | 2026-11-15 | high |
| hyundai-ioniq-5-gen1-77kwh-awd | power_kw | DE | 239 | strong | hyundai-ioniq-5-gen1-77kwh-rwd | Hyundai DE press | https://www.hyundai.news/de/articles/press-releases/hyundai-ioniq-5-mehr-leistung-groessere-batterie-und-reichweite.html | 2026-11-15 | high |
| hyundai-ioniq-5-gen1-77kwh-rwd | visible_feature | global | camera side mirrors present = MY2023+ (absence proves nothing) | decisive | hyundai-ioniq-5-gen1-73kwh-rwd;hyundai-ioniq-5-gen1-73kwh-awd | Hyundai EU press | https://www.hyundai.news/eu/articles/press-releases/updated-ioniq-5-with-new-battery-and-digital-mirrors.html | 2026-11-15 | high |
| bmw-i3-i01-120ah | build_date_range | global | built from 2018-11-01 | strong | bmw-i3-i01-94ah;bmw-i3-i01-60ah | Electrive | https://electrive.com/2018/09/28/new-120-ah-battery-cells-bmw-boosts-i3-and-i3s-range | 2026-11-15 | medium |
| bmw-i3-i01-120ah | battery_kwh | global | 42.2 | decisive | bmw-i3-i01-94ah;bmw-i3-i01-60ah | Electrive | https://electrive.com/2018/09/28/new-120-ah-battery-cells-bmw-boosts-i3-and-i3s-range | 2026-11-15 | medium |
| bmw-i3-i01-94ah | battery_kwh | global | 33 | decisive | bmw-i3-i01-120ah;bmw-i3-i01-60ah | Electrive | https://electrive.com/2018/09/28/new-120-ah-battery-cells-bmw-boosts-i3-and-i3s-range | 2026-11-15 | medium |
| hyundai-ioniq-electric-gen1-38kwh | visible_feature | global | new closed-grille pattern, redesigned LED DRLs, new 16" wheels (2019-09+) | decisive | hyundai-ioniq-electric-gen1-28kwh | Hyundai UK press | https://www.hyundai.news/uk/press-kit-archive/ioniq-2019/new-ioniq-electric-gets-important-enhancements.html | 2026-11-15 | high |
| hyundai-ioniq-electric-gen1-38kwh | onboard_charger | global | 7.2 kW (was 6.6) | strong | hyundai-ioniq-electric-gen1-28kwh | Hyundai UK press | https://www.hyundai.news/uk/press-kit-archive/ioniq-2019/new-ioniq-electric-gets-important-enhancements.html | 2026-11-15 | high |
| mg-zs-ev-gen1-long-range | visible_feature | global | smooth front bumper, no conventional grille = facelift (2021-10+) | decisive | mg-zs-ev-gen1-44kwh | Fleet News | https://www.fleetnews.co.uk/news/manufacturer-news/2021/10/08/mg-unveils-facelifted-zs-ev-with-longer-range | 2026-11-15 | medium |
| mg-zs-ev-gen1-long-range | battery_kwh | global | 72 | decisive | mg-zs-ev-gen1-standard-range;mg-zs-ev-gen1-44kwh | Fleet News | https://www.fleetnews.co.uk/news/manufacturer-news/2021/10/08/mg-unveils-facelifted-zs-ev-with-longer-range | 2026-11-15 | medium |
| mg-mg4-gen1-standard | dc_charge_kw | GB | 117 | strong | mg-mg4-gen1-long-range;mg-mg4-gen1-extended-range | DrivingElectric | https://www.drivingelectric.com/mg/4/41633/mg4-ev-range-battery-charging | 2026-11-15 | medium |
| mg-mg4-gen1-long-range | dc_charge_kw | GB | 135 | strong | mg-mg4-gen1-standard;mg-mg4-gen1-xpower | DrivingElectric | https://www.drivingelectric.com/mg/4/41633/mg4-ev-range-battery-charging | 2026-11-15 | medium |

---

## 5. Gaps, blocked pages, and conflicts to fix

**Blocked during this session** (permission prompt timed out; not retried):
- ev-inventory.com (Tesla model history, redirected from tesla-info.com)
- bevolt.com (Automobile Propre French used-EV top list)
- insideevs.com/news/406496 (Tesla HW2.5 vs 3.0)
- newsroom.bmwgroup.com (i3 120 Ah release)
- opendata.rdw.nl views `8ys7-d773` and `m9d7-ebf2`

**Search budget:** the web-search limit was used up mid-task. FR and BE lists and the 🔴 models in §1 still need a follow-up run.

**Seed conflicts for WS3:**
- (a) Model 3 LFP start: the seed says late 2021, Electrive says Oct 2020.
- (b) Model Y RWD: the seed has one 57.5 kWh value, but sources give two packs (55 BYD Berlin / 60 CATL Shanghai).
- (c) Enyaq 80 DC: the seed says 125 kW, Škoda UK says 135 kW (MY23).
- (d) The Q4 post-MY24 variants are missing from the seed.
- (e) MG ZS EV old pack: the seed says 44.5 kWh, Fleet News says 41.5 kWh.

**Still unknown 🔴:**
- Zoe Ph1 Q vs R charger and battery rental clues
- Leaf heat pump by trim and the 3.6 / 6.6 kW chargers
- MG4 chemistry, on-board charger and heat pump by trim
- Kona battery recall and 2021 facelift
- Ioniq 5 2024 (84 kWh)
- Model 3 Highland and HW4
- ID.4 2023/24 update details
- whether RDW holds battery kWh at all
- which non-Tesla makes encode battery in the VIN (none confirmed here)
