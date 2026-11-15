# R-25 Bidirectional: verifying the 🔴 items from R-01 (task T-042)

Researched 2026-11-15 by a WS3 research agent. Time-boxed (~1 h). Every link below was opened on 2026-11-15 unless it is listed under "Blocked / not opened". Confidence: 🟢 maker, standards body or other primary source · 🟡 one reputable secondary source, or reasoned · 🔴 unsure.

## Answer

None of the five 🔴 items can be published as R-01 states them. Two need correcting. **Ford Explorer/Capri (EU)**: V2H is confirmed by Ford for DE/AT/CH (E3/DC). V2G is not "unconfirmed" any more. An Octopus + Ford V2G offer for Germany was reported for summer 2026, for model year 2026.75 and later with an Ambibox wallbox (🟡, one secondary source). **Bidirectional over NACS/J3400**: SAE says the J3400 Recommended Practice "adopts V2G and backup power requirements". So "J3400 has no bidirectional support" is wrong. In practice the only live bidirectional products on NACS-port cars are Tesla's own (Cybertruck V2H + Texas V2G pilot, and Model 3/Y V2H **for cars ordered from 1 Oct 2026**, not "built from"). **Kia EV2**: Kia's own page lists V2G as a feature. "Standard on all trims" and "ISO 15118-20 ready" were not found. **BYD Dolphin**: V2G is offered only in the UK, as the Octopus/Zaptec "Power Pack" lease bundle (June 2025). Whether a normal Dolphin can do V2G outside that bundle was not found. BYD says V2G will come to DACH but gives no date. **Older Teslas at third-party J3400 DC sites**: the rule is not a model year. It depends on whether the car shows "CCS and 3rd-party NACS DC charging: Enabled". Cars showing "Not Installed" need Tesla's retrofit (🟡). **Car-side ISO 15118-20**: no maker document opened today states it, except a Hyundai IONIQ 9 V2G test in Australia reported as ISO 15118-20 (🟡, dealer/press, quoting Hyundai Australia). VW states its bidirectional charging is based on **ISO 15118-2**. Every other maker: `not_disclosed`.

## 1. Kia EV2 V2G

- 🟢 Kia UK's EV2 Brussels page lists "bidirectional charging" and "Vehicle-to-Grid (V2G)" among the EV technologies, next to V2L and Plug & Charge. Batteries 42.2 and 61 kWh. Standard range first (production early 2026), long range and GT Line later in 2026. UK pricing and dates are not announced. Source: https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/
- 🟡 The EV Report repeats this ("V2L and V2G functionality enables external power delivery") and gives no markets. https://theevreport.com/kia-ev2-compact-electric-suv-debuts-in-brussels
- 🔴→ **not_found:** "V2G standard on all trims"; any market where an EV2 V2G service is live; V2H; ISO 15118-20. Hyundai Motor Group's V2X release (28 Nov 2025) names only EV9, IONIQ 9 (V2G, NL and Korea) and EV6 (US V2H). EV2 is not mentioned. https://www.hyundaimotorgroup.com/en/news/hyundai-motor-group-expands-ev-energy-services-with-vehicle-to-grid-and-vehicle-to-home
- **Data:** mode `v2g`, status `announced` (hardware feature claimed), no `market_status` live anywhere, `iso15118_20_support` = `not_disclosed`.

## 2. BYD Dolphin bidirectional bundle

- 🟡 UK only: Octopus Energy + BYD "Power Pack" lease bundle (car + bidirectional Zaptec Pro charger + tariff), launched 23/24 June 2025, just under £300/month. Conditions: plug in ≥20×/month for ≥12 h; not available to people who already export; DNO permission needed (up to 12 weeks). electrive: "The BYD Dolphin is the first vehicle in the UK market with native V2G compatibility." https://www.electrive.com/2025/06/24/octopus-energy-and-byd-launch-uks-first-v2g-bundle
- 🟢 Zaptec (a partner, primary for its own role): "UK's first commercial vehicle-to-grid (V2G) offering", "Zaptec Pro charger with bidirectional capability", deployments by waiting list, "potential to … expand across the UK and Europe". It does not name the car model. https://www.zaptec.com/en-uk/info-hub/inside-zaptec/zaptec-joins-octopus-and-byd-to-enable-uks-first-bidirectional-charging-bundle
- 🟡 Route reasoned as **AC (on-board)**: the Zaptec Pro is an AC wallbox, so the inverter must sit in the car. No source opened today says "AC" outright. Verify before showing "no expensive box needed".
- 🟡 BYD DACH (MD MariaGrazia Davino, interview 22 Sep 2025): "V2G wird kommen", DACH "will be next", no date, no model named. https://www.elektroauto-news.net/news/byd-mariagrazia-davino-europa-strategie
- **not_found:** whether non-bundle (bought or used) Dolphins can do V2G; which Dolphin battery/trim; any BYD-issued press release on the bundle (the Octopus page was blocked, see below).
- **Data:** v2g, UK `live` with caveats `tariff_required`, `maker_box_only` (bundle charger) and a new "bundle/lease only" condition (see §8); DE/AT/CH `announced`; other markets `not_offered`.

## 3. Ford Explorer EV (Europe, MEB) V2G / V2H

- 🟢 **V2H confirmed by Ford** (27 Jan 2025): Explorer and Capri "are approved for bidirectional DC charging". This needs PV plus an E3/DC home power station with EDISON V2H, installed by E3/DC partners. Germany, Austria, Switzerland only. No battery or software limits stated. https://at.ford.com/us/en/home/news-media/news/2025/1/how-ford-explorer-and-capri-customers-can-use-their-vehicles-as-.html
- 🟡 **V2G announced for Germany** (published 12 Feb 2026): Octopus Energy + Ford, private customers, launch summer 2026. Ambibox bidirectional wallbox bought separately. "Full range of functions requires model year 2026.75 or later"; customers should check compatibility with Ford. €30/month bonus at ≥300 h plugged in. https://www.emove360.com/ford-and-octopus-energy-launch-bidirectional-charging-up-to-16000-kilometers-possible-free-of-charge/ (secondary; Ford/Octopus primary not opened, live status in Nov 2026 not verified).
- 🟢 The Mobility House lists "select Ford models, depending on software and battery configuration" as supported by its ChargeLine BiDi DC box. https://www.mobilityhouse.com/int_en/chargeline-bidi
- **Data:** v2h DE/AT/CH `live` (route `dc_offboard`, equipment E3/DC EDISON V2H, caveat `needs_dc_box`). v2g DE `announced` (until a Ford/Octopus page confirms it is live), caveats `needs_dc_box`, `tariff_required`, `build_date_from` (param: MY 2026.75; exact build date not disclosed). Used pre-MY2026.75 cars: V2G `not_disclosed`.

## 4. Older Teslas at J3400 / NACS sites

- 🟡 Third-party NACS DC chargers need the car to support the "CCS-style" handshake. Owners check *Controls › Software › Additional Vehicle Information*: "CCS and 3rd-party NACS DC charging: Enabled / Not Installed". "Vehicles manufactured before 2022 may lack the communication handshake required." Tesla offers a hardware retrofit that includes a CCS1 adapter. Source: Hypercharge (charger vendor), updated 24 Jul 2025. https://hypercharge.com/blog/using-third-party-nacs-connectors-on-tesla-vehicles/
- 🟡 Retrofit: US$450 including the US$175 CCS1 adapter. At launch (Feb 2023) it was for Model S/X, with 3/Y to follow. Not CCS-ready: "especially those before 2020". https://www.notateslaapp.com/NEWS/1232/TESLA-ANNOUNCES-PRICING-FOR-CCS-RETROFITS-ALLOWING-YOU-TO-CHARGE-AT-MORE-STATIONS
- 🟡 Superchargers: all Teslas can use them (native). Non-Teslas can use **only V3/V4** Superchargers, not V2, and only with automaker-supplied adapters. https://cleantechnica.com/2025/02/28/qa-regarding-tesla-supercharger-access-for-non-teslas/
- **Verdict on R-01 claim "≤2021 Teslas aren't compatible with third-party J3400 stations": partial.** It depends on the car's "CCS enabled" hardware, not a fixed year, and it can be retrofitted. Store it as a per-car condition, not by model year.
- **Data:** `ChargingPort.supercharger_access` = `native` for all Teslas. Add a third-party-DC condition: `ccs_hw_required` (new caveat, see §8) with tooltip "Check 'CCS and 3rd-party NACS DC charging: Enabled'; retrofit available."

## 5. Bidirectional power over NACS / J3400

- 🟢 SAE J3400 Recommended Practice released Oct 2024. SAE's Dr Rodney McGee: the RP "adopts V2G and backup power requirements" and moves to digital car-charger communication. Source: SAE's own Mobility Engineering magazine. https://www.mobilityengineeringtech.com/component/content/article/51809-sae-j3400-helps-define-the-future-of-ev-charging-in-north-america ; also ECM, 10 Oct 2024: https://www.ecmweb.com/electric-vehicles/article/55234527/sae-international-releases-j3400-ev-coupler-recommended-practice
- 🟡 SAE J3400/2 (reported 16 Jun 2025): 1,000 V coupler, "lays the groundwork for vehicle-to-grid and vehicle-to-home power transfer". https://eepower.com/market-insights/sae-j3400-2-sets-the-stage-for-quicker-smarter-nacs-charging/ . SAE J3400/1 (Apr 2025) covers adapter safety and is not bidirectional. https://saemobilus.sae.org/standards/j34001_202504-electric-vehicle-charging-adapter-safety-oem-qualified-device-designation (search listing only).
- 🟢 CharIN Testival North America (Detroit, 2–4 Jun 2026; Ford, GM, Nissan, Rivian, PACCAR, Bosch): ISO 15118-20 bidirectional power transfer (BPT) was tested, and 6 of the EVs had NACS inlets. The release does **not** say BPT was run over a NACS connector. https://www.charin.global/news/charin-testival-north-america-2026-detroit-press-release/
- 🟡 **Tesla Powershare** (Electrek, citing Tesla Energy and Tesla's Powershare page):
  - Cybertruck: V2H with Powershare Gateway + Universal Wall Connector. **V2G "Powershare Grid Support"** in Texas (CenterPoint, Oncor), invitation only, from Feb 2026; California next. https://electrek.co/2026/02/11/tesla-launches-cybertruck-v2g-program-texas-earning-money-truck-battery-pack/
  - Model 3/Y: V2H home backup with **Powerwall 3**, guaranteed for cars **ordered on or after 1 Oct 2026** in the US and Puerto Rico. Older 3/Y: "some, but not all" (PCS2 Lite inverter); check "Powershare Support" in Additional Vehicle Information. No Grid Support (no V2G) for 3/Y. Max 11.52 kW continuous. Not Model S/X. Canada: Cybertruck only. https://electrek.co/2026/10/06/tesla-powershare-home-backup-model-3-model-y-powerwall-3/
  - 🟡 Reasoned: these cars have NACS ports and discharge via a Wall Connector, so the power flows through the NACS inlet using a proprietary Tesla system. Not ISO 15118-20 as far as found.
- **Verdict on R-01 claim "J3400 lacks native bidirectional support": denied** for the standard. But no non-Tesla bidirectional product over a J3400 connector was found live. Ford's US V2H still uses the F-150 Lightning's CCS1 route (R-01).
- **Correction to R-01 §4:** Tesla Model 3/Y V2H is tied to the **order date (≥ 1 Oct 2026), US + PR**, not "built in the US from 1 Oct 2026". Older cars may qualify (check the car).

## 6. Car-side ISO 15118-20 per maker (official statements only)

| Maker | Finding | Status |
|---|---|---|
| VW group (MEB) | VW press (12 Jun 2023): "Bidirectional charging is based on ISO standard 15118-2". No -20 statement found. ChargeLine BiDi box supports -20/-2/DIN on its side (box, not car). | `not_disclosed` for -20; protocol `iso15118_2_ext` 🟢 |
| Hyundai / Kia | IONIQ 9 did Australia's first V2G discharge "using ISO 15118-20" (Jun 2026; dealer blog and press quoting Hyundai Australia CEO). HMG global release: no -20 mention. Kia EV2: not found. | IONIQ 9: `yes` 🟡 (needs a Hyundai doc); others `not_disclosed` |
| Renault | Mobilize/Renault V2G pages opened: no ISO 15118 part named. | `not_disclosed` |
| BMW | iX3/E.ON newsroom page blocked; nothing found elsewhere from BMW. | `not_disclosed` |
| Mercedes | Mercedes/Mobility House release (9 Sep 2025): no ISO 15118 mention. | `not_disclosed` |
| Volvo / Polestar | Volvo EX30 V2L press (1 Sep 2026): V2L via adapter, Plug & Charge in Europe from MY2026; no -20 mention. The R-01 claim "EX30 -20 ready" is not supported. Polestar: nothing found. | `not_disclosed` |
| Tesla | Nothing found; bidirectional is proprietary Powershare. | `not_disclosed` |
| BYD | Nothing found. | `not_disclosed` |
| Ford | Took part in CharIN NA 2026 where -20 BPT was tested; no vehicle-specific statement. | `not_disclosed` |
| GM | Same as Ford. | `not_disclosed` |
| Nissan | CHAdeMO cars use the CHAdeMO protocol (no ISO 15118). Leaf gen 3 AC V2G: no -20 statement found. | gen 1–2: `no` 🟡 (protocol `chademo`); gen 3: `not_disclosed` |

## 7. Other 🔴 in R-01 / T-042

- "Volvo EX30 and Kia EV2 marketed as -20 ready" → **not_found** in maker documents opened today. Keep `not_disclosed`.
- Renault 5 "top two motor versions" (🟡 in R-01) was not re-checked (out of time).

## 8. Schema notes for WS0 (proposals, not edits)

- Proposed caveat `bundle_only` "Only as part of a lease/energy bundle" (BYD Dolphin UK).
- Proposed caveat `ccs_hw_required` "Older Teslas: check 'CCS and 3rd-party NACS DC charging' is Enabled; retrofit available".
- Proposed caveat `order_date_from` (Tesla uses order date, not build date). Alternatively reuse `build_date_from` with a note.

## 9. Blocked / not opened (permission request timed out or site error)

octopus.energy/power-pack · en.wikipedia.org/wiki/SAE_J3400 · tesla.com/support/energy/powershare · newsroom.bmwgroup.com (iX3/E.ON) · mmx.prnewswire.com Kia EV2 press PDF · webstore.ansi.org SAE J3400-2025 (site error) · thedriven.io (redirect loop). These are the primary pages to retry for 🟢 upgrades.

## 10. Per-claim table

| claim | status | market | source_url | retrieved_at | confidence |
|---|---|---|---|---|---|
| Kia EV2 has V2G / bidirectional charging | confirmed (feature listed) | EU/UK (no service) | https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/ | 2026-11-15 | 🟢 |
| Kia EV2 V2G standard on all trims | not_found | — | https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/ | 2026-11-15 | 🔴 |
| Kia EV2 ISO 15118-20 | not_found | — | https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/ | 2026-11-15 | 🔴 |
| BYD Dolphin V2G via Octopus bundle | confirmed | UK | https://www.electrive.com/2025/06/24/octopus-energy-and-byd-launch-uks-first-v2g-bundle | 2026-11-15 | 🟡 |
| Bundle charger is Zaptec Pro, live, waitlist | confirmed | UK | https://www.zaptec.com/en-uk/info-hub/inside-zaptec/zaptec-joins-octopus-and-byd-to-enable-uks-first-bidirectional-charging-bundle | 2026-11-15 | 🟢 |
| Dolphin V2G only inside bundle | not_found | UK | https://www.electrive.com/2025/06/24/octopus-energy-and-byd-launch-uks-first-v2g-bundle | 2026-11-15 | 🔴 |
| BYD V2G coming to DACH (no date) | partial | DE/AT/CH | https://www.elektroauto-news.net/news/byd-mariagrazia-davino-europa-strategie | 2026-11-15 | 🟡 |
| Ford Explorer/Capri V2H (DC, E3/DC) | confirmed | DE/AT/CH | https://at.ford.com/us/en/home/news-media/news/2025/1/how-ford-explorer-and-capri-customers-can-use-their-vehicles-as-.html | 2026-11-15 | 🟢 |
| Ford Explorer/Capri V2G (Octopus, Ambibox, MY2026.75+) | partial (announced) | DE | https://www.emove360.com/ford-and-octopus-energy-launch-bidirectional-charging-up-to-16000-kilometers-possible-free-of-charge/ | 2026-11-15 | 🟡 |
| ≤2021 Teslas incompatible with 3rd-party J3400 DC | partial (depends on CCS hw; retrofit) | US/CA | https://hypercharge.com/blog/using-third-party-nacs-connectors-on-tesla-vehicles/ | 2026-11-15 | 🟡 |
| Tesla CCS retrofit US$450 incl. adapter | confirmed (2023) | US | https://www.notateslaapp.com/NEWS/1232/TESLA-ANNOUNCES-PRICING-FOR-CCS-RETROFITS-ALLOWING-YOU-TO-CHARGE-AT-MORE-STATIONS | 2026-11-15 | 🟡 |
| Non-Teslas only at V3/V4 Superchargers | confirmed | US | https://cleantechnica.com/2025/02/28/qa-regarding-tesla-supercharger-access-for-non-teslas/ | 2026-11-15 | 🟡 |
| J3400 lacks bidirectional support | denied (RP adopts V2G + backup power) | NA | https://www.mobilityengineeringtech.com/component/content/article/51809-sae-j3400-helps-define-the-future-of-ev-charging-in-north-america | 2026-11-15 | 🟢 |
| J3400/2 lays groundwork for V2G/V2H | confirmed | NA | https://eepower.com/market-insights/sae-j3400-2-sets-the-stage-for-quicker-smarter-nacs-charging/ | 2026-11-15 | 🟡 |
| ISO 15118-20 BPT tested on NACS-inlet cars | partial (BPT tested; not stated over NACS) | NA | https://www.charin.global/news/charin-testival-north-america-2026-detroit-press-release/ | 2026-11-15 | 🟢 |
| Cybertruck V2G (Powershare Grid Support) | confirmed (pilot, invite only) | US-TX | https://electrek.co/2026/02/11/tesla-launches-cybertruck-v2g-program-texas-earning-money-truck-battery-pack/ | 2026-11-15 | 🟡 |
| Model 3/Y V2H with Powerwall 3, ordered ≥2026-10-01 | confirmed | US, PR | https://electrek.co/2026/10/06/tesla-powershare-home-backup-model-3-model-y-powerwall-3/ | 2026-11-15 | 🟡 |
| VW MEB bidi based on ISO 15118-2 | confirmed | EU | https://www.volkswagen-newsroom.com/en/press-releases/cleverly-manage-your-own-electricity-first-id-models-support-bidirectional-charging-17949 | 2026-11-15 | 🟢 |
| Hyundai IONIQ 9 ISO 15118-20 V2G | confirmed (test) | AU | https://tynan.com.au/blog/hyundai-achieves-australia-s-first-standards-compliant-vehicle-to-grid-milestone | 2026-11-15 | 🟡 |
| Volvo EX30 ISO 15118-20 | not_found | — | https://www.volvocars.com/intl/media/press-releases/C35780FCBCCFC01F/ | 2026-11-15 | 🔴 |
| Mercedes car-side ISO 15118-20 | not_found | — | https://www.mobilityhouse.com/usa_en/our-company/newsroom/article/mercedes-benz-bidirectional-charing-home | 2026-11-15 | 🔴 |
| Renault car-side ISO 15118-20 | not_found | — | https://www.automotiveworld.com/news/mobilize-v2g-where-the-future-electric-renault-5-becomes-a-source-of-energy/ | 2026-11-15 | 🔴 |
| BMW, Polestar, Tesla, BYD, Ford, GM, Nissan gen 3 car-side -20 | not_found | — | (none found) | 2026-11-15 | 🔴 |

## 11. Ready-to-import rows (field names from docs/spec/bidirectional-and-connectors.md §3)

`variant_or_platform_id` values are proposed slugs; WS1 should map them to catalogue IDs. `source_licence`: facts only, taken from press or editorial text (no tables copied).

| entity | variant_or_platform_id | field | value | market | status | caveats | source_url | retrieved_at | confidence |
|---|---|---|---|---|---|---|---|---|---|
| BidiCapability | kia-ev2 | mode | v2g | ALL | announced | — | https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/ | 2026-11-15 | 🟢 |
| Variant | kia-ev2 | iso15118_20_support | not_disclosed | ALL | — | — | https://www.kia.com/uk/about/news/kia-ev2-brussels-motor-show-2026/ | 2026-11-15 | 🔴 |
| BidiCapability | byd-dolphin | mode | v2g | GB | live | tariff_required; maker_box_only; bundle_only (proposed) | https://www.electrive.com/2025/06/24/octopus-energy-and-byd-launch-uks-first-v2g-bundle | 2026-11-15 | 🟡 |
| BidiCapability | byd-dolphin | route | ac_onboard | GB | — | verify | https://www.zaptec.com/en-uk/info-hub/inside-zaptec/zaptec-joins-octopus-and-byd-to-enable-uks-first-bidirectional-charging-bundle | 2026-11-15 | 🟡 |
| BidiCapability | byd-dolphin | mode | v2g | DE,AT,CH | announced | — | https://www.elektroauto-news.net/news/byd-mariagrazia-davino-europa-strategie | 2026-11-15 | 🟡 |
| BidiCapability | ford-explorer-ev-meb; ford-capri-meb | mode | v2h | DE,AT,CH | live | needs_dc_box (equipment: e3dc-edison-v2h) | https://at.ford.com/us/en/home/news-media/news/2025/1/how-ford-explorer-and-capri-customers-can-use-their-vehicles-as-.html | 2026-11-15 | 🟢 |
| BidiCapability | ford-explorer-ev-meb; ford-capri-meb | route | dc_offboard | DE,AT,CH | — | — | https://at.ford.com/us/en/home/news-media/news/2025/1/how-ford-explorer-and-capri-customers-can-use-their-vehicles-as-.html | 2026-11-15 | 🟢 |
| BidiCapability | ford-explorer-ev-meb; ford-capri-meb | mode | v2g | DE | announced | needs_dc_box; tariff_required; build_date_from (param: MY2026.75) | https://www.emove360.com/ford-and-octopus-energy-launch-bidirectional-charging-up-to-16000-kilometers-possible-free-of-charge/ | 2026-11-15 | 🟡 |
| BidiCapability | vw-meb | protocol | iso15118_2_ext | EU | — | — | https://www.volkswagen-newsroom.com/en/press-releases/cleverly-manage-your-own-electricity-first-id-models-support-bidirectional-charging-17949 | 2026-11-15 | 🟢 |
| Variant | vw-meb | iso15118_20_support | not_disclosed | EU | — | — | https://www.volkswagen-newsroom.com/en/press-releases/cleverly-manage-your-own-electricity-first-id-models-support-bidirectional-charging-17949 | 2026-11-15 | 🟢 |
| Variant | hyundai-ioniq-9 | iso15118_20_support | yes | AU | pilot | — | https://tynan.com.au/blog/hyundai-achieves-australia-s-first-standards-compliant-vehicle-to-grid-milestone | 2026-11-15 | 🟡 |
| Variant | volvo-ex30 | iso15118_20_support | not_disclosed | EU | — | — | https://www.volvocars.com/intl/media/press-releases/C35780FCBCCFC01F/ | 2026-11-15 | 🔴 |
| BidiCapability | tesla-cybertruck | mode | v2h | US | live | home_battery_required or Powershare Gateway | https://electrek.co/2026/02/11/tesla-launches-cybertruck-v2g-program-texas-earning-money-truck-battery-pack/ | 2026-11-15 | 🟡 |
| BidiCapability | tesla-cybertruck | mode | v2g | US-TX | pilot | tariff_required (Tesla Electric); maker_box_only | https://electrek.co/2026/02/11/tesla-launches-cybertruck-v2g-program-texas-earning-money-truck-battery-pack/ | 2026-11-15 | 🟡 |
| BidiCapability | tesla-model-3; tesla-model-y | mode | v2h | US,PR | live | home_battery_required (Powerwall 3); order_date_from 2026-10-01 (proposed); older cars: check "Powershare Support" | https://electrek.co/2026/10/06/tesla-powershare-home-backup-model-3-model-y-powerwall-3/ | 2026-11-15 | 🟡 |
| BidiCapability | tesla-model-3; tesla-model-y | protocol | proprietary | US | — | — | https://electrek.co/2026/10/06/tesla-powershare-home-backup-model-3-model-y-powerwall-3/ | 2026-11-15 | 🟡 |
| BidiCapability | tesla-model-3; tesla-model-y | mode | v2g | US | not_offered | — | https://electrek.co/2026/10/06/tesla-powershare-home-backup-model-3-model-y-powerwall-3/ | 2026-11-15 | 🟡 |
| ChargingPort | tesla-all (US) | supercharger_access | native | US,CA | — | third-party J3400 DC: ccs_hw_required (proposed) | https://hypercharge.com/blog/using-third-party-nacs-connectors-on-tesla-vehicles/ | 2026-11-15 | 🟡 |
| Variant | nissan-leaf-gen1-2 | iso15118_20_support | no | ALL | — | chademo_legacy | (protocol by definition: CHAdeMO) | 2026-11-15 | 🟡 |
| Variant | renault, bmw, mercedes, polestar, tesla, byd, ford, gm, nissan-leaf-gen3 (all) | iso15118_20_support | not_disclosed | ALL | — | — | (none found) | 2026-11-15 | 🔴 |
