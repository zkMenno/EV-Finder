# Data sources

The human-readable table of the sources our pipeline imports. The machine registry is
`data/sources.yaml` (coordinator-owned); ids, licences and status here must match it.
Adapters live in `pipeline/ev_pipeline/sources/<id>/`. Each `fetch` writes raw data plus
`_fetch.json` (fetch time, query, licence text seen) to the git-ignored `data/raw/<id>/`.
Each `normalise` writes `data/staging/<id>.records.jsonl` and appends one line to
`data/staging/runlog.jsonl`. Every record carries its `Source` with the licence.

Last run: 2026-11-15 (UTC; the run log shows 2026-11-14T23:5x, just before midnight).

| id | Name | URL | Licence (exact, as found) | Attribution line | How we use it | Tonight | Rows |
|---|---|---|---|---|---|---|---|
| `openev` | Open EV Data | https://github.com/open-ev-data/open-ev-data-dataset | **CDLA-Permissive-2.0**: repo `LICENCE` file, "Community Data License Agreement - Permissive - Version 2.0" | Contains data from OpenEV Data (open-ev-data-dataset), CDLA-Permissive-2.0. | Specs per variant: battery, WLTP/EPA range, AC/DC kW, 10–80 % time and average, power, 0–100, top speed, boot/frunk, dimensions, weight, towing, seats, voltage, chemistry, cooling, warranty; EUR/GBP list prices for NL/DE/FR/BE/UK. Confidence medium (OEM/regulatory sources) or low. | **Live**: `git clone --depth 1` at commit `8edb266d` | 1,449 files → 1,229 records (1,189 vehicles + 40 DE price records). Fixture: 37 |
| `rdw` | RDW Open Data | https://opendata.rdw.nl/d/m9d7-ebf2 | **CC0-1.0**: Socrata metadata `license.name = "Public Domain"` (`licenseId PUBLIC_DOMAIN`); `metadata.custom_fields.Licentie = "Creative Commons 0 (CC0)"` | Bron: RDW Open Data (opendata.rdw.nl), CC0. | Count of registered battery-electric passenger cars in NL per make × trade name × year of first admission (confidence high). Plus spec records (confidence medium) per the same group: WLTP range (km) and consumption (kWh/100km) from the fuel table `8ys7-d773` via a 10 % plate sample, and NL catalogue price (`catalogusprijs`, EUR incl. VAT + BPM, cars sold new in NL) as a server-side median. Wide (IQR > 5 % of median) or small (< 5 cars) groups emit nothing. | **Live**: grouped SoQL (counts, price) + 10 % plate sample of both tables joined in memory (~40 requests, 1 s apart, ~4 min); plates never stored | 3,124 count records (922,990 cars) + 1,849 spec records: WLTP range 740, consumption 743, price 366. Dropped for spread: range 233, consumption 191, price 680; for small groups: 502 / 400 / 791. Fixture: 118 counts + 81 price groups + 86 sample groups |
| `eea` | EEA CO2 monitoring of new cars (Reg. 2019/631) | https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b | **CC-BY-4.0**: EEA SDI metadata record `b4044b06-2e6b-4f8e-a6e6-66e0e98bb0dd` (2025, provisional), use limitation: "License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: Directorate-General for Climate Action (DG-CLIMA)." Same text on the 2022–2024 records. | Contains data from the European Environment Agency, CO2 emissions from new passenger cars (Regulation (EU) 2019/631). Copyright holder: Directorate-General for Climate Action (DG CLIMA). CC BY 4.0. | New BEV registrations (`Ft = 'electric'`) per country × make × commercial name for NL/DE/FR/BE, year 2025 (provisional table `co2cars_2025Pv31`), confidence medium. Registration-weighted type-approval mass (kg), consumption (Z, Wh/km → kWh/100km) and electric range (Zr, km) as spec facts, confidence low. | **Live**: grouped SQL, POSTed to Discodata | 1,733 groups → 3,430 records (1,715 counts + 1,715 spec averages; 18 DE groups without make/name dropped). Counts: NL 159,006 · DE 544,418 · FR 339,849 · BE 142,114. Fixture: 68 |
| `nyland` | Bjørn Nyland range/charging tests | (not recorded: the URL lives only in the `NYLAND_SHEET_CSV_URL` env var) | **none**: permission pending | Bjørn Nyland test results (permission pending; local use only). | Importer skeleton for real-world range, consumption, usable kWh and 10–80 % average kW. Confidence high (exact tests). **Permission pending: local cache only, never in the repo, fixtures or releases.** Fetch → `data/local/nyland/`; normalise → `data/local/nyland/records.jsonl`, never `data/staging/`. | **Not run**: no URL, no permission | 0. Tests use an invented CSV ("Testcar Alpha"): 3 records |
| `kba-fz10` | KBA FZ10 new registrations by make and model series | https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz10/fz10_gentab.html | **dl-de/by-2-0**: Impressum sheet of each file, "Nutzungsbedingungen: © Kraftfahrt-Bundesamt, Flensburg / Datenlizenz Deutschland - Namensnennung - Version 2.0" | © Kraftfahrt-Bundesamt, Flensburg. Datenlizenz Deutschland – Namensnennung – Version 2.0 (FZ10, Neuzulassungen nach Marken und Modellreihen). | New BEV registrations in DE ("mit Elektroantrieb (BEV)" column) per Marke × Modellreihe, **year-to-date**: Jan–Oct 2026 (`fz10_2026_10`) and the full year 2025 (`fz10_2025_12`). Year = data year. Confidence high. | **Live**: two .xlsx downloads (Nov 2026 file not out yet, so Oct 2026 is newest) | 423 records (2026: 221, 2025: 202). BEV 2026 Jan–Oct 695,069 emitted + 3,161 "SONSTIGE" = 698,230 = KBA grand total; 2025: 540,884 + 4,258 = 545,142. Fixture: 30 |
| `dft-veh` | DfT vehicle licensing statistics, df_VEH0120_UK | https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files | **OGL-UK-3.0**: gov.uk page footer "All content is available under the Open Government Licence v3.0, except where otherwise stated" (no exception for these files) | Contains public sector information licensed under the Open Government Licence v3.0 (Department for Transport, vehicle licensing statistics). | Licensed (not SORN) battery-electric **cars** in the UK fleet at the end of the newest quarter (2026 Q2), per Make × GenModel × Model (model = GenModel, variant_name = DVLA Model). Fleet stock, so year is empty. Confidence high. | **Live**: URL resolved via the gov.uk content API; UK file 41 MB in about 2 s | 1,551 records (312 GenModels), 2,015,027 cars; 1,941 more in "MODEL MISSING" rows dropped (total 2,016,968). Fixture: 30 |
| `ademe` | ADEME – Car Labelling | https://data.ademe.fr/datasets/ademe-car-labelling | **Licence-Ouverte-2.0**: data-fair metadata `license.title = "Licence Ouverte / Open Licence"` (etalab link) | ADEME – Car Labelling, Licence Ouverte | `Energie = ELECTRIC` rows: best-case WLTP consumption (kWh/100km) and range (km), mass without driver (kg) per Marque × Modèle × Description commerciale; FR list price (EUR) as separate records. No power (nominal only), no year. Confidence medium. | **Live**: one CSV (1.1 MB) | 134 BEV rows → 79 distinct versions → 158 records (79 spec + 79 price). Fixture: 62 |
| `kilowatt-openev` | Open EV Data (KilowattApp) | https://github.com/KilowattApp/open-ev-data | **MIT-with-attribution**: repo `LICENSE`, "MIT License with Attribution Requirement", Copyright (c) 2024 Tijs Teulings; clause 2 requires clear and visible attribution | Open EV Data (https://github.com/KilowattApp/open-ev-data) | Fallback specs per car: usable kWh, AC kW, DC peak kW, average consumption (kWh/100km), confidence medium. DC curves (SoC %, kW) as separate `#dc_curve` records, status `estimated`, confidence low. Default, template and placeholder curves dropped. **Visible attribution required on the web About/credits page.** | **Live**: `git clone --depth 1` at commit `32d7dc59` (upstream data dated 2025-04-12), v2 format | 1,321 vehicles (1,282 cars) → 1,427 records (1,282 spec + 145 curves). Curves: 145 kept, 407 default, 292 template, 438 placeholder dropped. Fixture: 14 vehicles → 17 records |

## Notes per source

**openev.** Records are compiled the way `docs/ARCHITECTURE.md` describes:
`base.json` ← year base ← variant (objects deep-merge; arrays and scalars replace).
`record_key` is the list of layer files, joined with `+`. Some upstream files break the
`<vehicle>_<variant>` naming rule (Audi Q4/Q8 Sportback variants, Audi A6 `a6_e_tron.json`).
We attach those to the longest year-base file whose name prefixes theirs, or to `base.json`
alone if there is none. The data has no WLTP `efficiency` block and no `dc_charge_curve`, so
we emit no consumption and no curves from OpenEV. 21 vehicles (XPeng) have a 10–80 % time.
Prices exist only in USD/BRL/AUD/CNY and EUR for DE, so we keep only the 40 DE prices.
Variant files inherit their year base's price when they don't set their own (the upstream
merge rule).

**rdw.** The fuel type is in dataset `8ys7-d773`, and Socrata refuses joins ("joins are not
supported"). We therefore count in `m9d7-ebf2` alone, using a proxy:
`voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL AND datum_eerste_toelating >= 20100101`.
We checked it on 2026-11-15 against `8ys7-d773` with 1,000 random rows each way:
- 998/1,000 proxy rows are BEVs (one fuel-cell car, one petrol).
- 554/554 BEV passenger cars from the fuel table are proxy hits.

Year = year of first admission anywhere, so imports count from their foreign first
registration. Trade names are raw and messy (`NISSAN LEAF 40KWH`, `ID.3 PRO 150 KW`):
matching (T-005) maps them to models.

*Specs (added 2026-11-15, coverage-gaps findings 3 and 4).* Same grouping, merk ×
handelsbenaming × year of first admission, written into each record_key as
`[merk|handelsbenaming|jaar]`. Spec records have confidence medium, one field per record, with a
`registered_count` weight = the cars behind the median.
- **NL catalogue price** = `m9d7-ebf2.catalogusprijs`. RDW definition (Beschrijving dataset
  gekentekende voertuigen v5.4): "De catalogusprijs is gebaseerd op informatie van de
  importeur en is als volgt berekend: netto-catalogusprijs, verhoogd met de BTW en de BPM";
  legally required since 1 July 2005 and the basis for the bijtelling. So EUR, incl. VAT and
  BPM (BEVs paid no BPM before 2025). It is per car, so trims and factory options spread it.
  Only cars sold new in NL count (`datum_eerste_toelating = datum_eerste_tenaamstelling_in_nederland`),
  so used imports don't mix in. Median and count are exact, server-side (`median()`).
- **WLTP** = `8ys7-d773.actie_radius_enkel_elektrisch_wltp` (km) and
  `elektrisch_verbruik_enkel_elektrisch_wltp` (Wh/km, emitted as kWh/100km = Wh/km ÷ 10).
  Socrata metadata: "Actieradius / Electrisch verbruik gemeten bij een op een rollenbank
  rijdend puur elektrisch voertuig tijdens een rit volgens de WLTP test onder gecombineerde
  belasting". (The RDW PDF swaps the two descriptions; values show which is which: median
  162 = Wh/km.) The fuel table has no make, and joins are refused, so we use a fixed 10 %
  plate sample (`kenteken like '___7%'`, 9–10 % of BEVs in every year 2015–2026), fetch only
  plate + needed columns from both tables, join in memory, and store only per-group value
  histograms (never plates). Empty for NEDC-era cars.
- **Spread rule.** Interquartile range from the sample. IQR > 5 % of the median, or fewer than
  5 cars: no value for that field, counted in the run log (`dropped_wide_spread`,
  `dropped_small_sample`, with examples). Price may skip the sample check when the full
  group's min and max are within 5 %. A group where ~75 % of cars share one value passes; the
  median is then that car's real value, not a blend.

**eea.** The Discodata WAF (Azure Application Gateway) answers HTTP 403 to many GET queries
with quoted literals, but the same SQL POSTed as a form body works. That's why the adapter
POSTs. The table name is a constant in the adapter: bump it when the final 2025 table
(or the 2026 provisional one) appears. The UK is not in the EU data. `fetch` refuses to run
if the SDI metadata no longer states CC BY 4.0.

**kba-fz10.** One record = YTD BEV registrations for the file's year, so the newest file
(Jan to month) and last year's December file (whole year) never overlap and can be summed
per model. The adapter checks each file's sum: emitted + "SONSTIGE" = the
"NEUZULASSUNGEN INSGESAMT" row (run log `sums_match`). Model series are coarse and shared
with ICE models: the BEV column under (our reading, to confirm in matching) `BMW | X1` is the iX1, `BMW | 4ER` the i4,
`AUDI | A6` the A6 e-tron, `CITROEN | C3` the ë-C3, `MERCEDES | GLK, GLC` the GLC with EQ
technology, `MINI | MINI` Cooper E/SE. Some rows join two models (`VW | ID.4, ID.5`).
`fetch` refuses a file whose Impressum no longer names the Datenlizenz Deutschland.

**dft-veh.** VEH0120 is a quarter-end stock table, not registrations; the latest quarter
column is picked from the header. GenModel names carry the make (`TESLA MODEL 3`,
`VOLKSWAGEN ID3`, `MERCEDES EQA CLASS`) and are shared with ICE models where the BEV has no
own name (`HYUNDAI KONA`, `KIA NIRO`, `PEUGEOT 2008`, `VAUXHALL MOKKA`, `MINI COOPER`):
the counts are BEV-only because we filter on `Fuel`. DfT labels a few fuel-cell buses
"Battery electric"; cars look clean.

**ademe.** Each version has a WLTP Min/Max (the two ends of its interpolation family). We
emit the best case only (lowest consumption, highest range), never an average. Some names
cover several cars (`RENAULT | MEGANE | MEGANE (55Kw)` holds 40 and 60 kWh cars): those
become separate records (`#1`, `#2` in the key), so the merge sees the conflict. "Poids à
vide" = "Masse OM" − 75 kg on every electric row, so it excludes the driver. The file holds
only 134 BEV rows and many look old (ZOE, Honda e, e-Niro, Corsa-e 57 kW): treat it as a
partial snapshot, not the current French market. Makes are written `B.M.W.` and `M.G.`;
some descriptions are double-encoded UTF-8 and are repaired.

**kilowatt-openev.** Attribution is a licence condition, not a courtesy: the web
About/credits page must show "Open EV Data (https://github.com/KilowattApp/open-ev-data)"
(clause 2 of the LICENSE), and the copyright notice + licence text must ship with any copy
of the data (clause 1). `fetch` refuses to import if the LICENSE no longer contains the
attribution clause. We read `data/v2/` (same 1,321 vehicles and ids as v1 `ev-data.json`).
Upstream does not document how curves were obtained and its tool generates template curves,
so nothing is `measured`; some records point at ev-database.org (Q-047). Dropped:
`is_default_charging_curve: true` curves; unflagged curves shaped exactly like the two
generic templates; DC data where max_power equals usable kWh (a 1C placeholder on 567 cars);
AC > 43 kW; consumption outside 10–40 kWh/100km; motorbikes and microcars (Q-048).
`charging_voltage` (400/800) is an architecture label, not a nominal voltage, so it is not
emitted as `voltage_nominal_v`; no schema field holds it yet.
