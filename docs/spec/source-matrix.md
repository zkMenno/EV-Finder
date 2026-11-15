<!-- Mirror of the claude.ai spec doc, tab "Source matrix" (rev 2), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Source matrix: every data point, its sources and fallbacks

The rule: every data point has one or two primary sources and as many fallbacks as exist. The pipeline merges them into one value per variant with a confidence level, and the UI shows how many sources agree ("3 sources agree", "single source", "estimated"). 🟢 = source and fields confirmed in research, 🟡 = believed right, verify the exact fields when building the adapter, 🔴 = no good open source; manual entry from the maker's own documents, with a citation.

## How the matrix runs in the code

- **`data/sources.yaml`**: one entry per source: id, owner, licence, access method (API, bulk file, manual), refresh cadence, terms notes, status (active, waiting for permission, blocked).
- **`data/field_sources.yaml`**: one entry per field: primary sources (1–2), fallbacks in order, the agreement tolerance (for example battery kWh ±2%, length ±10 mm, price ±1%), and how to merge (priority, median, newest).
- **Every value is a Fact** with its source, date and conditions, so the merge can be rerun when a source changes.
- **Coverage report each release:** for each field, the share of variants with two or more agreeing sources, one source, or only an estimate. Target: 80% of the top 40 used models with two or more sources on every headline field. This report shows in the staff dashboard.
- **Conflicts** outside tolerance go to the review queue, never silently averaged.
- **Licence gate:** a source without a named licence or written permission cannot reach a public release. Its facts can still be used internally for cross-checks.

## Identity and core specs

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| Make, model, variant names, model years | EEA CO₂ monitoring dataset (type-approval names) 🟡; RDW type approval (TGK) datasets, CC0 🟢 | Open EV Data (MIT + attribution) 🟢; Wikidata (CC0) 🟡; maker press kits 🔴 |
| Generation boundaries and facelifts | Maker press releases 🔴; Wikidata/Wikipedia model histories 🟡 | RDW first-registration years per type approval 🟢; staff decision |
| Body type, segment, seats | RDW (body, seats), CC0 🟢 | Euro NCAP class 🟡; maker specs 🔴 |
| Power (kW), drivetrain | EEA (engine power) 🟡; RDW 🟢 | Open EV Data 🟢; fueleconomy.gov (US) 🟢 |
| Mass | EEA 🟡; RDW (empty mass) 🟢 | Maker specs 🔴 |
| Length, width, height, wheelbase | RDW (length, width, wheelbase) 🟢 | Euro NCAP datasheets 🟡; Wikidata 🟡; maker specs 🔴 |
| Towing (braked/unbraked) | RDW (max towed mass), CC0 🟢 | Maker specs 🔴 |
| Boot and frunk volume (litres) | Maker specs 🔴 | Björn Nyland's box tests (real luggage, pending permission) 🟡; owner reports later |
| 0–100 km/h, top speed | Maker specs 🔴 | Wikidata 🟡; fueleconomy.gov (US) 🟡 |
| Heat pump, V2L/V2G, tow bar option | Maker specs and price lists 🔴 | Open EV Data 🟡; owner reports later |
| Images | Wikimedia Commons (per-image CC licence) 🟡 | Maker press sites (media terms) 🟡; neutral silhouettes made by us |

## Battery and charging

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| Battery gross and usable kWh | Open EV Data (usable) 🟢; maker specs 🔴 | Björn Nyland measured usable 🟡; NAF/ADAC test reports 🟢 |
| Chemistry (NMC, LFP), voltage (400/800 V) | Maker specs 🔴 | Open EV Data 🟡; platform rules (same pack, same chemistry) |
| AC on-board charger (kW, phases) | Open EV Data 🟢 | Maker specs 🔴; Fastned pages 🟡 |
| Plug types | Open EV Data 🟢 | Fastned 🟢; maker specs |
| DC charge curve | Fastned curves (permission needed) 🟢; Open EV Data, minus default curves 🟢 | Björn Nyland curves 🟡; same platform and pack; generic curve shape (estimated) |
| Average kW and minutes 10–80% | NAF El Prix 🟢; ADAC 🟢 | Automobile Propre Supertests 🟢; derived from the curve; maker claim (labelled as a claim) |
| km added in 10/20 min | P3 Charging Index 🟢; ADAC 20-minute figure 🟢 | Derived: curve × motorway consumption |
| Winter charging time | NAF El Prix winter 🟢; ADAC winter stress test 🟢 | Summer time × brand cold factor (estimated) |

## Range and consumption

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| WLTP range and consumption | EEA (electric range, Wh/km) 🟡; RDW 🟢 | Maker specs; Open EV Data 🟢 |
| EPA range and consumption (US) | fueleconomy.gov API, public domain 🟢 | Maker US specs |
| Real range, summer mixed | Björn Nyland (pending permission) 🟡; NAF El Prix summer 🟢 | Edmunds (US) 🟢; real/WLTP ratio by brand × body × drivetrain |
| Real range, motorway 120 km/h | Björn Nyland 120 km/h tests 🟡; ADAC motorway figures 🟢 | InsideEVs/Out of Spec and Consumer Reports at 70 mph (113 km/h) 🟢; ratio model |
| Real range, winter | NAF El Prix winter 🟢; ADAC winter test 🟢 | Brand cold factor × summer real range |
| Real consumption | Spritmonitor owner logs 🟢; ADAC Ecotest 🟢 | Our owner data later; WLTP × ratio |

## Prices

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| New price, NL | RDW list price at registration (catalogusprijs), CC0 🟢 | Maker NL price lists 🔴 |
| New price, other countries | Maker price lists, monthly 🔴 | National incentive lists that publish prices 🟡; EV Database as a manual cross-check only |
| Used asking price ranges | Partner feeds (layer 1); our pre-filtered search sampling (layer 3) | Free price indices (layer 0) for trends; manual sample (layer 2) |
| Used price trend per country | Autotrader UK RPI, AutoScout24 AGPI, Indicata 🟢 | Recurrent (US), Clutch (CA), K Car (KR) 🟢 |
| Electricity prices (for cost per km) | Eurostat, CC BY 🟡 | Ofgem price cap (UK), EIA (US) 🟡 |
| Exchange rates | ECB reference rates 🟢 | — |

## Market and used availability

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| New registrations per model per country | National registries: RDW, KBA, DfT, SDES, FEBIAC, OFV 🟢 | EEA dataset (EU, yearly) 🟡; Ember (shares) 🟢; aggregator sites |
| Fleet on the road per model and year (used supply) | RDW fleet (CC0) 🟢; DfT VEH0160 🟢 | KBA fleet tables 🟡; SDES 🟡 |
| Ownership changes (used sales) | KBA ownership transfers 🟢; FEBIAC used BEV figures 🟢 | Otoshops (TR), K Car (KR) reports 🟢 |
| Listings available now | Partner feeds; sampling counts | Indicata stock and days-to-sell 🟢 |
| Emerging-market registrations | VAHAN, Thailand DLT, INEGI RAIAVL, ABVE, NZ MoT 🟢 | Ember 🟢 |

## Condition, reliability and safety

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| Battery health by age and km | Aviloo Certified EV Battery Report 🟢 | Recurrent, Generational 🟢; generic curve by chemistry (estimated) |
| Battery warranty | Maker warranty terms 🔴 | Industry default (8 years / 160,000 km) labelled "typical" |
| Common inspection defects by age | RDW inspections + defects, CC0 🟢 | DVSA MOT history (OGL) 🟢 | — |
| Recalls | RDW recall data 🟡; DVSA recalls 🟡; NHTSA recalls API 🟢 | EU Safety Gate 🟡; KBA recall database 🟡 |
| Safety rating | Euro NCAP (ask permission) 🟡 | ANCAP 🟡; NHTSA ratings API (US) 🟢 |
| Efficiency/environment rating | Green NCAP 🟡 | — |

## Platform, pack, voltage and chemistry

| Data point | Primary | Fallbacks |
| --- | --- | --- |
| Platform | Maker press kits 🔴 | Wikipedia/Wikidata platform pages 🟡; staff decision |
| Nominal and max pack voltage | Maker specs and press kits 🔴 | Björn Nyland tests 🟡; platform default; EVKX and EV Database as manual cross-checks only |
| "400 V charger behaviour" (booster or not) | Maker specs and owner manuals 🔴 | Fastned notes 🟡; owner reports later |
| Chemistry and cathode detail | Maker specs 🔴; cell supplier announcements (CATL, BYD, LG, Samsung SDI, Panasonic) 🟡 | Teardowns (for example Munro) 🟡; Battery Design pack pages (cross-check, licence unclear) 🟡; inferred from supplier + platform (low confidence) |
| Cell format, cell-to-pack, supplier | Supplier and maker announcements 🟡 | Teardowns 🟡 |
| Cooling type | Maker specs 🔴 | Platform default; teardowns 🟡 |

## Honest gaps 🔴

Boot volume, 0–100 times, heat pump and equipment, generation boundaries, warranty and new prices outside NL have no good open source. Those come from the maker's own spec sheets and price lists, entered by staff or extracted by an agent from the maker's public PDFs, always with a link and date. This is the slowest part of the catalogue, so the top 40 used models go first.

More sources means more matching work, not more code. The adapters are quick to write. Names that don't line up across sources ("ID.3 Pro S" vs "ID.3 77 kWh") are the real effort, and that is what the review queue is for.
