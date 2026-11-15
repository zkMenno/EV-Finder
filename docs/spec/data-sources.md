<!-- Mirror of the claude.ai spec doc, tab "Data sources" (rev 3), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Open data sources

Nov 14, 2026

Free, official or openly licensed sources for specs, registrations per model, fleet size, used transfers, recalls and market reports. Primary (government) sources first; aggregator sites only as fallback and cross-check. Licence notes marked 🟢 verified, 🟡 likely (check before launch), 🔴 unknown.

## Global and multi-country

| Source | What it gives | Granularity / cadence | Licence / access | Use for |
| --- | --- | --- | --- | --- |
| [IEA Global EV Outlook](https://www.iea.org/reports/global-ev-outlook-2026) + [Global EV Data Explorer](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer) | EV sales, stock, shares; GEVO 2026 has a chapter on resale value of used EVs; explorer now includes vehicle prices in selected markets | Country, annual (May) | CC BY 4.0 🟢 | Market pages, country context |
| [Our World in Data](https://ourworldindata.org/grapher/electric-car-sales) | IEA data re-packaged with a CSV/JSON API | Country, annual | CC BY (source terms apply) 🟢 | Easiest programmatic route to IEA numbers |
| [Ember EV sales tracker](https://ember-energy.org/latest-updates/ember-expands-its-transport-focus-as-electric-vehicles-become-a-global-energy-security-tool) | Monthly new registrations by drivetrain for 56 countries, built from national registries | Country, monthly | Open data, licence 🟡 | Monthly market pulse; list of national primary sources per country |
| [ICCT market monitors](https://theicct.org/wp-content/uploads/2026/10/ID-727-–-Global-LDVs-H1-2026_research-brief_final.pdf) | Europe monthly, global half-yearly; brand and country shares | Country, monthly / H1 | Free reports 🟢 | Context, cross-check |
| BNEF Electric Vehicle Outlook, Rho Motion | Forecasts, monthly totals | Region | Paid; free press summaries only | Headlines only, cited |

## Europe-wide

| Source | What it gives | Granularity / cadence | Licence / access | Use for |
| --- | --- | --- | --- | --- |
| [EEA CO₂ monitoring of new cars](https://co2cars.apps.eea.europa.eu/1) | Every new car registered in the EU, Iceland and Norway: manufacturer, commercial name, power, mass, electric energy consumption (Wh/km), electric range | Make/model/version, annual + provisional | Open, EEA terms 🟡 | Spec cross-check (WLTP Wh/km, range), new-registration counts per model per country |
| [EAFO (European Commission)](https://alternative-fuels-observatory.ec.europa.eu/transport-mode/road/eu27-uk-norway-iceland-switzerland-turkey-liechtenstein) | Registrations and fleet by fuel, top models; covers EU27, UK, NO, IS, CH, TR | Country, monthly / quarterly; downloads | Open portal, licence 🔴 | Fleet size per country, cross-check |

## Launch countries

| Country | Source | What it gives | Cadence | Licence / access |
| --- | --- | --- | --- | --- |
| NL | [RDW Open Data](https://data.overheid.nl/dataset/11346-open-data-rdw--gekentekende-voertuigen-brandstof) (Socrata API) | Every registered vehicle by plate: make, type, first registration, WLTP electric range, consumption; owner-change dates; APK inspections; recalls | Daily | CC0 🟢 |
| NL | [RVO Elektrisch vervoer cijfers](https://www.rvo.nl/onderwerpen/elektrisch-rijden/cijfers) + dashboard | Monthly EV fleet and sales overview; reuse allowed with source credit | Monthly | Attribution 🟢 |
| NL | CBS StatLine | Active fleet by vehicle characteristics and region | Annual | Open 🟡 |
| DE | KBA Neuzulassungen nach Modellreihen (FZ10) | New registrations per model series by fuel, incl. commercial share | Monthly | Free, attribution 🟡 |
| DE | KBA / VDA Besitzumschreibungen | Used-car ownership transfers by fuel (BEV 380,609 in 2024) | Monthly / annual | Free 🟡 |
| UK | [DfT vehicle licensing data files](https://Www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files) (VEH0120, VEH0160) | Licensed stock and first registrations by make, generic model, model and fuel, every quarter since 1994 | Quarterly | Open Government Licence 🟡 |
| UK | DVSA MOT history API / bulk MOT results | Mileage and test results per vehicle and model | Continuous | Free with key 🟡 |
| FR | [SDES / data.gouv.fr](https://www.data.gouv.fr/datasets/immatriculations-de-vehicules-routiers/discussions) | New and used registrations by fuel, user status and commune since 2011; monthly new-car notes | Monthly / annual | Licence Ouverte 🟡 |
| BE | [FEBIAC](https://www.febiac.be/sites/default/files/media/file/2026-01/Communiqu%C3%A9%20de%20presse%202025%20FR.pdf) press releases | New registrations by model and region; most popular used BEV models and monthly used BEV registrations | Monthly / annual | Free PDFs; figures citable 🟡 |
| BE | Statbel | Fleet by fuel; EV stock | Annual | Open 🟡 |
| NO | Statens vegvesen register via open API; [OFV](https://www.electrive.com/2026/04/01/norway-registers-17400-new-battery-electric-cars-in-march/) | Every registration by model; OFV monthly model stats incl. used-car owner changes | Near real-time / monthly | NLOD 🟡 |

## US and Australia (phase 4)

| Country | Source | What it gives | Cadence | Licence / access |
| --- | --- | --- | --- | --- |
| US | [fueleconomy.gov web services](https://fueleconomy.gov/feg/ws) | EPA range, efficiency, charge time for every model year since 1984; CSV/XML download and REST API, no key | Ongoing | US government data, public domain 🟢 (R-28) |
| US | NHTSA vPIC (VIN decoder) and recalls API | Decode make/model/year from VIN; recalls per model | Ongoing | Free 🟡 |
| US | [California Energy Commission ZEV sales](https://www.energy.ca.gov/zevstats) | New ZEV sales by make and model, county | Quarterly | Free to read, no commercial use 🔴 (R-28) |
| US | [Washington State EV population](https://catalog.data.gov/dataset/electric-vehicle-population-data) | Every registered EV: make, model, model year, range, county | Monthly | ODbL 🟡: internal use only, never in CC BY output (R-28) |
| US | [Argonne monthly sales](https://www.anl.gov/esia/light-duty-electric-drive-vehicles-monthly-sales-updates) | National monthly totals (stopped per-model reporting in Nov 2019) | Monthly | Free 🟢 |
| AU | [EVC State of EVs](https://www.pv-magazine-australia.com/press-releases/state-of-evs-2026-an-ev-bought-every-100-seconds-as-car-choice-charging-and-innovation-accelerate/) | Annual sales, fleet (612,000 EVs by June 2026), model count | Annual | Free report |
| AU | FCAI VFACTS via [The Driven](https://thedriven.io/2026/11/05/australian-electric-vehicle-sales-by-month-in-2026-by-model-and-by-brand-3/) | Monthly BEV sales per model | Monthly | Aggregator; cite 🟡 |

## Used-market and battery reports (free, cite the figures)

| Source | Market | What it gives | Cadence |
| --- | --- | --- | --- |
| AutoUncle insights | 14 EU markets | Used BEV share and median prices per country | Monthly |
| AA Cars Used Car Index, Autotrader retail price index | UK | Used EV prices, incl. top-20 models | Quarterly / monthly |
| Cox Automotive EV Market Monitor | US | Used EV sales, average listing price, days to sell | Monthly |
| AADA / AutoGrab, Pickles, Carma | AU | Used EV sales, auction volumes, depreciation by brand | Quarterly |
| Clutch, CARFAX Canada | CA | Used EV prices and share | Monthly |
| AUTO1 EV Trends, Indicata Market Watch | EU, BR | Wholesale used EV prices, stock days | Quarterly |
| Recurrent, Generational index, AVILOO performance report | US, UK, global | Battery health by model, mileage and age | Annual / semi-annual |
| Bjørn Nyland test sheet | Global | Range, charging, degradation tests | Ongoing |

## Aggregator fallbacks (cross-check only)

- [elektroquatsch.de](https://www.elektroquatsch.de/zulassungen/modell/peugeot-208): KBA registrations per model, monthly, with commercial share.
- [elbilstatistikk.no](https://elbilstatistikk.no/en/graph): Norway registrations from the public API.
- [EVKX sales statistics](https://evkx.net/nb/models/salestat/): top models per country from OFV, KBA, SIMI and others.
- The Driven (AU), CleanTechnica monthly country reports, best-selling-cars.com.

Aggregators repackage primary sources; always ingest the primary source and use aggregators only to spot gaps and errors.

## Added in research round 2 (Nov 2026)

### Free used-price indices (layer 0 for used prices)

Published for free by the marketplaces themselves. Country-level trends, not per-generation bands, but legal to quote with credit and useful to check our own bands.

| Source | Coverage | Frequency | Use |
| --- | --- | --- | --- |
| Autotrader UK Retail Price Index | UK, \~800,000 daily price points, used-EV section and model tables 🟢 | Monthly | UK trend line, top risers and fallers |
| AutoScout24 AGPI | DE and AT monthly; 5-country Europe report yearly (IT, DE, BE, NL, AT) 🟢 | Monthly / yearly | DE and AT trend line by fuel type |
| Indicata Market Watch | 13 European countries, BEV price, stock and days-to-sell 🟢 | Monthly, free PDF | Cross-country BEV trend, fastest-selling used EVs |
| Recurrent | US used EV prices and inventory 🟢 | Monthly and quarterly | US trend line |
| Clutch Used Car Pricing Report | Canada, incl. used EV prices 🟢 | Monthly | Canada trend line |
| K Car outlook | South Korea, 740+ models 🟢 | Monthly | KR trend line |
| Otomoto Insights, Sahibinden reports, Kavak reports, Data OLX Autos | PL, TR, MX, BR 🟢 | Monthly / quarterly | Emerging-market trend lines |

### Battery health

| Source | What | Notes |
| --- | --- | --- |
| Aviloo Certified EV Battery Report | Median state of health at 50k, 100k and 150k km for 20 popular models, from 500,000+ tests 🟢 | Twice a year; Aviloo sells the tests, so treat as a commercial source 🟢 |
| Belgium Car-Pass | Optional independent battery health test on the Car-Pass since Jan 2026 🟢 | Show a "Car-Pass battery test available" hint on BE listings |
| Recurrent, Generational | US and UK battery health studies 🟢 | Cross-check |

### Inspections and history

| Source | What | Licence |
| --- | --- | --- |
| RDW Keuringen + Geconstateerde gebreken | Every NL inspection and the defects found, per plate 🟢 | CC0 🟢 |
| DVSA MOT history API | UK test results, mileage at each test, failures and advisories; free key on application 🟢 | Open Government Licence 🟢 |

These two unlock a data-driven "Known issues" block per generation (most common inspection defects by age), which moves that feature from content work to a pipeline job.

### Registrations in emerging markets

| Country | Source | Granularity |
| --- | --- | --- |
| India | VAHAN dashboard 🟢 | Daily, by state, maker and fuel |
| Thailand | Department of Land Transport 🟢 | Monthly, by fuel type |
| Mexico | INEGI RAIAVL 🟢 | Monthly, by brand and model, EVs by state |
| Brazil | ABVE Data (from Renavam) 🟢 | Monthly, by powertrain and model |
| New Zealand | Ministry of Transport fleet statistics + NZTA open fleet data 🟢 | Monthly EV figures, new vs used imports |
| Türkiye | ODMD 🟡 | Monthly |
| Global | Ember EV tracker (60 countries) 🟢 | Monthly shares |

### Real DC charging (curves, not peak kW)

Peak kW on a brochure is often held for only a few minutes. These sources measure what a car really does from 10 to 80%.

| Source | What it gives | Conditions | Licence / use |
| --- | --- | --- | --- |
| Fastned brand overview | A charge curve per model and battery version 🟢 | Optimal battery temperature, about 30 °C 🟢 | Public pages, no open licence: ask permission; a natural Dutch partner |
| Open EV Data (KilowattApp) | Simplified curves based on Fastned's charts, with a flag when a default curve was used instead of measured data 🟢 | Optimal | MIT with an attribution requirement 🟢; drop the default curves |
| NAF + Motor El Prix | 10–80% time and average kW, next to the maker's claimed time, summer and winter 🟢 | Real chargers, real cold, preconditioned | Facts with credit; ask before bulk import |
| ADAC tests | Average kW from 10 to 80% for every tested car, km recharged in 20 minutes, a winter stress test 🟢 | Controlled | Facts with credit |
| P3 Charging Index | Real km recharged in 10 and 20 minutes, using ADAC consumption 🟢 | Same chargers for all cars | Yearly report, few models; facts with credit |
| Automobile Propre Supertests | Measured 10–80% times and average kW against peak kW 🟢 | Real chargers | Facts with credit |
| Bjørn Nyland | Charging curves from his tests 🟢 | Real chargers, Norway | Same permission request as the range sheet |
| EVKX | Measured curves tagged optimal or cold, verified or estimated 🟢 | Mixed | 🔴 Terms forbid using the data to build a competing vehicle database 🟢: manual cross-check only, but a good model for our data structure |
| Owners (later) | Curves logged with OBD apps | Real life | Owner-submitted, Phase 5 |
