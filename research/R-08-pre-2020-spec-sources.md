# R-08 — Open spec sources for pre-2020 used EVs (Q-007, T-052)

## Question

Our base spec sources (OpenEV Data, KilowattApp Open EV Data) are thin before 2020, so the 2010–2020 cars most bought used (Leaf ZE0/ZE1, Zoe ph1/ph2, i3 60/94/120 Ah, Ioniq 28/38, e-Golf, Soul EV, Kona/e-Niro 2018–20, Model S/X pre-2020, Model 3 2019–20, e-208/Corsa-e 2020, Mini SE 2020, Honda e, I-Pace, e-tron 2019, EQC) run on hand-entered `seed-manual` values with low confidence. Which open sources with a **named licence** give per-variant specs for them: battery kWh (usable/gross), WLTP/NEDC/EPA range, consumption, AC/DC kW, dimensions, weight? For each: licence, coverage, fields, granularity, and whether values are per configuration or averages.

All checks were live requests on 2026-11-15, one at a time with pauses. No code was written and nothing was committed. Confidence: 🟢 verified today, 🟡 reasoned or partly verified, 🔴 unsure or not reachable.

## Answer (short)

- **Best source: RDW type-approval (TGK) datasets** 🟢. Licence is **CC0 / Public Domain**. They hold one row per **type approval × variant × version (uitvoering) × revision**, and that includes **foreign approvals** (e2 = France for the Zoe, e1 = Germany for the i3/e-tron/EQC, e11 = UK for the Leaf/I-Pace, e4 = NL for Tesla/Hyundai/Kia, e6 = BE for the Honda e). Fields: **NEDC electric range and consumption** (pre-WLTP cars), **WLTP range and consumption as best/worst bounds** (the interpolation family), 30-minute power, length/width/height/wheelbase, mass in running order and empty mass, seats, top speed. All 17 target models were found. There is **no battery kWh and no AC/DC charging power**.
- **Second source: EEA CO2 monitoring, per TAN/Va/Ve** 🟢 (CC BY 4.0, every year 2010–2025 checked in SDI). From 2017 the data is **one row per registered car**. It uses the **same type-approval keys as RDW** (`Ve` = RDW `codeuitvoeringtgk`), so the two sources cross-check exactly. Per-car WLTP range `Zr` only starts in **2020**. `Z (Wh/km)` exists from 2010, but before 2020 it mixes NEDC and WLTP values without a flag. Mass, wheelbase and track width are filled. `Ep` (power) is unreliable.
- **US/Canada official ratings** 🟢: **fueleconomy.gov** (public domain) and **NRCan** (OGL-Canada, metric, kWh or Ah written in the model name). Per model year × trim from 2011/2012, EPA range and consumption, motor kW. They cover the US-sold cars only (no Zoe, e-208, Corsa-e, Honda e or EQC).
- **No open official source gives battery kWh or AC/DC charging kW** for these cars. That gap stays with KilowattApp (which does have about 366 rows ≤2020, some with errors), maker documents (Q-008) or permission-based sources. 🟡
- Weak or no-go: ADEME historical labelling 2001–2015 (Licence Ouverte, but **no EV range or consumption fields**), Wikidata (CC0, sparse, model-level only), UK VCA (licence contradicts itself), Green Vehicle Guide AU (licence page blocked by robots.txt), GitHub datasets (no licence, or CC0 with unsourced values), Euro NCAP (not open).

## Source details

### 1. RDW TGK — type-approval register (NL, includes EU approvals from other countries) 🟢

| item | finding |
|---|---|
| Datasets | `gr7t-qfnb` TGK Energiebron Uitvoering (82 cols), `byxc-wwua` TGK Basis Uitvoering (48), `x5v3-sewk` TGK Handelsbenaming Fabrikant (7), `4by9-ammk` TGK Aandrijving Uitvoering (16), `kyri-nuah` TGK Merk Uitvoering, `9s6a-b42z` Intrekking, plus the glossary `gska-f75a` (PDF "Begrippenlijst typegoedkeuringsregister", 12 March 2024). All updated 2026-11-14. |
| Licence | Socrata metadata for `gr7t-qfnb` etc.: `"license": {"name": "Public Domain"}`, attribution "Team Open Data RDW". RDW bijsluiter: CC0 (see R-02, including the clause that reusers may not say the data comes from RDW, Q-037). Same host and licence as our active `rdw` source. 🟢 |
| Key | `typegoedkeuringsnummer` + `codevarianttgk` + `codeuitvoeringtgk` + `volgnummerrevisieuitvoering` (+ `volgnummerenergiebron`). The per-plate table `m9d7-ebf2` carries the same `typegoedkeuringsnummer`, `variant` and `uitvoering`, so NL cars map exactly to TGK rows. |
| Energy fields (`gr7t-qfnb`, `codeenergiebron='E'`) | `elektrischeactieradiusnedc` (km), `elekverbruikgecombineerdnedc` (Wh/km), `actieradiusvolledigelekwltpogr`/`bgr` (km), `verbruikvolledigelekwltpogr`/`bgr` (Wh/km), `maximumvermogen30minogr`/`bgr` (kW, 30-minute power, **not** peak), `maximumnettovermogen*` (peak power, filled on only 541 of 233,638 E rows), `maximumconstructiesnelheid*`. |
| Meaning of ogr/bgr | Glossary: for WLTP range, Bgr = "De hoogste van alle ondergrenzen…" and Ogr = "De laagste van alle bovengrenzen…". For consumption, Ogr = lowest lower bound and Bgr = highest upper bound. **In practice Ogr is the best case (vehicle Low) and Bgr the worst case (vehicle High) of the WLTP interpolation family**: e.g. Zoe `e2*2007/46*0251*13` `MBLEA0300000`: range 316 / 295 km, 169 / 182 Wh/km. Some rows look swapped (I-Pace 480/420), so the adapter must check order. 🟡 |
| Base fields (`byxc-wwua`) | length, width, height, wheelbase (lower/upper bounds), `massarijklaar*` (mass in running order), `massaledig*` (empty mass), `maximummassa*`, seats, doors, top speed, road-load coefficients f0/f1/f2, `begindatumrevisieuitvoering`/`einddatum…`. Zoe `MALEA0400000`: 4085 × 1730 × 1562 mm, wheelbase 2588, running-order 1548 kg, revision from 2018-10-05. 🟢 |
| Granularity | **Per version (uitvoering)**, i.e. per type-approved configuration. These are approval values, not averages. Several commercial trims can share one version. |
| Size | 6,326,032 rows in all of `gr7t-qfnb`. 233,638 with `codeenergiebron='E'` (this includes PHEV electric rows, motorbikes and revisions). Of those, 16,629 have NEDC range, 29,531 NEDC consumption and 19,622 WLTP range. |
| Coverage test (TANs found by trade name in `x5v3-sewk`, first 80 TANs per name) | **Leaf** 28 TANs, NEDC rows (199 km/150 Wh/km; 250 km/150) and WLTP rows (e.g. 287–300) · **i3** 34 TANs, NEDC 190/129, 300/131, 312/126 …, WLTP 230–245, 270–285, 285–310 · **Ioniq** NEDC 280/115 (28 kWh), WLTP 280/311 (38 kWh, few rows) · **e-Golf** NEDC rows present, but my name filter also matched GTE PHEVs and showed **no WLTP rows** · **Soul EV** NEDC 212/143, 250/143 · **Kona** NEDC 289/150, 449/154, 484/147 and WLTP 440–510 · **e-Niro** WLTP 289 and 455 only (2 rows), no NEDC · **Model S/X** 1,743 / 1,460 NEDC rows (e.g. 363/208, 414/185, 467/217) · **Model 3** 370 WLTP rows (430–455, 498–525, 565–600 …) · **Corsa-e** WLTP 307–332, 313–349 · **Mini SE** WLTP 196–234 … · **Honda e** WLTP 199–215 · **I-Pace** NEDC 415/248 and WLTP · **e-tron** WLTP 1,362 rows (e.g. 328–385) · **EQC** NEDC 411–420/219–226 and WLTP 348–445 · **Zoe** every phase: R240 22 kWh NEDC 240 km/133 Wh/km (`AGVYB0`), ZE40 NEDC 403/133 (`YE0`), Q90/R110, ph2 WLTP per version. **e-208**: the TGK trade name is probably "208", not "E-208". Reach it through the plate → TAN route (🟡 not tested). |
| Gaps | No battery kWh, no AC/DC charge power, no peak power (only 30-min). NEDC consumption on some early rows is per row and can differ between versions of one TAN (Zoe `YA0` 146 vs `YA1` 163 Wh/km). That is real data (wheel/trim), not an average. |

### 2. EEA CO2 monitoring of new cars (Reg. 443/2009 → 2019/631), per type approval 🟢

| item | finding |
|---|---|
| Licence | Each SDI record "Monitoring of CO2 emissions from passenger cars, YYYY – Final data" for **2010–2024 final and 2025 provisional**: "License CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Copyright holder: Directorate-General for Climate Action (DG-CLIMA)." Checked all years today (UUIDs in Sources). 🟢 |
| Access | Discodata SQL, POST form body (the WAF blocks GET, see data/SOURCES.md). The all-years table `[CO2Emission].[latest].[co2cars]` holds 2010–2022P (filter `Year`, `Status`, `Version_file`). 2020–2025 also have their own tables (`co2cars_2020Fv22` …). |
| Granularity | **2010–2016: aggregated rows** (one row per MS × Mk × Cn × Va × Ve × values, with count `R`). **2017 onward: one row per registered car** (`R = 1`; 2018 has 15.27 M rows, 150,534 of them BEV). So per-version values can be read directly. Use `GROUP BY TAN, Va, Ve` and never average across versions. 🟢 |
| BEV rows (final) | 2010: 329 rows/5,602 cars · 2013: 1,206/24,225 · 2015: 2,028/56,816 · 2017: 43,448 · 2018: 150,534 · 2019: 344,986 · 2020: 726,758 · 2021: 999,649. |
| Field fill for BEVs | `Z (Wh/km)`: 2010 15/329 rows, 2014 970/1,471, 2016 2,184/2,599, 2018 123,547/150,534, 2019 211,075/344,986. **`Zr` (electric range): 0 before 2020**, then 425,146/726,758 (2020) and 814,219/999,649 (2021). `M (kg)` and `W (mm)`: nearly 100 %. `Mt` (WLTP test mass) from 2018. `TAN` missing in 2010. 🟢 |
| Per-car WLTP | From 2020, `Zr` and `Z` are **per individual car** inside the interpolation family. Zoe `MDLEA0800000` in 2020 shows Zr 352–395 km and Z 172–195 Wh/km, depending on `Mt`. The family's best case = max Zr / min Z, which should match RDW TGK Ogr (395 vs RDW, not tested). 🟢 |
| NEDC vs WLTP | **Before 2020, `Z` has no test-procedure flag.** Leaf 40 kWh 2018: Z = 206 (WLTP-like). Ioniq 2018: 115 and e-Golf 2018: 127 (NEDC-like). Leaf 24 kWh 2014: 150/173. Rule: before 2020, use `Z` only as corroboration, or only when `Mt`/`Ewltp` show the row is WLTP. 🟡 |
| Other fields | `Mk`, `Cn` (messy free text: "NISSAN LEAF 40KWH", "LEAF TEKNA", "Model 3"), `Mh/Man`, `Ct`, `W (mm)`, `At1/At2` (track), `Ep (KW)`, `Fm`, `IT`. **`Ep` is unusable as power**: the same version is reported as 25/88 kW (Ioniq), 65/100/150/340 kW (Model 3) by different member states. |
| Coverage | Every BEV sold new in the EU/EEA (plus UK until 2020): Zoe, e-208, Corsa-e, Honda e and EQC included. UK-only RHD versions are in until 2020. |
| Gaps | No battery kWh, no charging, no length/width/height (wheelbase and track only), no WLTP range before 2020. `M` = mass in running order (Q-039). |

### 3. fueleconomy.gov — EPA/DOE vehicles dataset (US) 🟢

| item | finding |
|---|---|
| Licence | No licence on the download page. The data.gov record links the EPA Data License: "Unless otherwise specified, all data produced by the U.S EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C. § 105" (https://edg.epa.gov/EPA_Data_License.htm, read today). Already `active` in sources.yaml. 🟢 (🟡 that it reaches the fueleconomy file only through data.gov) |
| File | `https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip` (2.2 MB zip, CSV dated 2026-11-04, 84 columns). |
| Fields for BEVs (`atvType = EV`) | `year`, `make`, `model` (trim/pack often in the name: "Leaf (30 kW-hr battery pack)", "i3 BEV (94 Amp-hour battery)", "Model S AWD - 85D", "Model 3 Long Range Performance AWD (19in)"), `evMotor` (kW text), `range` (mi), `combE`/`cityE`/`highwayE` (kWh/100 mi, **wall-to-wheel incl. charging loss**), `charge240` (hours at 240 V), `c240Dscr` (e.g. "6.6 kW charger"), `drive`, `VClass`, `baseModel`. **No battery kWh field, no DC power, no dimensions or mass.** |
| Granularity | Per model year × trim/option as certified. Not averages, but one rating can cover several trims. |
| Coverage 2010–2020 | 217 EV rows. Leaf 2011–2020 (24/30/40/62 kWh, SV/SL), i3 2014–2020 (60/94/120 Ah, i3s), Ioniq Electric 2017–2020, e-Golf 2015–2019, Soul EV 2015–2020, Kona 2019–2020, Niro 2019–2020, Model S 2012–2020 (~60 rows, every pack), Model X 2016–2020, Model 3 2017–2020, Mini SE 2020, I-Pace 2019–2020, e-tron 2019–2020, Bolt. **Missing: Zoe, e-208, Corsa-e, Honda e, EQC** (never sold in the US). |
| Caveat | EPA 5-cycle range is lower than NEDC/WLTP. It goes into `epa_range_km` (already in field_sources.yaml), never into WLTP. US variants can differ from EU ones (Leaf 2013+ US was built in the US; the 6.6 kW charger option). Units are imperial, so convert at ingestion (Rule 6). |

### 4. NRCan Fuel consumption ratings — battery-electric vehicles 2012–2026 (Canada) 🟢

| item | finding |
|---|---|
| Licence | CKAN `98f1a129-f628-4ce4-b24d-6f16bf24dd64`: "Open Government Licence - Canada". Licence text: "You are free to: Copy, modify, publish, translate, adapt, distribute or otherwise use the Information in any medium… for any lawful purpose. You must… Acknowledge the source…". Attribution: "Contains information licensed under the Open Government Licence – Canada." 🟢 |
| File | `my2012-2026-battery-electric-vehicles.csv` (2026-09-29, 1,250 rows, redirect via open.canada.ca; EN and FR versions). |
| Fields | Model year, Make, Model (pack in the name: "LEAF (24 kWh)", "LEAF (30 kWh)", "i3 (120 Ah)", "LEAF S PLUS"), Vehicle class, **Motor (kW)**, City/Highway/Combined **kWh/100 km**, Le/100 km, **Range (km)**, CO2, ratings, **Recharge time (h)**. |
| Coverage | 180 rows ≤ 2020. Same set as the US (i3, Soul EV, Leaf 24/30/40/62, Ioniq, Kona, Niro, e-Golf, I-Pace, e-tron 55 …). Same EPA test basis, already metric. |
| Use | A second agreeing source for `epa_range_km` and EPA consumption, and **evidence** for matching to a pack (kWh/Ah in the name). The name's kWh is a label, not a measured usable capacity, so it must not become `battery_kwh_*` directly (🟡). |

### 5. KilowattApp Open EV Data (already `active`) 🟡

Not new, but it changes the Q-007 premise. `data/ev-data.json` has **1,321 vehicles, about 366 with `release_year` ≤ 2020** (2013: 13, 2016: 23, 2018: 22, 2019: 82, 2020: 153). Pre-2020 entries include i3 60/94/120 Ah (18.8 / 27.2 / 37.9 kWh usable), Ioniq 28 and 38.3, Kona 39.2/64 with 7.2 or 11 kW AC, e-tron 50/55, I-Pace 84 kWh, Honda e 28.5, and Leaf/Zoe/Model S. It is the only open source with **usable kWh plus AC/DC kW** for these cars. Quality warning: **45 pre-2020 rows have AC max power equal to the battery size** (e.g. "i3 94 Ah 2017: 27.2 / 27.2 / 27.2"), which looks like a fallback or entry error. The adapter should reject those rows with a rule check (AC kW > 22 on a car without a 43 kW AC option, or AC = battery kWh). `release_year` is a release year, not a model-year span. 🟢 (counts) / 🟡 (quality)

### 6. ADEME historical car labelling 2001–2015 (data.gouv.fr) 🟢 licence, low value

"Emissions de CO2 et de polluants des véhicules commercialisés en France" (ADEME, dataset `53ba4c07a3a729219b7bead3`, licence `fr-lo` Licence Ouverte). One zip per year 2001–2015 (e.g. `fic_etiq_edition_40-mars-2015.csv`). BEVs are listed (`energ = EL`, e.g. BMW i3, CNIT/TVV codes), but **energy consumption and range are empty for EVs**. Only `puiss_heure` (30-min power), `masse_ordma_min/max` and the CNIT/TVV keys are present. The current `ademe-car-labelling` on data.ademe.fr has no revision history ("uniquement accessibles pour les jeux de données éditables", HTTP 501), so **2016–2020 snapshots are missing**. Only mass for FR-sold versions is worth taking. 🟢

### 7. Wikidata (CC0, already `active`) 🟢 licence, 🔴 usefulness

The SPARQL test on 15 models (P2073 range, P4140 energy storage capacity, P2067 mass) returned: Leaf has P4140 24/30/40/62 with no qualifiers tying them to years or variants, Model 3 range 215/346 with no basis, I-Pace mass 2208, EQC 2425, Honda e range 205/222. Zoe, i3, e-Golf, Soul, e-tron, e-208 and Mini had nothing. Model-level only and unqualified, so keep it for names and years as Decision 009 says.

### 8. UK VCA Car fuel data 🔴

https://carfueldata.vehicle-certification-agency.gov.uk/ (download page `downloads/default.aspx`, an ASP.NET form; file list not reachable by script). The licence contradicts itself: the site footer says "© Crown copyright" and links the National Archives crown-copyright page (usually OGL v3), while the data.gov.uk record `car-fuel-data-co2-and-vehicle-tax-tools` says **"Creative Commons Attribution"** (no version). The disclaimer says the data is "provided by manufacturers on a voluntary basis". Fields and EV coverage were **not verified**. Hold until the licence is confirmed. It would mostly duplicate EEA/RDW for UK cars anyway.

### 9. Green Vehicle Guide (Australia) 🔴

The copyright page `https://www.greenvehicleguide.gov.au/Home/Copyright` is **disallowed by robots.txt**, so it was not read. There is no data.gov.au record. R-06 already lists it as "no licence stated". No-go unless the department confirms a licence.

### 10. GitHub datasets 🔴

GitHub search ("electric vehicle specifications dataset", "ev dataset battery capacity range" …): almost all repos have **no licence** (Kaggle copies, student projects, often scraped from ev-database.org, so Rule 2 forbids them). The one CC0 hit, `mohitk24/ev-warranty-us-dataset` (1,117 rows, 2010–2025, gross/usable kWh, DC kW), cites URLs for warranty and chemistry but **not for capacity**, and the data file wasn't at the README path. Its capacity values have unknown origin, so it is unusable under Rule 1. `open-ev-data/open-ev-data-dataset` shows "NOASSERTION" on GitHub. We use it under CDLA-Permissive-2.0 from its LICENCE file (already verified).

### 11. Euro NCAP 🔴

Not open (already `blocked` in sources.yaml). Not re-checked.

## Coverage matrix (target models × sources)

✓ = found today with the fields named · p = partial · – = not covered · ? = not tested

| model | RDW TGK (NEDC / WLTP / dims+mass) | EEA per version (Z / Zr / M) | fueleconomy (EPA) | NRCan (EPA) | KilowattApp (kWh, AC/DC) |
|---|---|---|---|---|---|
| Leaf ZE0 (24/30) | ✓ NEDC / – / ✓ | Z (NEDC) / – / ✓ | ✓ 2011–17 | ✓ | p |
| Leaf ZE1 (40/62) | ✓ / ✓ / ✓ | Z (WLTP-like 2018–19), Zr 2020 / ✓ | ✓ | ✓ | p |
| Zoe ph1 (22/41) | ✓ NEDC per version / – / ✓ | Z / – / ✓ | – | – | p |
| Zoe ph2 (52) | – / ✓ / ✓ | Zr 2020+ per car | – | – | p |
| i3 60/94/120 Ah | ✓ / ✓ / ✓ | Z / Zr 2020 | ✓ (by Ah) | ✓ (by Ah) | ✓ |
| Ioniq 28 / 38 | ✓ NEDC / p WLTP | Z / Zr 2020 | ✓ | ✓ | ✓ |
| e-Golf | p NEDC (filter caught GTE too), no WLTP | Z / Zr 2020 | ✓ 2015–19 | ✓ | ? |
| Soul EV (PS) | ✓ NEDC / p | Z | ✓ 2015–19 | ✓ | ? |
| Kona 2018–20 | ✓ / ✓ | Z / Zr 2020 | ✓ 2019–20 | ✓ | ✓ |
| e-Niro 2018–20 | – / p (2 rows) | Z / Zr 2020 | ✓ (Niro EV) | ✓ | ? |
| Model S/X pre-2020 | ✓ NEDC (many) / p | Z / – (pre-2020) | ✓ every pack | ✓ | p |
| Model 3 2019–20 | – / ✓ (370 rows) | Z 2019 / Zr 2020 | ✓ | ✓ | ? |
| e-208 2020 | ? (name is "208"; use plate → TAN) | Zr 2020 | – | – | ? |
| Corsa-e 2020 | – / ✓ | Zr 2020 | – | – | ? |
| Mini SE 2020 | p / ✓ | Zr 2020 | ✓ | ? | ? |
| Honda e | – / ✓ | Zr 2020 | – | – | ✓ |
| I-Pace | ✓ / ✓ (check bound order) | Z / Zr 2020 | ✓ | ✓ | ✓ |
| e-tron 2019 | p / ✓ (1,362 rows) | Z 2019 / Zr 2020 | ✓ | ✓ | ✓ |
| EQC | ✓ / ✓ | Z 2019 / Zr 2020 | – | – | ? |

No row has an open, official battery kWh or DC kW value. 🟢 for what was tested; "?" cells were not tested.

## Ranked recommendation

1. **RDW TGK (`rdw` source, new `tgk` sub-adapter)**: CC0, per type-approved version, foreign approvals included, NEDC **and** WLTP bounds, dimensions, both masses. It covers the most targets and fills the "WLTP missing on 98 of 195 rows" gap (coverage-gaps.md #3) with NEDC values clearly labelled for older cars. It also resolves the shared-year ambiguity (coverage-gaps #6), because each NL plate points to one version. 🟢
2. **EEA per TAN/Va/Ve** (Q-039 option b): CC BY 4.0, same keys as RDW, so it gives a **second agreeing source** per version, and it is the only source for versions never registered in NL. Use `Zr`/`Z` from 2020 (per car, so take family best and worst). Before 2020, use `Z` only as corroboration unless the row is WLTP. 🟢
3. **fueleconomy.gov + NRCan** for the `epa_range_km` and EPA-consumption fields (US/CA market labels), with the kWh/Ah in the model name as matching evidence. Two agreeing official sources on the same test basis. 🟢
4. **KilowattApp pre-2020 rows** stay the source for usable kWh and AC/DC kW, but behind a rule check (reject AC = battery). Battery and charging otherwise wait on Q-008 (maker documents) or permission (Fastned, Nyland). 🟡
5. ADEME 2001–2015 for FR mass only. Wikidata for names and years only. VCA, Green Vehicle Guide, GitHub datasets and Euro NCAP are no-go for now. 🔴

**Answer to Q-007 (suggested):** RDW TGK + EEA per-version cover range, consumption, dimensions and mass for pre-2020 cars under CC0 / CC BY 4.0. fueleconomy + NRCan add EPA figures. Battery capacity and charging have no open official source. Keep KilowattApp (checked by rules) and leave the rest empty rather than fill it from memory.

## Adapter plan (for T-052; no code here)

**A. `rdw` TGK sub-adapter (lane `pipeline/ev_pipeline/sources/rdw`)**
1. Server-side grouped query on `m9d7-ebf2` (existing BEV proxy filter): `typegoedkeuringsnummer, variant, uitvoering, merk, handelsbenaming, year(datum_eerste_toelating), count(*)`. That gives the NL BEV version list (no join needed).
2. For those TANs (batched `in (...)`, ≤ 80 per query, 1 s apart), fetch `gr7t-qfnb` (`codeenergiebron='E'`), `byxc-wwua` and `x5v3-sewk`. Keep the newest `volgnummerrevisieuitvoering` and its start/end dates.
3. Emit per version: `nedc_range_km`, `nedc_consumption_wh_km`, `wltp_range_km` (best = Ogr, worst = Bgr, order checked), `wltp_consumption` (best/worst), `length_mm`, `width_mm`, `height_mm`, `wheelbase_mm`, `mass_running_order_kg` and `kerb_mass_kg` (from `massaledig*`, the empty mass, not running order minus 75), `seats`, `top_speed_kmh`, `power_30min_kw` (evidence only). Upper ≠ lower bound on a dimension → emit nothing for that field.
4. Record key `[TAN|variant|uitvoering|rev]`. Confidence high for single-valued fields, medium for interpolation bounds.
5. **Schema lane (coordinator)**: there is no NEDC field and no running-order mass field today (`ev.schema.json` has `wltp_km`, `epa_km`, `kerb_mass_kg`, `weight_kg`). Add `nedc_range_km`, `nedc_consumption_wh_km`, `wltp_range_km_worst` (or a min/max pair) and `mass_running_order_kg` before building (log in DECISIONS). NEDC must never fill `wltp_range_km` (data rule: no mixed bases).

**B. EEA per-version (Q-039 option b; lane `pipeline/ev_pipeline/sources/eea`)**
- One grouped POST per year: `GROUP BY Mk, Cn, TAN, Va, Ve, Year` with `SUM(R)`, `MIN/MAX(Zr)`, `MIN/MAX([Z (Wh/km)])`, `MIN/MAX([M (kg)])`, `MIN/MAX([W (mm)])`, `COUNT(Mt)`. 2010–2019 from `[co2cars]` (`Status='F'`, `Version_file`), 2020+ from the year tables.
- Emit WLTP only for 2020+. Before 2020, emit `Z` as `corroboration` only, unless `COUNT(Mt) = SUM(R)`. Never emit `Ep`.
- Join to RDW TGK on `TAN + Va + Ve` (same codes: EEA `Ve = 'MDLEA0800000'` ↔ RDW `codeuitvoeringtgk`). Agreement within tolerance → 2 sources.

**C. `fueleconomy` (existing) + new `nrcan-fcr` adapter**
- fueleconomy: filter `atvType = 'EV'`, `year ≤ 2020` too (it may already, so check). Convert mi→km and kWh/100 mi→kWh/100 km. Parse kWh/Ah from `model` as **matching evidence**.
- NRCan: one CSV (OGL-Canada, host `open.canada.ca`, needs a sources.yaml entry). Fields: `epa_range_km`, EPA consumption, motor kW (evidence). Match on make + normalised model + model year through a **config alias table** (`data/taxonomy/…`), e.g. "LEAF (30 kWh)" → `nissan-leaf-ze0` 30 kWh variant. The US Bolt EV and Soul EV are separate rows.

**D. Matching to our variants**
- Generation by make/model aliases + year (existing matcher).
- Variant by **spec fingerprint, not by name**: in the NEDC era, the NEDC range + 30-min power + mass pick the pack (e.g. Zoe NEDC 240 km = 22 kWh R240, 403 km = Z.E. 40). The fingerprint → variant map lives in config with a source note, and ambiguous versions go to `data/review/unmatched.csv`.
- Tests: fixtures of a few TGK rows (Zoe ph1/ph2, i3 94 Ah, Leaf 40, Model S 85, Model 3 SR+) and EEA grouped rows. No live calls.

**E. Still open after this**: battery kWh (usable/gross) and AC/DC kW before 2020 → KilowattApp with rule checks, plus Q-008 (maker documents) and permission requests. Peak power: RDW per-plate `netto_max_vermogen_elektrisch` (one motor on dual-motor cars, see rdw adapter) or maker documents.

## Sources (retrieved 2026-11-15)

- RDW Socrata catalogue, TGK datasets and columns: https://api.eu.socrata.com/api/catalog/v1?domains=opendata.rdw.nl&q=TGK 🟢
- RDW TGK Energiebron metadata ("Public Domain"): https://opendata.rdw.nl/api/views/gr7t-qfnb.json ; data: https://opendata.rdw.nl/resource/gr7t-qfnb.json 🟢
- RDW TGK Basis / Handelsbenaming / Aandrijving: https://opendata.rdw.nl/resource/byxc-wwua.json , …/x5v3-sewk.json , …/4by9-ammk.json 🟢
- RDW Begrippenlijst TGK-datasets (PDF, 12 maart 2024): https://opendata.rdw.nl/api/views/gska-f75a/files/23d0c3be-5a56-4652-a4d0-9adc4e110a43?download=true 🟢
- RDW bijsluiter (CC0): https://www.rdw.nl/over-rdw/dienstverlening/open-data/bijsluiter (via R-02) 🟢
- RDW per-plate fuel table fields: https://opendata.rdw.nl/resource/8ys7-d773.json 🟢
- EEA Discodata SQL: https://discodata.eea.europa.eu/sql (tables `[CO2Emission].[latest].[co2cars]`, `co2cars_2020Fv22`) 🟢
- EEA SDI records (CC BY 4.0, DG CLIMA), final data: 2010 `baa86df2-86b4-4339-b709-25d9b20f9301`, 2011 `665f2a8b-2993-4071-92f5-dde5a47dfd42`, 2012 `5380e9bd-18e9-4bf9-b26b-f985f2c5f99e`, 2013 `b9de889e-1434-4a8f-a93a-c17ef6a07527`, 2014 `af267be7-eebd-4c1a-ba24-b10a51201f47`, 2015 `770aa0a5-83ce-4663-93fa-78507f1990d6`, 2016 `1129c5fc-5af5-4c8f-b31e-dc740bd6e0f3`, 2017 `0a8985f6-af2d-44b7-ac88-a749da19a155`, 2018 `b319cb95-2c93-4635-8177-e5e0e4f48c1b`, 2019 `a0da862c-0bed-460f-808a-0bae489b12b9`, 2020 `47a7277f-d111-47ba-8438-d669b1057b6d`; via https://sdi.eea.europa.eu/catalogue/srv/api/search/records/_search 🟢
- fueleconomy.gov vehicles data: https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip ; download page https://www.fueleconomy.gov/feg/download.shtml 🟢
- EPA Data License: https://edg.epa.gov/EPA_Data_License.htm 🟢
- NRCan Fuel consumption ratings (OGL-Canada): https://open.canada.ca/data/api/action/package_search?q=fuel%20consumption%20ratings%20battery%20electric ; BEV CSV https://open.canada.ca/data/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64/resource/026e45b4-eb63-451f-b34f-d9308ea3a3d9/download/my2012-2026-battery-electric-vehicles.csv 🟢
- Open Government Licence – Canada: https://open.canada.ca/en/open-government-licence-canada 🟢
- KilowattApp Open EV Data: https://raw.githubusercontent.com/KilowattApp/open-ev-data/master/data/ev-data.json 🟢
- ADEME historical labelling (Licence Ouverte): https://www.data.gouv.fr/datasets/emissions-de-co2-et-de-polluants-des-vehicules-commercialises-en-france ; 2015 file https://static.data.gouv.fr/resources/emissions-de-co2-et-de-polluants-des-vehicules-commercialises-en-france/20151015-121340/ 🟢
- ADEME Car Labelling (current; no revisions): https://data.ademe.fr/data-fair/api/v1/datasets/ademe-car-labelling 🟢
- Wikidata SPARQL: https://query.wikidata.org/sparql 🟢
- UK VCA: https://carfueldata.vehicle-certification-agency.gov.uk/ ; disclaimer https://www.vehicle-certification-agency.gov.uk/fuel-consumption-co2/car-fuel-data-co2-and-vehicle-tax-tools-disclaimer/ ; data.gov.uk record https://ckan.publishing.service.gov.uk/api/action/package_show?id=car-fuel-data-co2-and-vehicle-tax-tools 🟡
- Green Vehicle Guide copyright (robots.txt disallowed, not read): https://www.greenvehicleguide.gov.au/Home/Copyright 🔴
- GitHub search API (repositories, licence field); `mohitk24/ev-warranty-us-dataset` README https://raw.githubusercontent.com/mohitk24/ev-warranty-us-dataset/main/README.md 🔴

Blocked or not reached: Green Vehicle Guide (robots.txt), the VCA download list (form postback), the CC0 GitHub data file (404 at the README path).
