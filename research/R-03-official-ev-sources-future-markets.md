# R-03 — Official open-data sources for EVs in future markets

## Question

Same question as R-02 (launch countries), but for the future markets in the Master spec "Global markets" list: **Tier 1b** Norway; **Tier 3** US, Canada, Australia, New Zealand, South Korea (and China, partner-only); **Tier 4** Singapore, Vietnam, Thailand, Indonesia, Malaysia, Philippines, Türkiye, Israel, Jordan, Brazil, Mexico, Colombia, Uruguay, Costa Rica, Chile; **Tier 5** watchlist Ethiopia, Nepal, Sri Lanka, India, Japan (Japan matters as a used-EV supply source).

For each market: which official bodies publish open data on EVs (fleet and registrations by make/model/year, specs, prices, inspections, recalls, charging, import/export)? Which official aggregators exist, and which primary registry are they built from? What is the exact licence on the publisher's own page?

Format and legend follow R-02. Licences were read on the publisher page or in its catalogue API (CKAN/Socrata/DCAT metadata). Where neither stated one, the table says **not stated** and marks it **needs check**. Retrieved 2026-11-15. 🟢 verified, 🟡 reasoned/partly verified, 🔴 unsure.

## Answer (short)

- **Best open data of all future markets: New Zealand and Malaysia.** Both publish per-vehicle or per-transaction data with make, model and fuel under **CC BY 4.0**. NZ also records **import status and country of origin**, so it shows the Japan → NZ used-EV flow directly.
- **US:** the federal sources are excellent and in the public domain: fueleconomy.gov specs (EPA range, kWh/100 mi), NHTSA vPIC/recalls/complaints, and the AFDC station data ("may be used for any purpose whatsoever"). Registration data is **state by state**. The famous **Washington EV population dataset is ODbL**, which is a licence-separation red flag. Connecticut DMV EV registrations are **Public Domain** and include make and model. **AFDC registration counts and Argonne sales are built on Experian/Wards (commercial)**, so do not ingest them.
- **Australia:** there is no national make/model fleet open data (BITRE "Road vehicles Australia" has fuel × year of manufacture only). **States fill the gap under CC BY 4.0.** Queensland has new registrations **and ownership transfers** with make, model and fuel, which is rare used-market data. Victoria has make × model counts but no fuel column. The Green Vehicle Guide licence could not be read (site timed out).
- **Canada:** NRCan Fuel Consumption Ratings (BEV specs) and Transport Canada iZEV incentive statistics (make/model/model year/province/month, programme now closed) are both under **OGL-Canada**. AFDC station data also covers Canada.
- **Norway:** SSB is **CC BY 4.0** but fuel-level only. Statens vegvesen's open vehicle dataset is **CC BY 4.0**, but **bulk download is paused** while it is rebuilt. The per-plate API needs a Norwegian eID. This is weaker than expected for Europe's biggest used-EV market.
- **Emerging markets with usable make/model data:** Malaysia (🟢), Israel (per-plate with VIN, licence "Other (Open)", needs check), Thailand (DLT monthly make × model, **no fuel column**, "Open Data Common" needs check), Mexico (INEGI RAIAVL monthly sales by make/model, "Términos de Libre Uso" allow commercial use with credit), Singapore (annual make × fuel, Singapore Open Data Licence with a **conspicuous-notice** rule), Uruguay (Montevideo only). **Brazil** publishes RENAVAM make/model counts, but the gov.br site licence is **CC BY-ND 3.0**, a red flag.
- **Weak or none:** Türkiye (TÜİK bulletins, no licence found), South Korea (national make/model registration not found openly; regional files only), Colombia (RUNT EV fleet is CC BY 4.0 but has **no make**), Chile (municipal fragments only), Indonesia, Vietnam, Philippines, Jordan, Costa Rica (no official open make/model data found). **China:** no open registration data (CPCA/CAAM are industry bodies; MIIT catalogues are lists, not open datasets).
- **Japan (supply side):** Customs trade statistics have a separate statistical code for **used BEVs (8703.80-010)** by destination country. The Customs terms say "商用利用も可能です" (commercial use allowed).

## Market evidence (why these markets)

| market | 2025 EV signal | source | conf. |
|---|---|---|---|
| China | EVs ≈ 55% of car sales | IEA GEVO 2026 executive summary | 🟢 |
| US | "just under 10%" of car sales, flat; dropped at year-end after tax credits ended | IEA GEVO 2026 | 🟢 |
| SE Asia (region) | sales more than doubled to a share of nearly 20%; Viet Nam, Indonesia, Thailand lead | IEA GEVO 2026 | 🟢 |
| Vietnam | 37% EV share of light-duty sales | ICCT, via newmobility.news | 🟡 |
| Thailand, Türkiye, Indonesia, Colombia | about 9% EV share each (ICCT definition) | ICCT, via newmobility.news | 🟡 |
| Türkiye | BEV ≈ 190k, **17% of passenger cars**, +90% | ODMD (industry), via Daily Sabah | 🟡 (does not match ICCT's 9%; definitions differ) |
| Latin America | +75%, led by Brazil and Mexico | IEA GEVO 2026 | 🟢 |
| India | 176,538 e-cars in CY2025, +77% | VAHAN, via e-vehicleinfo.com | 🟡 |

## Source tables

Legend for "usable": **yes** = licence verified on the publisher page or catalogue and access works by script. **needs check** = licence not stated or not readable, or access blocked. **no** = not open or not official.

### Tier 1b — Norway

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `svv-kjoretoy-open` | "Datasett for kjøretøyopplysninger" / Statens vegvesen | **primary** (Kjøretøyregisteret) | Technical vehicle information plus first-registration and deregistration dates. Plates and chassis numbers are excluded. Field list not published on the page. 🟡 | CSV and API (JSON/XML). **Bulk download currently paused**: the old data hub was shut down and SVV is building its own service | "gjort tilgjengelig under Creative Common Navngivelse 4.0 (CC 4.0-BY)" — https://www.vegvesen.no/fag/teknologi/apne-data/et-utvalg-apne-data/api-for-kjoretoyopplysninger/ 🟢 | Yes (CC BY). Wording not specified | **needs check** (availability) | Watch for the relaunch. This would become the NO equivalent of RDW |
| `svv-tekniske-api` | API for tekniske kjøretøyopplysninger / Statens vegvesen | primary | Per plate or VIN: dimensions, weights, engine/power, tyres, **last and next EU-kontroll date**, first registration in Norway. No mileage or owner. 🟢 | REST with an API key. Needs **Norwegian eID** (BankID/Buypass/Commfides) or Altinn for businesses | **not stated** on the page — https://www.vegvesen.no/fag/teknologi/apne-data/et-utvalg-apne-data/api-for-tekniske-kjoretoyopplysninger/ | — | needs check | Per-plate lookups, not statistics. The eID requirement blocks a non-Norwegian operator |
| `ssb-07849` | StatBank 07849 "Registered vehicles, by type of transport and type of fuel" / SSB | **aggregator of Kjøretøyregisteret** | Stock on 31 December by vehicle group × region × fuel (incl. Electricity), 2008–2025, annual. **No make/model.** 🟢 | PxWeb API https://www.ssb.no/en/statbank1/table/07849/ | "We use the licence Creative Commons Attribution 4.0 International (CC BY 4.0)" — https://www.ssb.no/en/diverse/lisens 🟢 | "attribute us as Statistics Norway, SSB…", link to ssb.no and the licence | **yes** (totals) | Sanity totals only |
| — | OFV (Opplysningsrådet for veitrafikken) | industry body, built on SVV data | Monthly registrations by make/model | ofv.no (page did not load for scripts) | not open data (🟡) | — | **no** | Same role as ACEA: do not ingest |
| `no-charging` | NOBIL / Enova | — | Charging stations. 🔴 not verified | — | not checked | — | needs check | — |

### Tier 3 — United States

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `fueleconomy-vehicles` | fueleconomy.gov "vehicles" dataset / DOE + EPA (run by ORNL) | **official aggregator** of EPA certification test data | Make × model × **year × options (variant)**, 1984 onward. EV fields include EPA range and combined kWh/100 mi. Updated continuously (web services page "Updated: Wednesday November 04 2026"). 🟢 | Zipped/unzipped CSV and XML: https://www.fueleconomy.gov/feg/download.shtml ; REST: https://www.fueleconomy.gov/feg/ws/index.shtml | Not stated on the download page. data.gov record (publisher EPA) links the **EPA Data License**: "all data produced by the U.S EPA is by default in the public domain … 17 U.S.C. § 105" — https://catalog-old.data.gov/dataset/www-fueleconomy-gov , https://edg.epa.gov/EPA_Data_License.htm 🟡 | Not required | **yes** (🟡 licence via data.gov) | Units are imperial (miles, kWh/100 mi), so convert at ingestion. "Options" text is free-form. Gives the best US variant-level spec catalogue |
| `nhtsa-vpic` | vPIC (Product Information Catalog) / NHTSA | primary (manufacturer VIN filings) | VIN decoding; makes, models, model years, vehicle types; batch decode. 🟢 (API tested) | REST JSON/XML/CSV, no key: `https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/tesla?format=json`; standalone DB download | "Information presented on this web site is considered public information and may be distributed or copied." — https://www.nhtsa.gov/about-nhtsa/terms-use 🟢 | Not required | **yes** | Useful as a **join key**: VIN prefix → make/model/year. WA and NY registers only give VIN fragments or full VINs |
| `nhtsa-recalls-complaints` | Recalls, complaints, investigations (ODI) / NHTSA | primary | Per campaign or complaint: make/model/model year, component, date. 🟡 (not downloaded) | REST APIs (api.nhtsa.gov) and ODI flat files | Same NHTSA terms as above 🟡 | — | yes (🟡) | Complaints are unverified consumer reports. Show them as counts, not as facts |
| `afdc-stations` | Alternative Fuel Stations (station locator) / DOE AFDC, run by NLR (formerly NREL) | primary (operator/network reports) | Every EV station in the **US and Canada**: connectors, power level, network, access, status; history from 2014. 🟢 | CSV/JSON download https://afdc.energy.gov/data_download ; API `developer.nrel.gov/api/alt-fuel-stations/v1` (API key) | Download terms: data "may be used for any purpose whatsoever"; DOE/NLR/Alliance names may not be used to endorse; AS IS; **user indemnifies DOE** — https://afdc.energy.gov/data_download 🟢 | Not required (no endorsement allowed) | **yes** | The developer.nrel.gov terms page is robots-blocked, so API rate limits were not read |
| — | AFDC "Vehicle Registration Counts by State" / NLR | aggregator of **Experian** (commercial) | State × fuel type, annual, rounded to 100. 🟢 | HTML/XLSX https://afdc.energy.gov/vehicle-registration | "derived by the National Laboratory of the Rockies with data from Experian Information Solutions" — no licence | — | **no** (third-party) | Cross-check only |
| — | Argonne "Light Duty Electric Drive Vehicles Monthly Sales Updates" | aggregator of **Wards** (commercial) | Monthly BEV/PHEV/HEV totals. "As of November 2019, Argonne no longer reports … by make and model." 🟢 | HTML figures https://www.anl.gov/node/101331/ | No licence stated | — | **no** | Totals cross-check only |
| `wa-ev-population` | Electric Vehicle Population Data (`f6w7-q2d2`) / Washington State Dept of Licensing | **primary** (state register) | One row per EV: VIN (first 10), county, city, ZIP, model year, make, model, BEV/PHEV, CAFV eligibility, **electric range**, utility, census tract. 🟢 | Socrata `https://data.wa.gov/resource/f6w7-q2d2.json` | **"Open Data Commons Open Database License" (ODbL)** — dataset metadata https://data.wa.gov/api/views/f6w7-q2d2.json 🟢 | ODbL attribution + **share-alike** | **needs check** (licence policy) | **Red flag:** ODbL must stay separate from CC BY output (AGENTS.md data rule 3). Related WA datasets (counts by county, title and registration activity, size history) are also ODbL |
| `ct-ev-registrations` | Electric Vehicle Registration Data (`y7ky-5wcz`) / CT DMV on data.ct.gov | primary | Per registration: make, **model**, vehicle year, fuel code, weight, body, registration start/end, city. Updated 2026-11-06. 🟢 | Socrata `https://data.ct.gov/resource/y7ky-5wcz.json` | "**Public Domain**" (Socrata catalogue metadata) 🟢 | Not required | **yes** | Small state, but the cleanest US state licence found |
| `ny-dmv-registrations` | Vehicle, Snowmobile, and Boat Registrations (`w4pv-hbkt`) / NYS DMV | primary | Per registration: **full VIN**, make, model year, body, **fuel type**, ZIP, county, validity dates. **No model field.** 🟢 | Socrata `https://data.ny.gov/resource/w4pv-hbkt.json` | **not stated** (metadata licence field empty) | — | needs check | Decode model from VIN via vPIC. Read the data.ny.gov terms of use before ingesting |
| `ca-dmv-fuel-zip` | Vehicle Fuel Type Count by Zip Code / California DMV (data.ca.gov) | primary | Counts as of 1 January by ZIP × model year × fuel × **make** × duty, 2019–2026. **No model.** 🟢 | CSV per year via CKAN `package_show?id=vehicle-fuel-type-count-by-zip-code` | **not stated** (CKAN licence empty) | — | needs check | The CEC ZEV sales dashboard (energy.ca.gov) was not verified 🔴 |
| — | Texas, Colorado registration open data | — | Not found in the Socrata catalogues searched. 🔴 | — | — | — | needs check | — |
| — | Experian Automotive, S&P Global Mobility (IHS Polk) | commercial | Full US VIO and registrations by make/model/trim | Paid | not open | — | **no** | This is the data behind AFDC registration counts |

### Tier 3 — Canada

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `nrcan-fcr` | Fuel consumption ratings / Natural Resources Canada | official aggregator of manufacturer test data | Make × model × model year specs, with a BEV/PHEV file (energy use, range). 🟡 (fields not opened) | CSV/XLSX on open.canada.ca | "**Open Government Licence - Canada**" (CKAN metadata) 🟢 | OGL-Canada attribution statement | **yes** | Same EPA 5-cycle basis as the US, so specs can be shared across both |
| `tc-izev` | Statistics on the Incentives for Zero-Emission Vehicles (iZEV) Program / Transport Canada | primary (programme records) | Incentivised new BEV/PHEV purchases and leases by **make, model, model year**, province, dealer postal code, engine type, recipient type, month. FY2019-20 to FY2024-25 CSVs, updated Nov 2025. 🟢 | CSV https://open.canada.ca/data/dataset/42986a95-be23-436e-af15-7c6bf292a2e1 | "Open Government Licence - Canada" 🟢 | Yes | **yes** | **Programme closed** ("Closed" in the title), so the series ends. Covers incentive-eligible cars only (price cap), not all EV sales |
| `statcan-nmvr` | New motor vehicle registrations (table 20-10-0024) / Statistics Canada | aggregator of provincial registries | Quarterly new registrations by fuel type and province. **No make/model.** 🟡 (table not opened) | StatCan CSV ZIP | StatCan tables are listed as OGL-Canada on open.canada.ca 🟡 | Yes | yes (totals) | — |
| — | SAAQ (Québec) vehicles in circulation | primary | 🔴 not found in the Données Québec search | — | — | — | needs check | Québec is Canada's largest EV province, so it is worth a manual check |
| `afdc-stations` | (see US) | | Covers Canada | | | | yes | |

### Tier 3 — Australia

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `bitre-rva` | "Road vehicles Australia, January 2026" / BITRE | **aggregator of state/territory registries**; replaces the ABS Motor Vehicle Census (discontinued 2021) | Stock on 31 January by vehicle type × state × **motive power** × year of manufacture × postcode. **No make/model.** Annual. 🟢 | CSV on data.gov.au `road-vehicles-australia-january-2026` | "**Creative Commons Attribution 3.0 Australia**" (CKAN). The 2024 edition says CC BY 2.5 AU 🟢 | Yes | **yes** (totals) | The licence version changes between editions, so store it per file |
| `qld-reg-new-transfers` | "Vehicle Registration New and Transfers" / Queensland TMR | **primary** | Registration **transactions: new and ownership transfers** with make, model, body type, colour, **fuel type**, year of manufacture, transaction type, customer type, LGA. 2026 files exist. 🟢 | CSV on data.qld.gov.au (slug ends in `-test`, so it may move) | "**Creative Commons Attribution 4.0**" (CKAN) 🟢 | Yes | **yes** | **Rare open used-market data** (transfers by model). Watch for a slug change |
| `qld-reg-stock` | "Vehicle registrations" / Queensland TMR | primary | Whole register by make, year, colour, category, body, fuel. Annual. Last updated 2022-10. 🟢 | CSV in parts | CC BY 4.0 🟢 | Yes | yes | Stale (2022) |
| `vic-fleet-by-model` | "Whole Fleet Vehicle Registration Snapshot by Model" / Victoria Dept of Transport and Planning | primary (VicRoads) | Quarterly count by make × model × colour (Q1 2026 file). **No fuel, no year.** 🟢 | CSV on opendata.transport.vic.gov.au | "Creative Commons Attribution 4.0 International" 🟢 | Yes | **yes** | BEV flag has to come from a model-name map. Codes are padded (`AION  `) |
| `vic-new-monthly` | "Monthly New Vehicle Registration" / Victoria DTP | primary | Monthly new registrations by make × model × colour × year of manufacture (Sept 2026 file). No fuel. 🟢 | CSV | CC BY 4.0 🟢 | Yes | **yes** | Same gaps as above |
| — | NSW vehicle registration by make/model | — | Not found on data.nsw (only charging). 🟡 | — | — | — | needs check | — |
| `au-gvg` | Green Vehicle Guide / Dept of Infrastructure, Transport, Regional Development, Communications, Sport and the Arts (**not DCCEEW**) | official aggregator of manufacturer/ADR test data | New-vehicle specs: CO2, energy use (kWh/100 km), electric range. 🟡 | Website; no bulk export found. Copyright page `/Home/Copyright` timed out | **not stated** (could not read) | — | needs check | A third-party site (vesr.gov.au) says it uses GVG data "under license", which suggests GVG has a licence, but it is unverified 🔴 |
| — | Electric Vehicle Council | industry body | EV sales reports (fed by FCAI/EVDirect) | PDF | not official | — | **no** | — |
| — | ANCAP | independent safety body | Crash ratings by model | Website | not checked 🔴 | — | needs check | Nice-to-have only |
| `nsw-ev-charging` | EV Charging Locations / Transport for NSW | aggregator of operator data | AC/DC sites, connectors, power, planned sites (file `ev_20261007.csv`). 🟢 | CSV on opendata.transport.nsw.gov.au | "Creative Commons Attribution" (CKAN, version not given) 🟡 | Yes | yes | There is **no national open charging register** in AU |

### Tier 3 — New Zealand

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `nzta-mvr` | "New Zealand vehicle fleet open data sets" (Motor Vehicle Register) / NZ Transport Agency Waka Kotahi | **primary** | One row per vehicle (over 5 million rows): make, model **and sub-model**, class, colour, year and month of first NZ registration, vehicle year, **import status**, **country of origin**, VIN prefix (11 chars), territorial authority, fuel-consumption fields; motive power in the metadata (🟡). **Monthly**, as at month end. 🟢 | CSV by vehicle year plus an all-years ZIP. Open Data Portal / ArcGIS Hub, and catalogue.data.govt.nz "Motor Vehicle Register CSV and API" | "**CC-BY International 4.0 Licence**" — https://nzta.govt.nz/resources/new-zealand-motor-vehicle-register-statistics/new-zealand-vehicle-fleet-open-data-sets 🟢 | Yes (wording not specified; name NZTA) | **yes** | **Best future-market source.** Import status and country of origin show **used Japanese imports** (e.g. Nissan Leaf). Height, weight and transmission are sparse |
| — | Ministry of Transport fleet statistics | aggregator of the MVR | Annual/monthly fleet reports. 🔴 not verified | transport.govt.nz | not checked | — | needs check | Use the MVR directly |
| — | NZ charging | — | 🔴 not verified (EECA/NZTA) | — | — | — | needs check | — |

### Tier 3 — South Korea

| id | name / publisher | primary or aggregator (of which primary) | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| — | National register by make/model (KOTSA / MOLIT) | primary | **No national make/model registration file found** on data.go.kr. KOTSA publishes other monthly/annual counts (e.g. motorcycle reports) under "이용허락범위 제한 없음". 🟡 | data.go.kr | — | — | needs check | MOLIT's stat.molit.go.kr (registration statistics) was not checked 🔴 |
| `jeju-vehicle-reg` | 제주특별자치도_차량별자동차등록대수정보 / Jeju | primary (regional) | Per vehicle name (차명), model year, displacement, fuel, use, class, first registration date, 2019 onward. 🟢 | CSV, data.go.kr id 15128417 | "**이용허락범위 제한 없음**" (no restriction on permitted use) 🟢 | — | yes (regional) | The fuel enum is listed as diesel/petrol/**other**, so EVs may sit under "기타" |
| `kr-regional-fuel` | Many city/province "자동차 등록현황" files (e.g. Chungju EV registrations) | primary (regional) | Counts by fuel (전기) × type. No model. 🟢 | data.go.kr CSV | Mostly "이용허락범위 제한 없음". Seoul's is "제3자 권리 포함 … 공공저작물 출처표시 (제1유형)" 🟢 | KOGL type 1 = attribution | yes (totals) | Fragmented |
| — | Charging (환경부 EV charger API on data.go.kr) and EV model list (ev.or.kr) | — | 🔴 not verified | — | — | — | needs check | — |

### Tier 3 — China (partner-only, brief)

| id | name / publisher | primary or aggregator | contents | access | licence | usable | gotchas |
|---|---|---|---|---|---|---|---|
| — | Ministry of Public Security vehicle register | primary | Only national totals in press releases | — | not open | **no** | — |
| — | MIIT announcements and NEV purchase-tax exemption catalogue | official lists | Type approvals, NEV models | Published as lists/PDFs, not open datasets 🟡 | not stated | **no** | Partner data only |
| — | CPCA, CAAM | industry associations | Monthly sales by make/model | Paid/redistributed via CEIC etc. | not open | **no** | — |

### Tier 4 — Southeast Asia

| id | country / publisher | primary or aggregator (of which primary) | contents | access | licence (as stated) + URL | usable | gotchas |
|---|---|---|---|---|---|---|---|
| `my-cars-reg` | **Malaysia** — "Car Registration Transactions" / Road Transport Department (JPJ) via data.gov.my | **primary** | One row per registration since 2000: `date_reg, type, maker, model, colour, fuel (incl. electric, hybrid_petrol), state`. Monthly (last 10 Nov 2026; next 10 Dec). 🟢 | CSV and **Parquet** per year: `https://storage.data.gov.my/transportation/cars_2026.csv`; open API | "made open under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**" — https://data.gov.my/data-catalogue/registration_transactions_car 🟢 | **yes** | New registrations only (🟡: transfers not seen). The best emerging-market source |
| `sg-car-pop-make` | **Singapore** — "Annual Car Population by Make" / LTA via data.gov.sg | aggregator of LTA register | Year × **make × fuel_type**, 2005–2024. No model. Also monthly new registrations by make. 🟢 | data.gov.sg API (`d_20d3fc7f08caa581c5586df51a8993c5`); LTA DataMall | **Singapore Open Data Licence v1.0**. Requires "a **conspicuous notice** acknowledging the source … and including a link to the … Licence"; no implied endorsement — https://data.gov.sg/open-data-licence 🟢 | **yes** | The attribution rule is stricter than CC BY: it needs a visible notice in the product |
| `th-dlt-newreg` | **Thailand** — "สถิติจำนวนรถจดทะเบียนครั้งแรก … จำแนกตามยี่ห้อและรุ่น" / Department of Land Transport | **primary** | Monthly first registrations by vehicle type × **make × model**. Buddhist-era years (2565 = 2022). Newest file seen: Dec 2567 (2024) plus 2566 full year. **No fuel column.** 🟢 | CSV via datagov.mot.go.th CKAN (`dataset_stat_1_001`) and gdcatalog.dlt.go.th | "**Open Data Common**" (CKAN licence title); terms text not read | **needs check** | The fuel-type table (data.go.th `25222`) is behind a Cloudflare block. EV flag needs a model-name map. Check whether 2025–2026 files exist |
| — | **Indonesia** — Korlantas/Polri register; Gaikindo | primary not open; Gaikindo is industry | Wholesale/retail by make (Gaikindo) | — | not open | **no** | Use ICCT market spotlights for context only |
| — | **Vietnam** — Vietnam Register; VAMA | primary not open; VAMA is industry (VinFast not a member) | — | — | not open | **no** | The largest SE Asian EV market has the least open data |
| — | **Philippines** — LTO | primary | EV registration counts only in press (e.g. "40k EVs registered Jan–Sep 2025") | — | no open dataset found 🟡 | **no** | — |

### Tier 4 — Middle East and Türkiye

| id | country / publisher | primary or aggregator (of which primary) | contents | access | licence (as stated) + URL | usable | gotchas |
|---|---|---|---|---|---|---|---|
| `il-mot-register` | **Israel** — "מספרי רישוי של כלי רכב פרטיים ומסחריים" / Ministry of Transport (data.gov.il) | **primary** | Per plate (4.2 million rows): make code/name, model code, **commercial name (`kinuy_mishari`)**, trim, year, engine model, **fuel (`sug_delek_nm`)**, ownership type, **full VIN (`misgeret`)**, **last test date**, licence expiry, first on-road month. Updated daily (2026-11-14). Related sets: deregistered vehicles, private-vehicle history, EVs by district, inactive vehicles. 🟢 | CKAN datastore API and CSV | "**Other (Open)**" (CKAN `other-open`, no licence URL). Charging-station set is "Creative Commons Attribution" | **needs check** | Very rich (RDW-like), but the licence text behind "Other (Open)" was not found. It contains full VINs |
| — | **Türkiye** — TÜİK "Motorlu Kara Taşıtları" (monthly) | **aggregator** of the EGM/Ministry of Interior register | Monthly vehicles registered to traffic by type, fuel and **brand** (bulletin). 🟡 | Bulletins and data portal | **not stated** (no licence found) | **needs check** | ODMD (industry) has the model-level BEV data but is not official |
| — | **Jordan** — Jordan Customs / Free Zones Corp. (JFZIC) | primary (clearances) | EV clearances and re-exports in press releases only | — | no open dataset found 🟡 | **no** | Import-fed from China (about 87% share per press). Customs is the only real source |

### Tier 4 — Latin America

| id | country / publisher | primary or aggregator (of which primary) | contents | access | licence (as stated) + URL | usable | gotchas |
|---|---|---|---|---|---|---|---|
| `mx-inegi-raiavl` | **Mexico** — RAIAVL "Venta al público y producción de vehículos ligeros por marca, modelo, segmento y país origen" / INEGI | **aggregator** of manufacturer/importer reports (administrative record of the industry) | Monthly retail sales by **make × model × type × segment × country of origin**, 2005–2026. Separate table RAIAVL_11: hybrid + electric sales by state since 2016 (no make). Export table by make/model/destination. 🟢 | PxWeb tables https://www.inegi.org.mx/app/tabulados/pxwebv2/pxweb/es/RAIAVL/RAIAVL/ | "Términos de Libre Uso de la Información del INEGI": copy, adapt and "**explotar comercialmente**"; must credit "Fuente: INEGI, nombre del producto" — https://www.inegi.org.mx/inegi/terminos.html 🟢 | **yes** | **No propulsion column** in the make/model table, so the EV flag needs a map. Only brands that report to INEGI are included (🟡: check BYD and other importers). These are sales, not registrations |
| `br-renavam` | **Brazil** — "Quantidade de Veículos por UF, Município, Marca e Modelo" (RENAVAM) / SENATRAN, Ministério dos Transportes | **primary** | Monthly fleet by state × municipality × **make/model**. Separate monthly files by fuel, year of manufacture/model, power etc. (Sept 2026 files). 🟢 (listing) | Fuel/year XLSX on gov.br; make/model on https://dados.transportes.gov.br/dataset/registro-nacional-de-veiculos-automotores-renavam (portal reset the connection) | gov.br page footer: "**Creative Commons Atribuição-SemDerivações 3.0** Não Adaptada" — https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/estatisticas-frota-de-veiculos-senatran . dados.transportes licence not read | **needs check** | **Red flag: ND (no derivatives)** if it applies to the data. Make/model and fuel are in **separate files** (no cross-tab). SENATRAN also sells statistical files via Serpro ("contratar arquivos estatísticos"). ABVE is industry, not official |
| `co-runt-ev` | **Colombia** — "Vehículos eléctricos e híbridos matriculados en Colombia – RUNT 2.0" (`ntxy-q9ix`) / MinTransporte | aggregator of RUNT | Fuel (ELECTRICO/…), **model year** (`modelo`), registration year, class, body, municipality, count. **No make.** Updated 2026-08. 🟢 | Socrata `https://www.datos.gov.co/resource/ntxy-q9ix.json` | "**Creative Commons Attribution 4.0 International**" (metadata) 🟢 | yes (totals) | `modelo` means model year, not model. Many municipal fleet sets on datos.gov.co are **CC BY-SA 4.0** |
| `uy-mvd-parque` | **Uruguay** — "Parque automotor de Montevideo" / Intendencia de Montevideo | primary (municipal) | Annual registered cars by **make, model, year** (2019–2024 files). 🟢 | CSV on catalogodatos.gub.uy | "**Licencia de DAG de Uruguay**" (PDF linked in metadata; text not read) | **needs check** | Montevideo only. National (SUCIVE) not found |
| — | **Chile** — INE / municipal "Permisos de circulación" | primary (municipal) | Per-municipality circulation permits (e.g. Calbuco 2025). 🟢 | datos.gob.cl | Mixed: **PDDL** for some years, **ODbL** for 2022 (same municipality) | **needs check** | No national make/model file found. ANAC is industry (PDF reports) |
| — | **Costa Rica** — Registro Nacional / MOPT | primary | No open dataset found (portal search returned nothing). 🔴 | — | — | **no** | — |

### Tier 5 — watchlist (one line each)

| country | finding | conf. |
|---|---|---|
| India | VAHAN dashboard (MoRTH) is the primary source of make × fuel registrations and is cited by media for e-car figures. It was **unreachable from our proxy** (connection reset), no licence found, and it is a JSF dashboard (scraping only). data.gov.in uses GODL. Keep watching | 🟡 |
| Japan | **Supply source.** Customs trade statistics have a used-BEV code **8703.80-010 ("Used")** by destination country (third-party listing). Customs terms say "商用利用も可能です" (commercial use allowed); attribution rules sit in a 利用規約 page not read. Auction data (USS etc.) is commercial | 🟡 |
| Ethiopia | ICE import ban drives EV imports; no open registration data found | 🔴 |
| Nepal | High EV share of imports; customs data only in reports | 🔴 |
| Sri Lanka | EV import rules change often; no open data found | 🔴 |

## Recommended source per field per market (Tier 3 + best Tier 4)

| field | US | CA | AU | NZ | NO | KR | MY | MX |
|---|---|---|---|---|---|---|---|---|
| Fleet by make/model/year | state registers: **CT** (PD), NY (+vPIC decode, licence check), WA (**ODbL**, keep separate) | none open | **VIC** by model (no fuel); QLD stock (2022) | **NZTA MVR** | SVV dataset (when relaunched); SSB totals | Jeju only | derive from **JPJ transactions** | none (sales only) |
| New registrations by make/model | CT/WA new rows; no federal source | **iZEV** (to 2025) | **VIC monthly**, **QLD new** | **MVR** (first NZ reg date) | SVV (paused) | none | **JPJ** | **INEGI RAIAVL** (sales) |
| Used-market transactions | none | none | **QLD transfers** | MVR import status (used imports) | none | none | none seen | none |
| BEV/PHEV flag | fueleconomy / vPIC via VIN | iZEV engine type | QLD fuel; VIC → model map | MVR motive power (🟡) | SSB fuel | regional fuel files | JPJ `fuel` | model map |
| Specs (range, energy use) | **fueleconomy.gov** | **NRCan FCR** | GVG (licence check) | none (reuse JP/EU/AU specs) | EEA (EU/EEA member, see R-02) 🟡 | none verified | none | none |
| Recalls / complaints | **NHTSA** | not checked | not checked | not checked | — | — | — | — |
| Inspection | none | none | none | none | SVV API (last EU-kontroll, eID) | — | — | — |
| Charging | **AFDC** | **AFDC** | NSW (CC BY) | not verified | NOBIL (check) | not verified | not checked | not checked |
| Import flows | — | — | — | MVR country of origin | — | — | — | RAIAVL country of origin |

## Ranking: which future markets have the best open data

Scored on make/model granularity, EV flag, used-market signal, licence clarity and scriptable access.

1. **New Zealand** 🟢: per-vehicle, monthly, CC BY 4.0, import origin. Same quality as RDW.
2. **Malaysia** 🟢: per-transaction, monthly, CC BY 4.0, Parquet, fuel column.
3. **Israel** 🟡: per-plate with fuel, commercial name, test dates and daily updates. Licence needs checking.
4. **US** 🟢 specs/recalls/charging, 🟡 registrations: federal data is public domain; registrations are a patchwork of states (CT clean, WA ODbL, NY no licence).
5. **Australia** 🟢: VIC + QLD under CC BY 4.0, including used transfers in QLD. No national make/model data, and the specs licence is unclear.
6. **Canada** 🟢: OGL specs plus iZEV make/model (series ended). No open fleet by model.
7. **Mexico** 🟢: INEGI make/model sales, clear commercial-use terms, no EV column.
8. **Singapore** 🟢: make × fuel only; strict visible-attribution rule.
9. **Thailand** 🟡: make × model monthly, no fuel, licence text unread, recency unclear.
10. **Norway** 🟡: open licence, but bulk download is paused and the per-plate API is eID-gated.
11. **Brazil** 🟡/🔴: make/model exists, but CC BY-ND on gov.br and the portal was unreachable.
12. **Colombia, Uruguay, Chile, South Korea, Türkiye** 🟡: totals, fragments or no licence.
13. **Vietnam, Indonesia, Philippines, Jordan, Costa Rica, China** 🔴: no official open make/model data.

**Impact on entry order.** The proposed order (Türkiye → South Korea → Thailand/Malaysia/Indonesia → Brazil/Chile → Mexico → Vietnam → India) puts the **two weakest-data markets first**. Türkiye has no licence on TÜİK and model data only from ODMD; Korea has no national model-level file. If open data decides the order, **Malaysia** and **NZ/Australia** (and the US, for Tier 3) come first. Türkiye and Korea would need partner or commercial data from day one. 🟡 (this is a data view only, not a market-size view)

## Adapters to build next (ranked)

1. **`nzta-mvr`** (NZ): monthly CSV ZIP, CC BY 4.0. Per vehicle, with import origin.
2. **`my-jpj-cars`** (MY): yearly Parquet, CC BY 4.0. Trivial to parse.
3. **`fueleconomy`** (US + good for CA): one CSV, public domain. Best variant-level spec catalogue outside the EEA. Convert units.
4. **`nhtsa-vpic`** (US): VIN → make/model/year decoder. Needed for NY and WA data and useful for listing deep links.
5. **`afdc-stations`** (US + CA charging): CSV/JSON, "any purpose".
6. **`au-states`** (QLD new+transfers, VIC by model + monthly): CKAN CSVs, CC BY 4.0. Needs a model → BEV map.
7. **`nrcan-fcr`** + **`tc-izev`** (CA): OGL-Canada CSVs.
8. **`inegi-raiavl`** (MX): PxWeb API. Needs a model → BEV map.
9. **`ct-dmv-ev`** (US state, public domain) as a template for other Socrata state registers.
10. Only after a licence check: `il-mot-register`, `th-dlt-newreg`, `sg-lta`, `br-renavam`, `svv-kjoretoy` (when bulk returns).

Skip: AFDC registration counts and Argonne (Experian/Wards), OFV, ODMD, ABVE, ANAC, EVC, Gaikindo, VAMA, CPCA/CAAM (industry or commercial).

## Licence red flags

- **Washington State EV population (and sibling WA DOL sets): ODbL.** Share-alike database licence. It must stay in a separate ODbL pipeline (AGENTS.md data rule 3) or be skipped. Use CT (public domain) as the US state template.
- **Brazil gov.br: CC BY-ND 3.0** ("Atribuição-SemDerivações") on the SENATRAN statistics pages. Derived figures could breach ND. Confirm the licence on dados.transportes.gov.br, and email SENATRAN if it is the same.
- **AFDC vehicle registration counts = Experian; Argonne sales = Wards.** These are government pages with commercial data underneath and no licence. Do not ingest.
- **AFDC station terms:** no endorsement, plus a clause where the **user indemnifies DOE/NLR/Alliance**. Low risk, but note it in DECISIONS.
- **Singapore Open Data Licence:** a **conspicuous notice with a link to the licence** must appear in the product, and no implied endorsement.
- **Israel "Other (Open)":** no licence text found. The data also carries full VINs (privacy and re-identification).
- **Thailand "Open Data Common"** and **Uruguay "Licencia de DAG"**: national licences whose text was not read.
- **Chile municipal permits:** PDDL and ODbL mixed for the same publisher across years, so check every file.
- **Colombia datos.gov.co:** many fleet datasets are **CC BY-SA 4.0** (the national RUNT EV set is CC BY 4.0).
- **No licence stated:** NY DMV, CA DMV, NHTSA (only "public information may be distributed or copied"), fueleconomy.gov page (public domain only via the data.gov/EPA record), Norway SVV per-plate API, TÜİK, VAHAN, Green Vehicle Guide.
- **Australia BITRE:** CC BY version differs per edition (2.5 AU vs 3.0 AU), so store the licence per file.

## Sources (retrieved 2026-11-15)

Market evidence
- IEA Global EV Outlook 2026, executive summary: https://www.iea.org/reports/global-ev-outlook-2026/executive-summary ; manufacturing and trade: https://www.iea.org/reports/global-ev-outlook-2026/manufacturing-and-trade 🟢
- ICCT 2025 market figures via newmobility.news: https://newmobility.news/en/2026/05/20/ev-adoption-emerging-markets-overtake-established-leaders/ 🟡
- Türkiye ODMD figures via Daily Sabah: https://www.dailysabah.com/business/automotive/turkish-car-sales-hit-record-in-2025-evs-ascend-further 🟡
- India VAHAN-based CY2025: https://e-vehicleinfo.com/india-ev-car-sales-surge-77-in-cy2025/ 🟡

Norway
- SVV open vehicle dataset (CC BY 4.0, download paused): https://www.vegvesen.no/fag/teknologi/apne-data/et-utvalg-apne-data/api-for-kjoretoyopplysninger/ 🟢
- SVV technical API (eID, key): https://www.vegvesen.no/fag/teknologi/apne-data/et-utvalg-apne-data/api-for-tekniske-kjoretoyopplysninger/ 🟢
- SSB licence (CC BY 4.0): https://www.ssb.no/en/diverse/lisens ; table 07849: https://www.ssb.no/en/statbank1/table/07849/ 🟢

US
- fueleconomy.gov downloads: https://www.fueleconomy.gov/feg/download.shtml ; web services: https://www.fueleconomy.gov/feg/ws/index.shtml ; data.gov record: https://catalog-old.data.gov/dataset/www-fueleconomy-gov ; EPA Data License: https://edg.epa.gov/EPA_Data_License.htm 🟡
- NHTSA terms of use: https://www.nhtsa.gov/about-nhtsa/terms-use ; vPIC API: https://vpic.nhtsa.dot.gov/api/ 🟢
- AFDC data download terms: https://afdc.energy.gov/data_download ; registration counts (Experian): https://afdc.energy.gov/vehicle-registration ; API docs: https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/ 🟢
- Argonne monthly sales (Wards, no make/model since 2019): https://www.anl.gov/node/101331/ ; https://www.anl.gov/ev-facts/model-sales 🟢
- WA EV population (ODbL): https://data.wa.gov/api/views/f6w7-q2d2.json 🟢
- CT EV registrations (Public Domain): https://data.ct.gov/resource/y7ky-5wcz.json (catalogue via https://data.colorado.gov/api/catalog/v1?ids=y7ky-5wcz) 🟢
- NY DMV registrations: https://data.ny.gov/api/views/w4pv-hbkt.json 🟢 (no licence)
- CA DMV fuel type by ZIP: https://data.ca.gov/api/3/action/package_show?id=vehicle-fuel-type-count-by-zip-code 🟢 (no licence)

Canada
- open.canada.ca CKAN (NRCan FCR, iZEV; OGL-Canada): https://open.canada.ca/data/dataset/42986a95-be23-436e-af15-7c6bf292a2e1 🟢

Australia
- BITRE Road vehicles Australia Jan 2026: https://data.gov.au/data/dataset/road-vehicles-australia-january-2026 🟢
- VIC fleet by model / monthly new: https://discover.data.vic.gov.au/dataset/whole-fleet-vehicle-registration-snapshot-by-model , https://discover.data.vic.gov.au/dataset/monthly-new-vehicle-registration 🟢
- QLD new and transfers / stock: https://www.data.qld.gov.au/dataset/vehicle-registration-new-and-transfers-test , https://www.data.qld.gov.au/dataset/vehicle-registrations 🟢
- NSW EV charging: https://data.nsw.gov.au/data/dataset/2-ev-charging-locations 🟢
- Green Vehicle Guide: https://greenvehicleguide.gov.au/Home/About (copyright page timed out) 🔴

New Zealand
- NZTA fleet open data (CC BY 4.0): https://nzta.govt.nz/resources/new-zealand-motor-vehicle-register-statistics/new-zealand-vehicle-fleet-open-data-sets ; catalogue: https://catalogue.data.govt.nz/dataset/motor-vehicle-register-api1 🟢

South Korea
- data.go.kr Jeju per-model register: https://www.data.go.kr/catalog/15128417/fileData.json ; KOTSA DCAT example: https://www.data.go.kr/biz/dcat/metadata/15150261.do ; Seoul fuel counts: https://data.go.kr/catalog/15086025/fileData.json 🟢

Tier 4
- Malaysia JPJ car registrations (CC BY 4.0): https://data.gov.my/data-catalogue/registration_transactions_car ; file https://storage.data.gov.my/transportation/cars_2026.csv 🟢
- Singapore Open Data Licence: https://data.gov.sg/open-data-licence ; Annual Car Population by Make: https://data.gov.sg/datasets/d_20d3fc7f08caa581c5586df51a8993c5/view 🟢
- Thailand DLT first registrations by make/model: https://datagov.mot.go.th/en/dataset/dataset_stat_1_001 , https://datagov.mot.go.th/en/dataset/dataset_stat_1_002 🟢 (licence text unread)
- Israel MoT register: https://data.gov.il/api/3/action/package_show?id=private-and-commercial-vehicles 🟢 (licence "Other (Open)")
- Mexico INEGI RAIAVL: https://www.inegi.org.mx/app/tabulados/pxwebv2/pxweb/es/RAIAVL/RAIAVL/RAIAVL_8_9.px/ ; terms: https://www.inegi.org.mx/inegi/terminos.html 🟢
- Brazil SENATRAN frota (CC BY-ND 3.0 footer): https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/estatisticas-frota-de-veiculos-senatran ; 2026 files: https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/frota-de-veiculos-2026 ; Serpro paid files: https://www.gov.br/pt-br/servicos/contratar-arquivos-estatisticos-denatran 🟢
- Colombia RUNT EV/hybrid (CC BY 4.0): https://www.datos.gov.co/api/views/ntxy-q9ix.json 🟢
- Uruguay Montevideo parque automotor: https://catalogodatos.gub.uy/dataset/intendencia-montevideo-parque-automotor-de-montevideo1 🟢
- Chile municipal permits: https://datos.gob.cl (search "permisos de circulación") 🟢

Tier 5
- Japan Customs terms (commercial use allowed): https://www.customs.go.jp/kiyaku.htm ; trade stats usage: https://www.customs.go.jp/toukei/sankou/howto/riyou.htm ; code 870380010 "Used" (third-party listing): https://treayo.com/en/hs/japan/870380010 🟡
- Jordan EV imports from China (press): https://ammannet.net/english/china-captures-87-jordan’s-electric-vehicle-market-2025 🔴

Blocked during research: VAHAN dashboard (connection reset), dados.transportes.gov.br (tunnel closed), greenvehicleguide.gov.au copyright page (timeout), developer.nrel.gov/docs/terms (robots), data.go.th fuel table (Cloudflare), ofv.no (no content for scripts).
