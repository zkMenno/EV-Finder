# R-28 US and Australia data sources (Phase 4)

**Answer:** The US is easy for specs and hard for open registration counts. Australia is the other way round. 🟢 **fueleconomy.gov** (EPA/DOE) is public domain. One bulk CSV (`vehicles.csv`, 1,684 BEV rows, model years 1998–2027, updated 2026-11-04) gives EPA range, kWh/100 mi, 240 V charge time, motor text and drive type. It has **no battery-kWh field**. 🟢 **NHTSA recalls** are public domain ("U.S. Government Work"). The vPIC VIN decoder is free and rate-limited, but its battery fields were empty in our tests. US state registrations need care:
- 🟢 Washington DOL (the best one: per-vehicle make/model/year, plus a *used-sale* file with odometer and sale price) is **ODbL**, so it has to stay out of our CC BY output until WS0 decides how to handle it.
- 🟢 New York is open (OPEN-NY terms), but it has **no model field**.
- 🟡 California DMV has make only and no named licence.
- 🔴 California CEC ZEV stats **forbid commercial use**.
- 🔴 Texas has PDF reports only.

In Australia:
- 🟢 Queensland TMR (make/model/fuel, new + transfers) and Victoria DTP (fleet + monthly new, by make/model) are **CC BY 4.0**.
- 🟢 The ABS Motor Vehicle Census is CC BY 4.0 but **ceased in 2021**.
- 🔴 The **Green Vehicle Guide is not openly licensed as far as we can tell**: even the NSW Government's VESR site uses GVG data "with permission" under a "personal use only" end-user licence. Treat it as permission-needed.
- 🔴 EVC sales data is copyright with no-redistribution terms.

Checked 2026-11-15. Every link below was opened on that date unless it is marked *not opened*. 🟢 verified on the source / 🟡 reasoned or partly verified / 🔴 unsure, blocked or not open.

---

## 1. United States

### 1.1 fueleconomy.gov (EPA + DOE, run by ORNL)

| Item | Finding | Status |
|---|---|---|
| Web services doc + data dictionary | https://www.fueleconomy.gov/feg/ws/index.shtml (page says "Updated: Wednesday November 04 2026") | 🟢 |
| Bulk download | https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip (2.2 MB zip → 21.9 MB CSV, 50,647 rows, 84 columns). Also unzipped CSV and XML; emissions file linked by `id` | 🟢 downloaded |
| REST API | `/ws/rest/vehicle/{id}` (JSON or XML), menu chain `/ws/rest/vehicle/menu/year → make → model → options` (options returns vehicle ids). No key. | 🟢 |
| Licence | data.gov record for "www.fueleconomy.gov" (https://catalog.data.gov/dataset/www-fueleconomy-gov) points to https://edg.epa.gov/EPA_Data_License.htm. That page says: "Unless otherwise specified, all data produced by the U.S EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C. § 105", with a no-warranty clause. | 🟢 |
| Licence outside the US | 17 U.S.C. § 105 covers *domestic* copyright. The US government can in principle claim copyright abroad, but for factual test data the risk is very low. Credit "Source: fueleconomy.gov (US EPA/DOE)" anyway. | 🟡 reasoned |
| Cadence | The site was updated 2026-11-04, and new model years appear (2027 is already present). Monthly pull is enough. | 🟢 |
| My MPG (user-shared) | `/ws/rest/ympg/shared/...`: user-reported MPG. It is mostly for combustion cars, and owner-shared data could carry other terms. **Don't use.** | 🟡 |

**EV-relevant fields.** These are the actual header names in `vehicles.csv` (2026-11-04 file). Definitions come from the data dictionary on the ws page.

| Field | Dictionary definition | BEV fill rate (n = 1,684) | Note |
|---|---|---|---|
| `id` | vehicle record id | 100 % | Our source key |
| `year` | model year | 100 % | 1998–2027 |
| `make`, `model`, `baseModel` | manufacturer (division); model name (carline); base model name | 100 % | `model` carries the variant ("Model 3 Long Range AWD", "Kona Electric (17 inch Wheels)") |
| `atvType` | type of alt-fuel vehicle; `EV` = electric, `Plug-in Hybrid` | 100 % | Filter `atvType == "EV"` |
| `fuelType`, `fuelType1` | "Electricity" for BEVs | 100 % | Cross-check |
| **`range`** | EPA range, combined (miles) | 100 % | ⚠️ This is the BEV range. It is **in the CSV but missing from the dictionary list**. |
| `rangeCity`, `rangeHwy` | EPA city / highway range (miles) | 1,497 / 1,684 | Decimal values |
| `rangeA`, `rangeCityA`, `rangeHwyA` | "EPA range for fuelType2" | **0 BEV rows** | Used only for dual-fuel vehicles and PHEVs. **Not** the BEV range, despite the task note. |
| **`combE`** | combined electricity consumption, kWh/100 miles | 100 % | Headline consumption |
| `cityE`, `highwayE` | city / highway kWh/100 miles | ≈100 % | The EPA highway cycle is not 120 km/h motorway driving; see §3 |
| `comb08`, `city08`, `highway08` | MPGe for EVs (footnote 11) | 100 % | Skip; it can be derived |
| `charge240` | hours to charge at 240 V | 1,660 | The EV label page says this is time to charge "a fully empty battery using 240 volt electrical service" |
| `charge240b`, `c240Dscr`, `c240bDscr` | alternate charger time; charger descriptions | `c240Dscr` 141 rows, mostly "standard charger" | Only 8 rows have "x.x kW charger" text |
| `charge120` | hours at 120 V | mostly 0 | Skip |
| `evMotor` | electric motor (kW), free text | 1,627 parseable, 49 "TBD" | e.g. "84 and 191 kW ACPM 3-Phase", "150 kW PMSM (IPM)". These are per-motor ratings, **not system power**. |
| `drive` | drive axle type | 100 % | AWD 955, RWD 299, FWD 187, 4WD 130, Part-time 4WD 91, 2WD 14 |
| `VClass` | EPA size class | 100 % | US classes ("Small Sport Utility Vehicle 4WD") |
| `hlv`, `hpv`, `lv2`, `lv4`, `pv2`, `pv4` | luggage / passenger volume, cubic feet | cars only (footnote 8: not for SUVs, vans, trucks) | Not comparable with VDA litres; don't map to `boot_l` |
| `createdOn`, `modifiedOn` | record dates | 100 % | Use `modifiedOn` as the fact's source date |
| `feScore`, `ghgScore`, `co2TailpipeGpm`, `fuelCost08`, `youSaveSpend` | scores and costs | 100 % | US-specific; skip |

**Not in the data (🟢 checked against the header):** battery capacity (kWh), DC fast-charge power or time, weight, dimensions, 0–60 time, price. The source matrix lists fueleconomy.gov as a 0–100 km/h fallback. That is wrong for the CSV, so drop it.

### 1.2 NHTSA

| Source | Finding | Status |
|---|---|---|
| Recalls API | `https://api.nhtsa.gov/recalls/recallsByVehicle?make=&model=&modelYear=`. Tested with Tesla Model 3 2019: 22 results. Fields: `Manufacturer, NHTSACampaignNumber, parkIt, parkOutSide, overTheAirUpdate, ReportReceivedDate, Component, Summary, Consequence, Remedy, Notes, ModelYear, Make, Model`. No key. | 🟢 |
| Recalls licence | data.gov record "Recalls Data" (https://catalog.data.gov/dataset/recalls-data) gives the licence as https://www.usa.gov/government-works (US Government Work, public domain), last updated 2026-11-14. | 🟢 |
| Recalls bulk | Flat files are listed on data.gov ("ODI Recalls/Complaints flat file"); I saw the record names in search results but did not open them. | 🟡 not opened |
| vPIC VIN decoder | `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json`. Returns `Make, Model, ModelYear, ElectrificationLevel, FuelTypePrimary, BodyClass`. Battery fields exist (`BatteryKWh, BatteryType, BatteryV, ChargerLevel, ChargerPowerKW, EVDriveUnit`) but were **empty** for a Tesla and a Leaf test VIN. A standalone DB download is offered. | 🟢 |
| vPIC terms | The API page says "Users/Applications attempting to use vPIC APIs will be controlled by an automated traffic rate control mechanism". There is no separate licence on the page. It is a federal work, so public domain under 17 U.S.C. § 105. | 🟡 licence reasoned, rate limit 🟢 |
| Use for us | Recalls: per model-year "known issues" on generation pages. vPIC: only if a user enters a US VIN later. Not a spec source. | |

### 1.3 State registration open data

| State | Dataset | What it has | Licence | Status |
|---|---|---|---|---|
| **WA** | Electric Vehicle Population Data, https://data.wa.gov/api/views/f6w7-q2d2.json (Socrata id `f6w7-q2d2`) | One row per registered BEV/PHEV: `vin_1_10, county, city, state, zip_code, model_year, make, model, ev_type, cafv_type, electric_range, legislative_district, dol_vehicle_id, electric_utility, _2020_census_tract`. Monthly; current file is "registered as of September 30, 2026" and the rows were updated 2026-10-14. Note: "Electric Range is no longer maintained for BEVs … Zero (0) will be entered". Base MSRP was dropped in Dec 2025. | **ODbL 1.0** (metadata `licenseId: ODBL`), attribution "Washington State Department of Licensing" | 🟢 |
| **WA** | Electric Vehicle Title and Registration Activity, `rpr4-cgyd` | Per transaction: `new_or_used_vehicle, sale_price, date_of_vehicle_sale, odometer_reading, transaction_type, model_year, make, model, electric_range, county…`. **This is the only open source we found with used-EV sale prices plus mileage.** | ODbL 1.0 | 🟢 |
| WA | 9 more DOL EV datasets (by county, size history, share of new registrations, most common models…) | Aggregates | All ODbL 1.0 | 🟢 |
| **NY** | Vehicle, Snowmobile, and Boat Registrations, https://data.ny.gov/api/views/w4pv-hbkt.json | Per vehicle: `make, model_year, body_type, fuel_type, zip, county, reg_valid_date…`. **No model field.** Monthly; updated 2026-11-03. Also "Electric Vehicles per County" (`uu25-czyc`). | OPEN-NY Terms of Use (PDF https://data.ny.gov/download/77gx-ii52/application%2Fpdf, last modified 2013-03-08): no attribution or share-alike required; use must be lawful. Not an SPDX licence. | 🟢 terms read; low value (make only) |
| **CA** | DMV "Vehicle Fuel Type Count by Zip Code", https://data.ca.gov/dataset/vehicle-fuel-type-count-by-zip-code | Annual snapshot: `Date, ZIP Code, Model Year, Fuel, Make, Duty, Vehicles`. **No model.** | No licence set; the CKAN `rights` field says "No Restrictions on Public Use" | 🟡 |
| CA | CEC ZEV and Infrastructure Statistics, https://www.energy.ca.gov/zevstats | New ZEV sales and population by make/model (DMV data cross-referenced by VIN). Dashboards. | CEC Conditions of Use (https://www.energy.ca.gov/conditions-of-use): "free for public use … provided the Energy Commission is credited", **but** "Use or modification of these materials or information for commercial or profit-making purposes is prohibited". | 🔴 Not usable on an affiliate-funded site without written OK. Fixes the 🟢 in data-sources.md. |
| **TX** | TxDMV "Alternatively Fueled Vehicle Report" FY2025 (PDF) https://www.txdmv.gov/sites/default/files/report-files/FY_2025_Alternatively_Fueled_Vehicle_Report.pdf | Annual counts by fuel type. No per-model open dataset found. Atlas EV Hub lists a Texas ZIP-level CSV compiled by Dallas-Fort Worth Clean Cities (https://www.atlasevhub.com/materials/state-ev-registration-data/), but Atlas has a User License Agreement and login, so I did not open it. | Unclear | 🔴 |
| Other | CARB's copy of fueleconomy.gov on data.ca.gov ("Vehicle Fuel Economy", Other (Public Domain)) | Duplicate of 1.1; ignore | — | 🟢 |

**ODbL consequence (Data rule 3).** WA counts or used prices cannot go into our CC BY release as they stand. Options for WS0:
- (a) Use them internally only, for cross-checks and the QA back-test.
- (b) Publish a separate ODbL "US registrations" dataset/page with attribution, with no derived values flowing into the CC BY variant table.
- (c) Publish only "Produced Works" (charts or text) that cite DOL. Under ODbL §4.5 these don't trigger share-alike, but it needs a decision.

Recommended: (a) now, (b) at the Phase 4 launch.

---

## 2. Australia

| Source | Finding | Licence | Status |
|---|---|---|---|
| **Green Vehicle Guide** (DITRDCSA), https://www.greenvehicleguide.gov.au/ | The site works (home page and FAQ opened). Vehicle pages give lab energy use (kWh/100 km) and electric range. I **found no bulk download or API link** on the home page; a "User login | Register" exists. | **Copyright page not readable**: https://www.greenvehicleguide.gov.au/Home/Copyright returned an empty reply to curl, and the fetch tool permission timed out, so *not opened*. Indirect evidence (🟢 opened): the NSW Government's VESR site (https://vesr.gov.au/vehicle/mg-zs-ev-suv-2022) says "The Green Vehicle Guide data has been used with permission from the copyright owner … Limited End-user licence: You may print and reproduce views … for your personal use only." | 🔴 Treat as **permission needed**, not CC BY 4.0. Ask the department for a data licence (draft email for Menno). |
| VESR (Vehicle Emissions Star Rating, NSW DCCEEW) | Repackages GVG data with star ratings | © NSW plus GVG permission notice above | 🔴 Don't use |
| **Queensland TMR**, "Vehicle Registration New and Transfers", https://www.data.qld.gov.au/dataset/vehicle-registration-new-and-transfers-test | Transaction records 2016–2026 (22 resources, updated 2026-09-07): make, model, body type, colour, **fuel type**, year of manufacture, transaction type (new / transfer), customer type, LGA. Also "Vehicle registration transfers—by year" (make, model, body shape). | **CC BY 4.0** (CKAN `CC-BY-4.0`) | 🟢 licence. 🟡 columns: taken from the description; the CSV and field-descriptor downloads returned HTTP 202 with no body (bot check?). Retry from the pipeline with a plain UA and backoff. |
| **Victoria DTP**, "Whole Fleet Vehicle Registration Snapshot by Model" (quarterly, to Q3 2026) and "Monthly New Vehicle Registration", via https://discover.data.vic.gov.au | Fleet: `CD_MAKE_VEH1, CD_MODEL_VEH, CD_CLR_BDY_VEH_P, TOTAL1`. Monthly new: `CD_MAKE_VEH, CD_MODEL_VEH, CD_CLR_BDY_VEH_P, NB_YEAR_MFC_VEH, TOTAL`. **No fuel field**, so EVs have to be picked out by model name (most AU EV model names are unique). | **CC BY 4.0** | 🟢 |
| **NSW TfNSW**, "Vehicle Registration Statistics", https://data.nsw.gov.au/data (dataset `2-transport-nsw-vehicle-registration-statistics`; resources on opendata.transport.nsw.gov.au) | Monthly counts of registrations, transactions, usage and age, 25 resources. I did **not** find a make/model/fuel breakdown in the resource names. | "Creative Commons Attribution" (version not stated in CKAN) | 🟡 low value |
| **ABS Motor Vehicle Census**, https://www.abs.gov.au/statistics/industry/tourism-and-transport/motor-vehicle-census-australia/latest-release | Final release: reference date 31 Jan 2021, published 30/06/2021. "This release has ceased". EV counts by type (23 thousand EV registrations). Historic only. | ABS site: CC BY 4.0 (https://www.abs.gov.au/website-privacy-copyright-and-disclaimer), excluding microdata and third-party content | 🟢 |
| BITRE Motor Vehicle Census (ABS replacement, from NEVDIS) | ABS says BITRE and Austroads are building a replacement. bitre.gov.au refused our connection (HTTP/2 error), so *not opened*. | Unknown | 🔴 check later |
| **Electric Vehicle Council**: monthly "EVC Vehicle Sales Report" (https://electricvehiclecouncil.com.au/evc-vehicle-sales-report/) and State of EVs 2026 PDFs (https://electricvehiclecouncil.com.au/state-of-evs-2026) | Monthly deliveries by model (subscription); annual report PDFs | Subscription terms: "EVC has and will retain all title to … copyright", subscriber "shall not distribute, reproduce or copy the reports … without the prior written permission of the EVC". I found no open licence for the State of EVs PDFs. | 🔴 Cite single headline figures with a link at most; no data import |
| NSW "Experimental EV use estimates (ABS)" | ABS one-off from 2019-20 SMVU (released 2021) | CC BY | 🟢 historic, background only |

**Gap:** Australia has no open, licence-clean spec source (range, kWh/100 km) unless GVG grants permission. Fallbacks: Open EV Data (already active) for specs, plus maker AU pages cited fact by fact.

---

## 3. Field map: fueleconomy.gov → our fields

Constants: 1 mi = 1.609344 km. Then:

- kWh/100 km = kWh/100 mi ÷ 1.609344
- Wh/km = kWh/100 km × 10 = kWh/100 mi × 6.2137

| fueleconomy.gov | Our field | Rule | Confidence |
|---|---|---|---|
| `atvType == "EV"` | row filter | Skip `Plug-in Hybrid` (out of scope) | 🟢 |
| `id` | `source_ref` on every Fact | e.g. `fueleconomy:47908` | 🟢 |
| `year` | model year → variant `year_start` / `year_end` matching | Many US model years map to one generation; match through WS1 matching rules | 🟢 |
| `make`, `baseModel`, `model` | matching keys | `baseModel` → model; `model` text (trim, wheels, motors) → variant hint. Unmatched rows go to the review queue (rule 5). | 🟡 |
| `range` (mi) | **`epa_range_km`** | `round(range × 1.609344)` → 342 mi → **550 km** | 🟢 |
| `rangeCity`, `rangeHwy` (mi) | proposed `epa_range_city_km`, `epa_range_hwy_km` (not in schema) | × 1.609344 | 🟢 data, needs schema request |
| `combE` (kWh/100 mi) | proposed **`consumption_epa_kwh_100km`** (Wh/km in UI) | `combE / 1.609344` → 25.84 → **16.05 kWh/100 km = 160.5 Wh/km**. **Do not** write it to `consumption_kwh_100km` (WLTP). | 🟢 conversion. 🟡 basis: I believe EPA measures energy from the wall, charging losses included (SAE J1634), but the label page I opened only says "how many kilowatt-hours the vehicle would use to travel 100 miles". |
| `cityE`, `highwayE` | proposed `consumption_epa_city_…`, `consumption_epa_hwy_…` | same conversion. EPA highway ≠ 120 km/h motorway: never feed `consumption_motorway_kwh_100km` directly, only as a model input | 🟡 |
| `charge240` (h) | proposed `ac_full_charge_h` (info only) | Do not derive `ac_kw`: there is no battery kWh and the losses are unknown | 🟢 |
| `c240Dscr` | `ac_kw` | Only when it matches `^(\d+(\.\d+)?) kW charger$` (8 BEV rows); else null | 🟢 |
| `evMotor` | `power_kw` (fallback only) | Parse kW numbers. For one motor use that value. For "A and B kW", **don't sum** into system power: store as `motor_kw_text` and send to review. | 🟡 |
| `drive` | `drivetrain` | `Front-Wheel Drive`→`fwd`; `Rear-Wheel Drive`→`rwd`; `All-Wheel Drive`, `4-Wheel Drive`, `4-Wheel or All-Wheel Drive`, `Part-time 4-Wheel Drive`→`awd`; `2-Wheel Drive`→null (review) | 🟢 |
| `VClass` | `body` / `segment` hint only | "Pickup", "SUV", "Station Wagon" give useful body hints. Size classes are US interior-volume classes, not EU segments. Low confidence; never primary. | 🟡 |
| `hlv`/`lv4` (ft³) | none | × 28.3168 = litres, but SAE method and cars only, so not comparable with `boot_l` | 🟢 decision |
| `modifiedOn` | Fact `source_date` | Parse "Sun Aug 25 00:00:00 EDT 2024" | 🟢 |
| — | `battery_kwh_net` | **Not available.** `range × combE/100` gives wall energy (overstates usable kWh), so don't derive it | 🟢 |

**Schema request (to WS0):** the schema has no EPA consumption field. Add `consumption_epa_kwh_100km` and, optionally, `epa_range_city_km` / `epa_range_hwy_km` and `ac_full_charge_h`. `field_sources.yaml` already has `epa_range_km: {primary: [fueleconomy]}` 🟢. Remove `fueleconomy` from the `accel_0_100_s` fallbacks in the source matrix (no such field).

Encoding: the CSV read cleanly as Latin-1 / UTF-8 compatible text in Python's `csv` module.

---

## 4. Ready-to-import `data/sources.yaml` rows

The first two **replace** the existing `fueleconomy` and `nhtsa` rows; the rest are new. Under the yaml's own rule, "(to confirm)" rows stay `blocked`.

```yaml
  - {id: fueleconomy, name: fueleconomy.gov vehicles.csv + web services, owner: US EPA / US DOE (ORNL), licence: US-Government-Public-Domain, access: bulk, cadence: monthly, status: active,
     terms: "EPA Data License (edg.epa.gov/EPA_Data_License.htm, via data.gov record): public domain under 17 USC 105, no warranty. Credit 'fueleconomy.gov (US EPA/DOE)'. BEV range is column `range` (not rangeA). No battery kWh. Checked 2026-11-15."}
  - {id: nhtsa, name: NHTSA recalls API, owner: US NHTSA, licence: US-Government-Public-Domain, access: api, cadence: weekly, status: active,
     terms: "api.nhtsa.gov/recalls/recallsByVehicle; data.gov licence usa.gov/government-works. No key. Checked 2026-11-15."}
  - {id: nhtsa-vpic, name: NHTSA vPIC VIN decoder, owner: US NHTSA, licence: US-Government-Public-Domain (to confirm), access: api, cadence: ad hoc, status: blocked,
     terms: "Federal work; no licence on API page. Automated rate control. Battery fields usually empty. Only needed for US VIN lookup later."}
  - {id: wa-dol-ev, name: Washington State Electric Vehicle Population Data, owner: Washington State Department of Licensing, licence: ODbL-1.0, access: api, cadence: monthly, status: blocked,
     terms: "data.wa.gov f6w7-q2d2 (+ rpr4-cgyd used-sale/odometer, other DOL EV sets). ODbL: never mix into CC BY output (Data rule 3). Blocked for release until WS0 decides internal-only vs separate ODbL output. Internal cross-checks OK."}
  - {id: ny-dmv-reg, name: NY DMV Vehicle Registrations, owner: New York State DMV, licence: OPEN-NY-Terms-2013, access: api, cadence: monthly, status: active,
     terms: "data.ny.gov w4pv-hbkt. OPEN-NY Terms: no attribution or share-alike required, lawful use only. Make + fuel type only, no model field. Credit 'NYS DMV' anyway."}
  - {id: ca-dmv-fuel, name: California DMV Vehicle Fuel Type Count by ZIP, owner: California DMV, licence: none named (rights 'No Restrictions on Public Use') (to confirm), access: bulk, cadence: yearly, status: blocked,
     terms: "data.ca.gov vehicle-fuel-type-count-by-zip-code. Make only, no model. Confirm licence with data.ca.gov before release."}
  - {id: cec-zev, name: California Energy Commission ZEV statistics, owner: California Energy Commission, licence: none (commercial use prohibited), access: manual, cadence: quarterly, status: blocked,
     terms: "energy.ca.gov Conditions of Use forbid commercial or profit-making use without written approval. Needs permission."}
  - {id: txdmv-afv, name: TxDMV Alternatively Fueled Vehicle Report, owner: Texas DMV, licence: unknown (to confirm), access: manual, cadence: yearly, status: blocked,
     terms: "PDF only, fuel-type counts, no model breakdown."}
  - {id: au-gvg, name: Australian Green Vehicle Guide, owner: Australian Government DITRDCSA, licence: none (permission needed) (to confirm), access: manual, cadence: monthly, status: waiting_permission,
     terms: "No bulk download or API found. Copyright page not readable 2026-11-15. NSW VESR uses the data 'with permission' under a personal-use end-user licence. Ask the department for a data licence."}
  - {id: qld-tmr-reg, name: Queensland vehicle registrations (new and transfers), owner: Queensland Department of Transport and Main Roads, licence: CC-BY-4.0, access: bulk, cadence: yearly, status: active,
     terms: "data.qld.gov.au vehicle-registration-new-and-transfers-test (+ transfers by year). Make, model, fuel type, year, new/transfer. Attribution: 'Queensland Government (TMR), CC BY 4.0'. Downloads returned HTTP 202 to curl; retry with backoff."}
  - {id: vic-dtp-reg, name: Victoria vehicle registration snapshots, owner: Victoria Department of Transport and Planning, licence: CC-BY-4.0, access: bulk, cadence: quarterly, status: active,
     terms: "discover.data.vic.gov.au whole-fleet snapshot by model (quarterly) + monthly new registrations. No fuel field: identify EVs by model. Attribution: 'State of Victoria (DTP), CC BY 4.0'."}
  - {id: tfnsw-reg, name: Transport for NSW vehicle registration statistics, owner: Transport for NSW, licence: CC-BY (version to confirm), access: bulk, cadence: monthly, status: blocked,
     terms: "Aggregate counts; no make/model/fuel breakdown found. Low value; confirm CC BY version if used."}
  - {id: abs-mvc, name: ABS Motor Vehicle Census (ceased), owner: Australian Bureau of Statistics, licence: CC-BY-4.0, access: manual, cadence: ceased (last 31 Jan 2021), status: active,
     terms: "Historic context only. ABS website material is CC BY 4.0 except microdata and third-party content."}
  - {id: bitre-mvc, name: BITRE Motor Vehicle Census (NEVDIS), owner: Bureau of Infrastructure and Transport Research Economics, licence: unknown (to confirm), access: manual, cadence: yearly, status: blocked,
     terms: "ABS replacement product. Site not reachable 2026-11-15; check licence later."}
  - {id: evc, name: Electric Vehicle Council sales report and State of EVs, owner: Electric Vehicle Council (AU), licence: none, access: manual, cadence: monthly, status: blocked,
     terms: "Subscription terms: EVC keeps copyright; no distribution or reproduction without written permission. Cite single figures with a link only."}
```

---

## 5. Open items and follow-ups

1. **WS0 decision:** ODbL handling for WA DOL. Recommend internal-only now and a separate ODbL output at Phase 4 launch. The used-sale and odometer file is valuable for US used-price bands.
2. **WS0 schema request:** `consumption_epa_kwh_100km` (+ optional city/hwy range, `ac_full_charge_h`).
3. **Menno (later, drafted by WS5):** a permission or licence request to the Green Vehicle Guide team. A request to CEC only if California sales data is ever needed.
4. **Retry when unblocked:** the GVG copyright page, BITRE census page, QLD CSV downloads, Atlas EV Hub licence, and the NHTSA recall flat-file records.
5. **Fix in docs/spec/data-sources.md §US/AU (WS0 owns it):** CEC "citation requested 🟢" should be 🔴 (commercial use prohibited). WA "Public 🟢" should be "ODbL 🟢". fueleconomy "US government data 🟡" should be "public domain 🟢".
6. The web-search budget ran out during this task. GVG licence wording and BITRE were not searched further.
