# R-21 Heat pump fitment for the ~40 most common used EVs (NL / DE / FR / BE / UK)

Researched 2026-11-15 by a WS3 research agent for T-031. Time-boxed, and cut short when the shared web-search budget for the session ran out (see "Gaps"). Confidence: 🟢 official maker document · 🟡 secondary source (press, test, dealer, forum consensus) · 🔴 unsure, single weak source, or not found.

## The answer

Only **8 of the ~40 models** have a heat pump status we can import with fair confidence. The rest stay `not_disclosed`, and the Trip fit UI shows both cases (spec §"Unknown heat pump on used cars").
- **Option (paid extra), so a used car may or may not have one:** the VW group MEB cars (VW ID.3 / ID.4 / ID.5, Škoda Enyaq, and the Cupra Born MY26) 🟢/🟡. Germany also lists Hyundai Kona and Ioniq 5, Kia EV6 and the Polestar 2 Standard Range as option-only 🟡.
- **Standard:** Tesla Model 3 from the 2021 refresh, Tesla Model Y 🟡, Renault Zoe (both phases, trim split not proven) 🟡/🟢, and the BMW i4, Mercedes EQA and Renault Mégane E-Tech, each listed as standard by two German secondary sources 🟡.
- **None:** Tesla Model 3 2019–2020 🟡, Nissan Leaf 2011–2012 🟡 and Dacia Spring Electric 100 🟡.

**Three of the brief's starting assumptions do not hold up:**
1. 🟡 **The Nissan Leaf does have a heat pump on many cars.** Nissan added it with the 2013 British-built update, and Nissan's own promoted copy for the 2018 Leaf says "the new LEAF uses an innovative heat-pump for the cabin". Fitment by trim is not published in anything we opened, so the Leaf has to be `not_disclosed` per trim, not `none`.
2. 🔴 **We could not confirm "Peugeot e-208: none until 2023, then option".** Electrive reports a new, more efficient heat pump for e-208/e-2008 "from 2022". A German dealer list (undated) shows it as standard. Stellantis UK (June 2025) confirms it as standard on the GT Premium trim. The 2019–2021 status is not disclosed.
3. 🟡 **The Zoe heat pump is not "an option from 2017".** It was a launch feature in 2012–13 coverage. The Renault Germany 09/2019 price list shows it included on all three ZE50 trims, and Renault Switzerland (Feb 2024) lists it as standard.

**Used-car trap (VW group, model years 2022–2023):** 🟡 VW delivered ID. cars *without* the optional heat pump during the chip shortage. In January 2023 the option could not be picked at all in the German configurator, and Canadian buyers got the price taken off their bill. Some cars ordered with a heat pump may not have one. The UI should never infer fitment from the order spec or the trim.

## 1. Which models, and why (popularity basis)

The list joins four public rankings with the generations already in `data/seed/models.yaml`. That seed list was itself built as "used-EV favourites", so most of the ranked models already have generation ids.

| Market | Basis | What it gives | Link (opened 2026-11-15) |
|---|---|---|---|
| DE | KBA vehicle stock at 1 Jan 2026, as reported by electrive | Top 10 BEVs in stock: ID.3 116,053 · Model Y 106,184 · ID.4/ID.5 97,120 · Model 3 81,352 · Enyaq 80,970 · Zoe 79,417 · Fiat 500 60,571 · Born 60,256 · Smart Fortwo 57,341 · VW Up 56,334 | https://www.electrive.net/2026/04/28/vw-id-3-ist-das-verbreitetste-e-auto-in-deutschland/ |
| NL | TopGear NL, used EV sales 2025 (the article does not name the data source 🟡) | Model 3 11,338 · ID.3 4,595 · Audi e-tron 4,236 · Kia Niro 3,960 · Model Y 3,327 · Kona 3,106 · Peugeot 208 2,653 · XC40 2,522 · Enyaq 2,448 · Zoe 2,380 | https://topgear.nl/autonieuws/populairste-gebruikte-ev-van-2025-is-toevallig-ook-een-exportfavoriet/ |
| FR | rouleur-electrique.fr, used EV sales 2025 (no data source named 🟡) | Zoe 23,490 · e-208 15,220 · Model 3 12,928 · Fiat 500e 11,791 · Dacia Spring 8,181 | https://rouleur-electrique.fr/la-renault-zoe-domine-encore-le-marche-de-lelectrique-doccasion-en-2025/ |
| UK | cinch retailer data, Q1 2025, rank only | Model 3 · Leaf · MINI · Kona Electric · Corsa-e · e-Niro · Zoe · ID.3 · I-Pace · Mokka-e | https://www.cinch.co.uk/news/used-ev-sales-up-39-percent |
| UK | SMMT used-car release, 10 Feb 2026: 274,815 used BEV transactions in 2025, but no per-model breakdown | context only | https://www.smmt.co.uk/evs-power-up-used-car-market-in-three-year-growth-run/ |
| BE | 🔴 No source found before the search budget ran out. Gap: FEBIAC or DIV data should be checked. | — | — |

**Justification:** every model that appears in two or more of these rankings is included. The remaining places in the ~40 are filled with seed-list generations that are common in at least one market (Leaf, i3, e-Golf, Ioniq, I-Pace, MG4/ZS, Polestar 2, EQA/EQC, Mach-E, e-C4, etc.). VW e-up!, ID.5 and Opel Mokka-e are in the rankings but not yet in `models.yaml`; they are marked "(new slug)" below. DfT VEH0160 (UK licensed stock by model) and RDW open data (NL) would be the better primary bases. Both were planned but not reached; WS1 can compute them when it ingests those datasets.

## 2. Fitment per model

Market codes: `ALL` = no market difference found; `EU` = statement about continental Europe; `DE`, `FR`, `CH`; `GB` (ISO code for the UK). The "Source" column gives the link we opened. Notes summarise what the source says, in our own words.

| # | Model / generation | MY | Market | Heat pump | Conf. | Evidence (paraphrased) | Source |
|---|---|---|---|---|---|---|---|
| 1 | Tesla Model 3 (pre-refresh) | 2019–2020 | ALL | none | 🟡 | Nyland test: 2019 car without a heat pump vs a 2021 car with one | https://insideevs.com/features/458189/2021-tesla-model-3-heat-pump-test-vs-2019-model/ |
| 2 | Tesla Model 3 (refresh) | 2021–2023 | ALL | standard | 🟡 | "The 2021 Model 3 has a heat pump as standard"; Electrek (source-based) and DiscoverEV agree | same as above · https://electrek.co/2020/10/16/tesla-launches-model-3-2021-refresh-range-features/ |
| 3 | Tesla Model 3 Highland | 2024– | ALL | not_disclosed | 🔴 | Almost certainly standard, but we opened no Tesla doc or test for Highland | — |
| 4 | Tesla Model Y gen1 | 2021–2024 | ALL | standard | 🟡 | Model Y was Tesla's first car with a heat pump (DiscoverEV); German guide (Feb 2023) says Tesla fits it as standard on all cars | https://www.discoverev.co.uk/ev-reviews/tesla-model-3-long-range-2021-review · https://einfacheauto.de/blog/welche-e-autos-haben-eine-warmepumpe |
| 5 | Tesla Model Y Juniper | 2025– | DE | standard | 🟡 | Auto Bild (30 Dec 2025) lists Model Y among cars with a standard heat pump | https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html |
| 6 | Tesla Model S (gen1, facelift) | 2013–2021 | ALL | not_disclosed | 🔴 | Only a weak US aggregator says pre-2021 cars used resistive heat | https://recharged.com/articles/which-evs-have-heat-pump/ |
| 7 | Tesla Model S Palladium | 2022– | ALL | not_disclosed | 🔴 | Same weak source says standard from the refresh; not verified | same |
| 8 | Renault Zoe ph1 | 2013–2019 | ALL | standard | 🟡 | 2012 launch coverage describes the Zoe's heat pump as a core feature, with no trim caveat. Trim split not proven. | https://www.greenmotor.co.uk/2012/03/renault-zoe-ze-unmasked-keenly-priced.html · https://www.torquenews.com/1075/renault-releases-details-zoe-electric-car-ahead-launching-sales-march |
| 9 | Renault Zoe ph2 (ZE50) | 2019–2024 | DE | standard | 🟡 | Renault DE price list 09/2019: the "2-circuit heat pump" row appears as included on Life, Experience and Intens. Our reading of the PDF symbols is inferred, hence 🟡. | https://professional.auto-motor-und-sport.de/static-download/news/1775221/pl_zoe_0919.pdf |
| 10 | Renault Zoe ph2 | 2022 | GB | standard | 🟡 | Renault IE/UK eBrochure Feb 2022: heat pump in base Play kit, inherited by higher trims (inferred) | https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/car-ebrochures/ZOE-eBrochure.pdf |
| 11 | Renault Zoe ph2 | 2024 | CH | standard | 🟢 | Renault CH price list from Feb 2024: heat pump among standard equipment of Evolution (Iconic builds on it) | https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Neuer_ZOE_PL_f.pdf |
| 12 | Renault Mégane E-Tech | 2025– | DE | standard | 🟡 | Auto Bild Dec 2025: standard. Earlier model years not checked. | https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html |
| 13 | Nissan Leaf ZE0 (pre-update) | 2011–2012 | GB | none | 🟡 | Heat pump was introduced with the 2013 update (Nissan Insider buyer's guide) | https://nissaninsider.co.uk/buyers-guide-choosing-a-used-nissan-leaf/ |
| 14 | Nissan Leaf AZE0 | 2013–2017 | GB | not_disclosed | 🟡 | Heat pump added in 2013 ("70% more efficient heating"), but no source opened gives the trim split | https://nissaninsider.co.uk/three-trim-levels-and-new-pricing-structure-for-next-generation-leaf/ |
| 15 | Nissan Leaf ZE1 | 2018–2025 | GB/EU | not_disclosed | 🔴 | Nissan promoted copy: "uses a heat-pump for the cabin". NZ buyer's guide: UK-new cars sometimes lack it. Trim split unknown. | https://www.whatcar.com/news/promoted-conquer-the-cold-with-the-new-nissan-leaf/n18295 · https://evdb.nz/wp-content/uploads/2025/07/Nissan-Leaf-buyers-guide-NZ-2017-2024-v2.pdf |
| 16 | Nissan Leaf gen3 | 2025– | ALL | not_disclosed | 🔴 | not researched | — |
| 17 | VW ID.3 gen1 | 2020–2023 | EU | option | 🟢 | VW: "optional heat pump" for ID.3/4/5; first priced €1,250, cut to €990 (June 2021); 2022–23 cars delivered without it during chip shortage | https://volkswagen.ie/en/electric-cars/software-and-technology/id-technology/heat-pump.html · https://www.elektroauto-news.net/news/vw-erstattet-enttaeuschten-waermepumpen-kunden-285-euro · https://ecomento.de/2023/01/24/vw-kann-elektroautos-aktuell-nicht-mit-waermepumpe-ausliefern |
| 18 | VW ID.3 (facelift) | 2024– | AT/DE | option | 🟢 | VW Austria ID.3 page: "optional heat pump"; Auto Bild 2025 agrees | https://www.volkswagen.at/id3-neo/id3-neo/waermepumpe |
| 19 | VW ID.4 gen1 | 2021– | EU | option | 🟢 | VW IE heat pump page (ID.3/4/5 optional) | https://volkswagen.ie/en/electric-cars/software-and-technology/id-technology/heat-pump.html |
| 20 | VW ID.5 (new slug) | 2022– | EU | option | 🟢 | same | same |
| 21 | Škoda Enyaq | 2023 | GB | option | 🟢 | Škoda UK 2023MY: heat pump single option £1,025 | https://www.skoda.co.uk/news/details/skoda-announces-raft-of-updates-and-enhancments-for-enyaq-iv |
| 22 | Škoda Enyaq | 2020– | DE | option | 🟡 | German dealer list (undated): option | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe |
| 23 | Cupra Born | 2021–2025 | EU | not_disclosed | 🔴 | 05/2024 brochure lists a heat pump, but its standard/option column was unreadable | https://www.cupraofficial.it/content/dam/public/cupra-website/generic/pdf/cupra-born-june-2024.pdf |
| 24 | Cupra Born 59 kWh | 2026 | DE | option | 🟡 | ev-supply.de: MY26 heat pump costs extra | https://www.ev-supply.de/blogs/cupra-born-elektroauto-news/cupra-born-150-kw-59-kwh-my26-warmepumpe |
| 25 | Hyundai Kona Electric OS | 2018–2023 | DE | option | 🟡 | Dealer list (undated, appears to cover 2022–23 models): option. Hyundai NZ says Kona has the heat pump tech but doesn't say if standard. | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe · https://www.hyundai.co.nz/about/media/pr/recycling-more-heat-hyundai-turn-up-ev-efficiency-with-new-heat-pump-technology |
| 26 | Hyundai Kona Electric OS | 2018–2023 | GB | not_disclosed | 🔴 | UK facelift launch reports (2021) don't mention it | https://www.businesscar.co.uk/news/2021/mar-8-14/specs-and-prices-revealed-for-facelifted-hyundai-kona-electric |
| 27 | Hyundai Kona Electric SX2 | 2023– | ALL | not_disclosed | 🔴 | not found | — |
| 28 | Hyundai Ioniq 5 | 2021– | DE | option | 🟡 | Dealer list (undated): option | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe |
| 29 | Kia EV6 | 2021– | DE | option | 🟡 | Dealer list: option. Auto Bild 2025: usually standard only on top trims. | same · https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html |
| 30 | Kia e-Niro (DE) | 2018–2022 | ALL | not_disclosed | 🔴 | Auto Bild tested one with a heat pump; UK trim releases checked don't mention it | https://www.zapmap.com/news/kia-adds-e-niro-39-kwh-and-faster-charging-to-range |
| 31 | Peugeot e-208 P21 | 2019–2021 | ALL | not_disclosed | 🔴 | Not found in the FR options guides checked | https://www.caradisiac.com/les-options-179574.htm |
| 32 | Peugeot e-208 P21 | 2022– | DE | standard | 🔴 | Electrive: new heat pump "from 2022" (status not stated); dealer list (undated): standard. Year range is our inference. | https://www.electrive.com/2021/11/25/peugeot-e-208-e-2008-receive-range-upgrade · https://www.meinauto.de/lp/elektroautos-mit-waermepumpe |
| 33 | Peugeot e-208 / e-2008 GT Premium | 2025– | GB | standard | 🟢 | Stellantis UK, 3 Jun 2025: heat pump standard on GT Premium. Other trims not stated. | https://www.media.stellantis.com/uk-en/peugeot/press/peugeot-announces-new-range-topping-gt-premium-trim-and-powertrain-enhancements-for-208-2008 |
| 34 | Peugeot e-2008 P24 | 2020–2021 | ALL | not_disclosed | 🔴 | as e-208 | — |
| 35 | Opel Corsa-e / Mokka-e (new slug) | 2020– | ALL | not_disclosed | 🔴 | not found (same Stellantis platform as e-208, but not assumed) | — |
| 36 | Fiat 500e (332) | 2020– | GB | not_disclosed | 🔴 | UK spec guide equipment lists don't mention a heat pump. Absence from a list ≠ none. | https://www.fiat.co.uk/content/dam/fiat2023/uk/price-and-specification-guides/new500/fiat-500e.pdf |
| 37 | Dacia Spring gen1 | 2021–2024 | ALL | not_disclosed | 🔴 | not found for earlier versions | — |
| 38 | Dacia Spring Electric 100 | 2025– | DE | none | 🟡 | ev-supply.de: cabin heating is resistive only | https://www.ev-supply.de/blogs/elektroauto-news/dacia-spring-electric-100-warmepumpe-alle-details |
| 39 | MG4 | 2022– | GB | not_disclosed | 🔴 | Owner forum: UK cars lacked it early on; not confirmed by MG | https://mgevs.com/goto/post?id=136681 |
| 40 | MG4 | 2022– | EU | not_disclosed | 🔴 | Same forum: standard on EU Luxury/Trophy. Owner reports only. | same |
| 41 | Polestar 2 Standard Range | 2025 | DE | option | 🟡 | ev-supply.de: optional, not standard | https://www.ev-supply.de/blogs/elektroauto-news/polestar-2-standard-range-single-motor-warmepumpe-alle-details |
| 42 | Polestar 2 | 2020–2024 | ALL | not_disclosed | 🔴 | not found | — |
| 43 | Audi e-tron (GE) | 2019–2022 | DE | not_disclosed | 🔴 | Dealer list says standard, but this conflicts with common reports of an option. Held back until a price list is checked. | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe |
| 44 | BMW i4 | 2021– | DE | standard | 🟡 | Dealer list + Auto Bild 2025 both: standard | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe · https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html |
| 45 | Mercedes EQA | 2021– | DE | standard | 🟡 | Dealer list + Auto Bild 2025 both: standard | same two |
| 46 | Mercedes EQC | 2019–2023 | DE | standard | 🟡 | Dealer list: standard (single source) | https://www.meinauto.de/lp/elektroautos-mit-waermepumpe |
| 47 | MINI Cooper SE (F56) | 2020–2023 | DE | standard | 🟡 | Dealer list: standard (single source) | same |
| 48 | VW e-up! (new slug) | 2020–2023 | ALL | not_disclosed | 🔴 | ADAC winter test groups it with "simple heating" cars; heater type not stated outright | https://www.adac.de/rund-ums-fahrzeug/elektromobilitaet/elektroauto/heizung-elektroauto/ |
| 49 | Not researched (search budget ran out) | — | ALL | not_disclosed | 🔴 | BMW i3, VW e-Golf (both), Hyundai Ioniq Electric, Ioniq 6, Kia Soul (both), Niro EV SG2, Audi Q8 e-tron, Q4 e-tron, Jaguar I-Pace, Volvo XC40/EX40, Ford Mach-E, Citroën ë-C4, BYD Atto 3, Honda e, smart (both), MG ZS EV, Fiat 500e 312, MINI J01 | — |

**On the German dealer list (meinauto.de):** the page is undated and lists models, not model years. We count it as one 🟡 source for the period the listed models were on sale. Where it is the only source, it should be replaced by a maker price list before the value is published.

## 3. Gaps and next steps (for WS3 / T-031)

- 🔴 **Search budget ran out at about 45 min.** It is shared across all agents in the turn. The models in row 49 were never searched. Next run: maker price-list PDFs (Preislisten / tarifs / price & spec guides) for each gap model, one per market. Price lists are the best source because they show standard vs option per trim and per date.
- 🔴 **Belgium:** no popularity source yet.
- **Primary popularity data:** DfT VEH0160 (UK) and RDW open data (NL) should replace the press rankings. WS1 can compute them.
- **Trim-level granularity:** where a heat pump is standard only on some trims (Leaf, EV6, MG4, e-208), the `variant_slug_hint` should point at the trim variant once `variants.yaml` has trims. Until then those stay `not_disclosed`.
- **Never infer from the order spec (VW 2022–23).** Owner confirmation, or a VIN/equipment-code lookup, is the only reliable test. A /learn line could explain how to check (e.g. the Leaf NZ guide's "grey pipes left of the inverter cover" tip, 🟡).

**Licence note:** each fact above is a single attribute cited to its URL, and the notes are our own paraphrases. No table was copied wholesale. Maker price lists and press releases are cited for facts only. The meinauto.de, ev-supply.de and Auto Bild pages are commercial editorial: cite, don't copy.

## 4. Ready-to-import table

`heat_pump` ∈ standard | option | none | not_disclosed. All rows retrieved 2026-11-15. `confidence`: high = 🟢, medium = 🟡, low = 🔴. `model_year_to` empty = still on sale / open.

```csv
variant_slug_hint,model_year_from,model_year_to,market,heat_pump,source_url,retrieved_at,confidence
tesla-model-3-gen1,2019,2020,ALL,none,https://insideevs.com/features/458189/2021-tesla-model-3-heat-pump-test-vs-2019-model/,2026-11-15,medium
tesla-model-3-gen1,2021,2023,ALL,standard,https://insideevs.com/features/458189/2021-tesla-model-3-heat-pump-test-vs-2019-model/,2026-11-15,medium
tesla-model-3-highland,2024,,ALL,not_disclosed,,2026-11-15,low
tesla-model-y-gen1,2021,2024,ALL,standard,https://www.discoverev.co.uk/ev-reviews/tesla-model-3-long-range-2021-review,2026-11-15,medium
tesla-model-y-juniper,2025,,DE,standard,https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html,2026-11-15,medium
tesla-model-s-gen1,2013,2016,ALL,not_disclosed,https://recharged.com/articles/which-evs-have-heat-pump/,2026-11-15,low
tesla-model-s-facelift,2016,2021,ALL,not_disclosed,https://recharged.com/articles/which-evs-have-heat-pump/,2026-11-15,low
tesla-model-s-palladium,2022,,ALL,not_disclosed,https://recharged.com/articles/which-evs-have-heat-pump/,2026-11-15,low
renault-zoe-ph1,2013,2019,ALL,standard,https://www.greenmotor.co.uk/2012/03/renault-zoe-ze-unmasked-keenly-priced.html,2026-11-15,medium
renault-zoe-ph2,2019,2024,DE,standard,https://professional.auto-motor-und-sport.de/static-download/news/1775221/pl_zoe_0919.pdf,2026-11-15,medium
renault-zoe-ph2,2022,2022,GB,standard,https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/car-ebrochures/ZOE-eBrochure.pdf,2026-11-15,medium
renault-zoe-ph2,2024,2024,CH,standard,https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Neuer_ZOE_PL_f.pdf,2026-11-15,high
renault-megane-e-tech-gen1,2025,,DE,standard,https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html,2026-11-15,medium
nissan-leaf-ze0,2011,2012,GB,none,https://nissaninsider.co.uk/buyers-guide-choosing-a-used-nissan-leaf/,2026-11-15,medium
nissan-leaf-ze0,2013,2017,GB,not_disclosed,https://nissaninsider.co.uk/three-trim-levels-and-new-pricing-structure-for-next-generation-leaf/,2026-11-15,medium
nissan-leaf-ze1,2018,2025,ALL,not_disclosed,https://www.whatcar.com/news/promoted-conquer-the-cold-with-the-new-nissan-leaf/n18295,2026-11-15,low
nissan-leaf-gen3,2025,,ALL,not_disclosed,,2026-11-15,low
volkswagen-id3-gen1,2020,2023,EU,option,https://volkswagen.ie/en/electric-cars/software-and-technology/id-technology/heat-pump.html,2026-11-15,high
volkswagen-id3-gen1,2024,,DE,option,https://www.volkswagen.at/id3-neo/id3-neo/waermepumpe,2026-11-15,high
volkswagen-id4-gen1,2021,,EU,option,https://volkswagen.ie/en/electric-cars/software-and-technology/id-technology/heat-pump.html,2026-11-15,high
volkswagen-id5-gen1,2022,,EU,option,https://volkswagen.ie/en/electric-cars/software-and-technology/id-technology/heat-pump.html,2026-11-15,high
skoda-enyaq-gen1,2023,2023,GB,option,https://www.skoda.co.uk/news/details/skoda-announces-raft-of-updates-and-enhancments-for-enyaq-iv,2026-11-15,high
skoda-enyaq-gen1,2020,,DE,option,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
cupra-born-gen1,2021,2025,EU,not_disclosed,https://www.cupraofficial.it/content/dam/public/cupra-website/generic/pdf/cupra-born-june-2024.pdf,2026-11-15,low
cupra-born-gen1,2026,2026,DE,option,https://www.ev-supply.de/blogs/cupra-born-elektroauto-news/cupra-born-150-kw-59-kwh-my26-warmepumpe,2026-11-15,medium
hyundai-kona-electric-os,2018,2023,DE,option,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
hyundai-kona-electric-os,2018,2023,GB,not_disclosed,https://www.businesscar.co.uk/news/2021/mar-8-14/specs-and-prices-revealed-for-facelifted-hyundai-kona-electric,2026-11-15,low
hyundai-kona-electric-sx2,2023,,ALL,not_disclosed,,2026-11-15,low
hyundai-ioniq-5-gen1,2021,,DE,option,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
kia-ev6-gen1,2021,,DE,option,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
kia-niro-ev-de,2018,2022,ALL,not_disclosed,https://www.zapmap.com/news/kia-adds-e-niro-39-kwh-and-faster-charging-to-range,2026-11-15,low
peugeot-e-208-p21,2019,2021,ALL,not_disclosed,https://www.caradisiac.com/les-options-179574.htm,2026-11-15,low
peugeot-e-208-p21,2022,,DE,standard,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,low
peugeot-e-208-p21,2025,,GB,standard,https://www.media.stellantis.com/uk-en/peugeot/press/peugeot-announces-new-range-topping-gt-premium-trim-and-powertrain-enhancements-for-208-2008,2026-11-15,high
peugeot-e-2008-p24,2020,2021,ALL,not_disclosed,,2026-11-15,low
peugeot-e-2008-p24,2025,,GB,standard,https://www.media.stellantis.com/uk-en/peugeot/press/peugeot-announces-new-range-topping-gt-premium-trim-and-powertrain-enhancements-for-208-2008,2026-11-15,high
opel-corsa-e-f,2020,,ALL,not_disclosed,,2026-11-15,low
opel-mokka-e-gen1,2021,,ALL,not_disclosed,,2026-11-15,low
fiat-500e-332,2020,,GB,not_disclosed,https://www.fiat.co.uk/content/dam/fiat2023/uk/price-and-specification-guides/new500/fiat-500e.pdf,2026-11-15,low
dacia-spring-gen1,2021,2024,ALL,not_disclosed,,2026-11-15,low
dacia-spring-gen1,2025,,DE,none,https://www.ev-supply.de/blogs/elektroauto-news/dacia-spring-electric-100-warmepumpe-alle-details,2026-11-15,medium
mg-mg4-gen1,2022,,GB,not_disclosed,https://mgevs.com/goto/post?id=136681,2026-11-15,low
mg-mg4-gen1,2022,,EU,not_disclosed,https://mgevs.com/goto/post?id=136681,2026-11-15,low
polestar-2-gen1,2020,2024,ALL,not_disclosed,,2026-11-15,low
polestar-2-gen1,2025,2025,DE,option,https://www.ev-supply.de/blogs/elektroauto-news/polestar-2-standard-range-single-motor-warmepumpe-alle-details,2026-11-15,medium
audi-e-tron-ge,2019,2022,DE,not_disclosed,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,low
bmw-i4-g26,2021,,DE,standard,https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html,2026-11-15,medium
mercedes-eqa-h243,2021,,DE,standard,https://www.autobild.de/artikel/waermepumpe-im-elektroauto-reichweite-22410821.html,2026-11-15,medium
mercedes-eqc-n293,2019,2023,DE,standard,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
mini-cooper-se-f56,2020,2023,DE,standard,https://www.meinauto.de/lp/elektroautos-mit-waermepumpe,2026-11-15,medium
volkswagen-e-up-gen1,2020,2023,ALL,not_disclosed,https://www.adac.de/rund-ums-fahrzeug/elektromobilitaet/elektroauto/heizung-elektroauto/,2026-11-15,low
bmw-i3-i01,2013,2022,ALL,not_disclosed,,2026-11-15,low
volkswagen-e-golf-mk7,2014,2017,ALL,not_disclosed,,2026-11-15,low
volkswagen-e-golf-mk75,2017,2020,ALL,not_disclosed,,2026-11-15,low
hyundai-ioniq-electric-gen1,2016,2022,ALL,not_disclosed,,2026-11-15,low
hyundai-ioniq-6-gen1,2022,,ALL,not_disclosed,,2026-11-15,low
kia-soul-ev-ps,2014,2019,ALL,not_disclosed,,2026-11-15,low
kia-soul-ev-sk3,2019,2022,ALL,not_disclosed,,2026-11-15,low
kia-niro-ev-sg2,2022,,ALL,not_disclosed,,2026-11-15,low
audi-e-tron-q8,2023,2025,ALL,not_disclosed,,2026-11-15,low
audi-q4-e-tron-gen1,2021,,ALL,not_disclosed,,2026-11-15,low
jaguar-i-pace-x590,2018,2024,ALL,not_disclosed,,2026-11-15,low
volvo-xc40-recharge-gen1,2020,2023,ALL,not_disclosed,,2026-11-15,low
volvo-xc40-recharge-ex40,2024,,ALL,not_disclosed,,2026-11-15,low
ford-mustang-mach-e-gen1,2021,,ALL,not_disclosed,,2026-11-15,low
citroen-e-c4-c41,2020,,ALL,not_disclosed,,2026-11-15,low
byd-atto-3-gen1,2022,,ALL,not_disclosed,,2026-11-15,low
honda-e-gen1,2020,2024,ALL,not_disclosed,,2026-11-15,low
smart-eq-fortwo-453,2017,2024,ALL,not_disclosed,,2026-11-15,low
mg-zs-ev-gen1,2019,,ALL,not_disclosed,,2026-11-15,low
fiat-500e-312,2013,2019,ALL,not_disclosed,,2026-11-15,low
mini-cooper-se-j01,2024,,ALL,not_disclosed,,2026-11-15,low
```

Import notes: `opel-mokka-e-gen1`, `volkswagen-id5-gen1` and `volkswagen-e-up-gen1` are new slug hints that are not yet in `models.yaml`. Rows with an empty `source_url` are placeholders that say "not researched" and must not be shown as facts. `market` uses ISO codes (GB = UK), `ALL` and `EU`. If the seed schema prefers `UK`, map it on import.
