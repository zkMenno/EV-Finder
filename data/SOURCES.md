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
| `rdw` | RDW Open Data | https://opendata.rdw.nl/d/m9d7-ebf2 | **CC0-1.0**: Socrata metadata `license.name = "Public Domain"` (`licenseId PUBLIC_DOMAIN`); `metadata.custom_fields.Licentie = "Creative Commons 0 (CC0)"` | Bron: RDW Open Data (opendata.rdw.nl), CC0. | Count of registered battery-electric passenger cars in NL per make × trade name × year of first admission. Confidence high. | **Live**: one grouped SoQL query, no row-level download | 3,124 groups → 3,124 records, 922,990 cars. Fixture: 118 |
| `eea` | EEA CO2 monitoring of new cars (Reg. 2019/631) | https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b | **CC-BY-4.0**: EEA SDI metadata record `b4044b06-2e6b-4f8e-a6e6-66e0e98bb0dd` (2025, provisional), use limitation: "License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: Directorate-General for Climate Action (DG-CLIMA)." Same text on the 2022–2024 records. | Contains data from the European Environment Agency, CO2 emissions from new passenger cars (Regulation (EU) 2019/631). Copyright holder: Directorate-General for Climate Action (DG CLIMA). CC BY 4.0. | New BEV registrations (`Ft = 'electric'`) per country × make × commercial name for NL/DE/FR/BE, year 2025 (provisional table `co2cars_2025Pv31`), confidence medium. Registration-weighted type-approval mass (kg), consumption (Z, Wh/km → kWh/100km) and electric range (Zr, km) as spec facts, confidence low. | **Live**: grouped SQL, POSTed to Discodata | 1,733 groups → 3,430 records (1,715 counts + 1,715 spec averages; 18 DE groups without make/name dropped). Counts: NL 159,006 · DE 544,418 · FR 339,849 · BE 142,114. Fixture: 68 |
| `nyland` | Bjørn Nyland range/charging tests | (not recorded: the URL lives only in the `NYLAND_SHEET_CSV_URL` env var) | **none**: permission pending | Bjørn Nyland test results (permission pending; local use only). | Importer skeleton for real-world range, consumption, usable kWh and 10–80 % average kW. Confidence high (exact tests). **Permission pending: local cache only, never in the repo, fixtures or releases.** Fetch → `data/local/nyland/`; normalise → `data/local/nyland/records.jsonl`, never `data/staging/`. | **Not run**: no URL, no permission | 0. Tests use an invented CSV ("Testcar Alpha"): 3 records |

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

**eea.** The Discodata WAF (Azure Application Gateway) answers HTTP 403 to many GET queries
with quoted literals, but the same SQL POSTed as a form body works. That's why the adapter
POSTs. The table name is a constant in the adapter: bump it when the final 2025 table
(or the 2026 provisional one) appears. The UK is not in the EU data. `fetch` refuses to run
if the SDI metadata no longer states CC BY 4.0.
