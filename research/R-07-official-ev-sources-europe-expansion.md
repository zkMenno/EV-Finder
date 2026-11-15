# R-07 — Official open-data sources for EVs: European expansion markets

## Question

The launch countries (NL, DE, FR, BE, UK) are covered in **R-02**. This file covers Menno's next European markets from the Master spec "Global markets" list:

- **Tier 1b:** DK, SE, FI
- **Tier 2:** PT, ES, AT, CH, IE, IT, PL, UA

For each country it asks which official bodies publish open data on electric cars (fleet and registrations per make/model/variant/year, used-market transactions, imports, specs, inspections), how primary registries relate to aggregators, and the exact licences. Afterwards it gives a compact pass over other growing EU EV markets outside the tiers (LU, IS, CZ, Baltics, GR, HU, SI).

Norway, the US, Australia and non-European markets are in **R-03**. Norway (95.9% BEV share in 2025) is not covered here.

Same rules as R-02: licences are quoted from the publisher's own page where it could be reached. "Not stated" means not stated, so those rows are marked **needs check**. Confidence: 🟢 verified this session, 🟡 reasoned or seen only in portal metadata, 🔴 unsure or unreachable.

## Market context (why these countries)

BEV share of new cars. Source: ACEA figures as republished by best-selling-cars.com, which is an aggregator and not an official source. 🟡

| country | BEV 2025 | share 2025 | BEV Q1–Q3 2026 | share Q1–Q3 2026 | growth YoY Q1–Q3 |
|---|---|---|---|---|---|
| DK | 126,542 | 68.5% | 124,049 | **81.7%** | +40% |
| SE | 99,723 | 36.5% | 90,856 | 42.9% | +26% |
| FI | 26,745 | 37.2% | 28,677 | 50.4% | +49% |
| PT | 52,256 | 23.2% | 54,726 | 29.0% | +49% |
| ES | 101,627 | 8.8% | 100,508 | 11.0% | +40% |
| AT | 60,651 | 21.3% | 63,172 | 26.2% | +37% |
| CH | 53,250 | 22.8% | 45,464 | 26.2% | +27% |
| IE | 23,601 | 18.9% | 35,179 | 27.4% | +57% |
| IT | 94,624 | 6.2% | 101,716 | 8.0% | +67% |
| PL | 43,311 | 7.2% | 24,404 | 5.2% | **−5.5%** |
| LU | 12,663 | 26.9% | 11,615 | 31.0% | +24% |
| IS | 5,988 | 41.2% | 5,108 | 49.7% | +36% |
| SI | 6,419 | 11.2% | 10,457 | 19.8% | +136% |
| CZ | 13,806 | 5.6% | 13,806 | 7.4% | +36% |
| EU | 1,880,370 | 17.4% | 1,931,465 | 22.7% | +49% |

ACEA's own EU headline for 2025 is 1,880,370 BEVs, a 17.4% share. 🟢 UA is not in ACEA data. Coordinator note: EV imports to UA collapsed after VAT on EVs returned in January 2026.

## Answer (short)

- **FI is the best of the tier countries.** Traficom publishes the **full vehicle register per vehicle under CC BY 4.0**. It covers make, model, commercial name, variant/version, type-approval number, fuel, first-registration date and municipality, and also the **odometer reading** (`matkamittarilukema`). Traficom also has PxWeb tables with registrations by model series × fuel, inspection faults by model, and used imports by make × fuel × country of origin.
- **ES is the second best.** DGT publishes **per-vehicle microdata** for the fleet, new registrations, **transfers (the used market)** and deregistrations. Fields include make, model (commercial name), type/variant/version, first registration in Spain vs abroad (`PROCEDENCIA`), new/used, number of holders, Wh consumption and **electric range**. The EU-portal metadata says CC BY 4.0. The DGT page itself only requires faithful reproduction with the source cited.
- **CH is very rich but has a licence gap.** ASTRA publishes free per-vehicle datasets: NEUZU (new registrations), BEST (fleet), **GEBR (imported used cars)** and **AHOI (change of holder, i.e. the used market)**. **No licence is stated** anywhere on ASTRA's pages. The BFS aggregates on opendata.swiss say "commercial use requires permission".
- **IE is clean at aggregate level.** CSO PxStat (CC BY 4.0) has monthly **new cars by make and model × fuel** (TEM28) and **second-hand imports by make** (TEM25).
- **UA is surprisingly good.** The MVS register of every registration operation is open under CC BY on data.gov.ua. Each row has VIN, make, model, year, fuel and an operation code, and the codes identify imports and resales.
- **AT has make-level data only.** Statistik Austria OGD gives new registrations by make under CC BY 4.0. Make × fuel is only in STATcube (free reuse with the source quoted).
- **DK, SE, PT and IT have no open official make/model data:**
  - DK: Danmarks Statistik has fuel-level data only (free reuse with attribution). The DMR weekly full-register XML dump exists, but its terms could not be verified.
  - SE: SCB/Trafikanalys data is CC0, but the official statistics explicitly do **not** publish make/model.
  - PT: INE (CC BY 4.0) has fuel-level data only, and that data comes from ACAP, the industry association.
  - IT: the MIT fleet data (make only, CC BY 4.0) is a 2019 snapshot. ACI has fuel × municipality only.
  - In all four, **EEA CO2 monitoring** has to fill the make/model gap.
- **PL is blocked.** The CEPiK open API timed out from here, and an external tracker reports 100% failures. The licence is unverified.
- **Off-tier gems:**
  - **CZ:** per-vehicle register, inspections and **imported vehicles**, all CC0-equivalent.
  - **LU:** per-vehicle fleet with WLTP range plus monthly change deltas, CC0.
  - **LT:** Regitra fleet plus inspections, CC BY 4.0.
  - **LV:** CC0 snapshots.
- **SI** suspended vehicle data publication because of GDPR.

## Source tables

Legend for "usable": **yes** = licence verified on the publisher's page or official portal, and the file was fetched by script. **needs check** = licence not stated or only in harvested metadata, or access failed. **no** = not open.

### Denmark (Tier 1b)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `dk-dmr-xml` | Motorregistret (DMR) full export / Motorstyrelsen (formerly SKAT) | **primary** | Whole register, one record per vehicle (VIN, plate, make, model, variant, fuel, emissions, weights, inspection status). Weekly. 🟡: the existence and cadence come from Synsbasen's docs ("XML export of the entire vehicle registry, provided weekly by DMR through their public FTP server"), and DST builds its statistics from DMR | **FTP** (port 21). Blocked from this environment, so not fetched | **not stated**. No official page found that grants a licence | — | **needs check** | FTP only. The file is huge (multi-GB XML). Ask Motorstyrelsen for written reuse terms before ingesting. Commercial resellers (Synsbasen, nummerplade APIs) are built on it |
| `dst-bil` | StatBank BIL51 (new cars by owner × fuel, monthly since 2011), BIL52 (stock, monthly), **BIL56 (used-car trade: re-registrations, ownership changes × fuel, monthly)**, BIL21 (stock by age × fuel), BIL53/54 (by municipality) / Danmarks Statistik | aggregator of DMR | Fuel (incl. "El") × owner × region × age. **No make/model.** 🟢 (checked through the API tableinfo) | REST `https://api.statbank.dk/v1/data/BIL51/CSV?...`. No key needed | "You are free to re-use and reproduce contents from dst.dk and statbank.dk. This includes even commercial use. You should, however, always include a source accreditation to Statistics Denmark. You are, however, not allowed to use our logo." — https://www.dst.dk/en/Statistik/brug-statistikken/kildeangivelse | Yes, linked: "Source: Statistics Denmark – StatBank.dk/BIL51" | **yes** | BIL56 is a rare official **used-market volume by fuel** series |
| — | Mobility Denmark (De Danske Bilimportører) | not official (industry) | Monthly make/model sales | PDF/web | not open | — | no | Do not ingest |
| — | Synsbasen | commercial reseller of DMR + Færdselsstyrelsen inspections | Per-plate API | Paid | commercial | — | no | Its docs are useful as evidence of what DMR contains |

### Sweden (Tier 1b)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| — | Vägtrafikregistret / Transportstyrelsen | **primary** | Per vehicle. Open as statistics only. Extracts by make, year model or area are sold as "Fordonsurval" (villkorad data, Excel) | Paid / contract | Open data "får vidareutnyttjas utan restriktioner" (https://www.transportstyrelsen.se/sv/om-oss/statistik-och-analys/oppna-data/villkor-och-regler/). Register extracts are **villkorad** | — | **no** (register) | The free open part is counts by vehicle category only |
| `se-scb-tk1001` | Statistikdatabasen TK1001 (PersBilarDrivMedel etc.) / SCB for Trafikanalys | aggregator of Vägtrafikregistret | New registrations and stock by **fuel** × county/municipality × owner × year model. Monthly. 🟢 | PxWeb API `https://api.scb.se/OV0104/v1/doris/sv/ssd/TK/TK1001/...` | "We use the licence **CC0** for this data … If you yourself have processed data from Statistics Sweden, do not state the source." Agency-sourced tables "you should state this" — https://www.scb.se/en/About-us/about-the-website-and-terms-of-use/open-data-api/ | Not required. For processed data SCB asks that we **not** credit SCB | **yes** | Trafikanalys' quality declaration says: "Intressevariabler … som inte redovisas i den officiella statistiken, är **fabrikat/modell**". So **no make/model**. Trafa's own statistics portal states no separate licence. "Sweden's official statistics" logo/text may not be used on processed data (https://prod.trafa.se/en/pages/statistics/) |
| `se-trafa-manad` | Fordon månad (monthly Excel) and statistikportal / Trafikanalys | aggregator | Same as SCB plus press tables. 🟢 | XLSX on trafa.se/vagtrafik/fordon | **not stated** on trafa.se. Use the SCB API copy (CC0) instead | — | needs check | Trafa's new-registration counts ≠ Mobility Sweden's (Mobility Sweden excludes direct imports and older year models) |
| — | Mobility Sweden | not official | Make/model monthly | web | not open | — | no | — |

### Finland (Tier 1b)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `fi-traficom-ajoneuvot` | "Ajoneuvojen avoin data" (Open data for vehicles) / Traficom | **primary** (liikenneasioiden rekisteri) | **One row per vehicle in use**, 5,260,994 rows. Columns (header read from the file): `ajoneuvoluokka, ensirekisterointipvm, variantti, versio, kayttoonottopvm, korityyppi, omamassa, kayttovoima, suurinNettoteho, sahkohybridi, sahkohybridinluokka, merkkiSelvakielinen, mallimerkinta, kaupallinenNimi, tyyppihyvaksyntanro, kunta, NEDC_Co2, WLTP_Co2, matkamittarilukema, valmistenumero2, jarnro`. Material date 30 Sep 2026. Quarterly. 🟢 | ZIP-packed CSV (`;`), 201 MB / 934 MB: `https://opendata.traficom.fi/Content/Ajoneuvorekisteri.zip` | "The material been licensed under the **Creative Commons Nimeä 4.0 International** license" — https://tieto.traficom.fi/en/datatraficom/open-data ; avoindata.fi: `cc-by-4.0` | Yes ("as long as the original source of the data is mentioned") | **yes** | **`matkamittarilukema` (odometer, last recorded at inspection)** is gold for used EVs. BEV = `kayttovoima` code for electricity (decode with the "luokitukset" XLSX on the same page). Dates are `dd.mm.yyyy`. `kaupallinenNimi` is free text. Snapshot only, so history needs one snapshot per quarter. No range/Wh field |
| `fi-traficom-wvta` | Type-approval open data M1/N1 (WVTA tables Versio, Kaupallinennimi, Merkki, Paasto …) / Traficom | primary (type approval) | Type/variant/version technical data for common M1/N1. Updated 1.3, 1.6, 1.9 and 1.12. 🟢 | `https://opendata.traficom.fi/Content/wvta.zip` + Aineistokuvaus.pdf | Same open-data page (CC BY 4.0 statement is per dataset; for WVTA 🟡) | Yes | needs check | Join to the vehicle table on `tyyppihyvaksyntanro` + variant/version. Good for specs |
| `fi-traficom-pxweb` | TraFi statistics database: `060_ensirek_tau_106` (first registrations by **model series × fuel**, 2014–2026), `105` (× municipality × month), **Käytettynä maahantuodut** (`030/040`: used imports by make × fuel × first-use year × month; `020`: by **country of origin**), **Katsastuksen vikatilastot** (`040/050`: periodic inspections **by model** and by fault, 2023–2025) / Traficom | aggregator of the register | 718 model-series values, fuel incl. "Sähkö". Monthly. 🟢 (dimensions read through the API) | PxWeb API `https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/...` (JSON/CSV) | **not stated per table**. The open-data page's general wording ("freely used … as long as the original source … is mentioned") 🟡 | Yes | needs check (likely yes) | Inspection-by-model is the Finnish counterpart of UK MOT. Used imports by origin country show the DE/SE → FI flow |

### Portugal (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| — | Registo automóvel (IRN) / IMT vehicle register | **primary** | Per vehicle. **Not open.** 🟡 | — | — | — | no | DGPJ publishes counts of registration *acts* only (CC BY 4.0, data.europa.eu) |
| `pt-ine-0014603` | "Registers of imported used passenger cars" (by **fuel**, monthly) and `0002134` "New passenger cars sold" (by engine band) / INE | aggregator. **Source stated as ACAP** (industry association) | Fuel or cc band × month. **No make/model.** 🟢 | dados.gov.pt CSV, e.g. `https://dados.gov.pt/api/1/datasets/r/1da9b288-a50f-4af9-8e7d-7cef676c0f6b`; INE `https://www.ine.pt/xurl/indx/0014603` | dados.gov.pt / data.europa.eu: `https://creativecommons.org/licenses/by/4.0/` 🟡 (INE's own terms page not fetched) | Yes | needs check | Third-party (ACAP) origin under INE's CC BY. Used-import series by fuel is useful for PT's import-fed used market |
| — | ACAP, UVE | not official | Make/model monthly (ACAP); EV barometer (UVE) | PDF | not open | — | no | — |

### Spain (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `es-dgt-parque` | "Microdatos de parque de vehículos (mensual / anual)" / DGT (Ministerio del Interior) | **primary** (Registro de Vehículos) | **One row per vehicle in the fleet.** `PROVINCIA, MUNICIPIO, FABRICANTE, MARCA, MODELO` (commercial name), `TIPO, VARIANTE, VERSION, FECHA_MATR, FEC_PRIM_MATR, CLASE_MATR, PROCEDENCIA, NUEVO_USADO, NUM_TITULARES, CAT_EURO, KW, PROPULSION, CATELECT, CONSUMO, AUTONOMIA, EMISIONES_CO2, CARROCERIA …`. Generated on the 5th of each month. 🟢 (from the interface PDF) | Pipe-delimited TXT with header, from "DGT en cifras": https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Microdatos-de-parque-de-vehiculos-mensual/ ; layout https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/Interfaz-de-Salida-Fichero-Parque-Mensual.pdf | data.europa.eu (MIR records): "**Creative Commons Attribution 4.0 International**". Older DGT records point to `https://datos.gob.es/avisolegal` (commercial use allowed; cite the source; "prohibido desnaturalizar el sentido"; no implied endorsement). DGT sede: reproduction "debe ser realizada fielmente … y siempre debe ser citada como fuente el Organismo Autónomo Jefatura Central de Tráfico" — https://sede.dgt.gob.es/es/contenido/derechos-sobre-la-propiedad-intelectual/ | Yes: "Jefatura Central de Tráfico (DGT)" | **yes** (licence 🟡: CC BY appears in metadata only) | Make/model/type/variant/version values with **≤5 occurrences are masked with "¡"**, so rare EVs vanish. Municipality is blanked below 10k inhabitants. `FEC_PRIM_MATR` ≠ `FECHA_MATR` and `PROCEDENCIA` flag imported used cars. **`AUTONOMIA` and `CONSUMO` give range and consumption per vehicle** |
| `es-dgt-matriculaciones` | "Microdatos de Matriculaciones de Vehículos" (daily / monthly) / DGT | primary | Each vehicle entering the register, same layout family (MATRABA). 🟡 (layout assumed equal to parque) | ZIP/TXT, DGT en cifras; datos.gob.es `e00130502-matriculacion-de-vehiculos` | Same as above | Yes | **yes** (🟡) | Daily files allow near-real-time new-EV tracking |
| `es-dgt-transferencias` | "Microdatos de Transferencias de Vehículos" (daily / monthly) / DGT | primary | **Every change of ownership**, i.e. **used-car transactions** per vehicle with make/model/version/age. 🟡 (datos.gob.es description text is wrongly copied from "Bajas") | TXT, DGT en cifras | data.europa.eu: CC BY 4.0 (`mir-e00130502-ds-matrabatrans-000001`) | Yes | **yes** (🟡) | The best official used-EV market signal found in any country in this file. Includes dealer-stock transfers ("compraventa"), so dedupe them |
| `es-dgt-bajas` | "Microdatos de Bajas" / DGT | primary | Deregistrations incl. export | TXT | CC BY 4.0 (metadata) | Yes | yes (🟡) | Export bajas are useful for tracking EVs leaving the country |
| — | ANFAC, AEDIVE | not official | Monthly make/model | PDF | not open | — | no | — |

### Austria (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| — | Zentrale Zulassungsevidenz (BMI) / Versicherungsverband (ZDB) | **primary** | Per vehicle. Not open | — | — | — | no | — |
| `at-statistik-ogd-pkwnzl` | "Pkw-Neuzulassungen nach Marken ab Jänner 2000" (`OGD_fkfzul0759_OD_PkwNZL_1`) / Statistik Austria | aggregator of the registration data | Monthly new cars by **make only** (no fuel, no model), since Jan 2000. Updated 10 Nov 2026. 🟢 | CSV + code lists: `https://data.statistik.gv.at/data/OGD_fkfzul0759_OD_PkwNZL_1.csv` (`_HEADER`, `_C-J59-0` makes, `_C-A10-0` months) | "Lizenz: **Creative Commons Namensnennung 4.0 International**" — https://data.statistik.gv.at/web/meta.jsp?dataset=OGD_fkfzul0759_OD_PkwNZL_1 | Yes ("Quelle: Statistik Austria") | **yes** (limited) | The only vehicle OGD set. Codes such as `J59-332` must be decoded with the code list |
| `at-statcube-kfz` | STATcube "Kfz-Neuzulassungen" / "Kfz-Bestand" (make × fuel × Bundesland) / Statistik Austria | aggregator | Make × fuel incl. Elektro, monthly. 🟡 (cube contents not opened) | STATcube web (guest access with limits); CSV export | "Reproduction and distribution … is permitted provided the source 'STATcube – Statistical Database of Statistics Austria' is quoted." — https://www.statistik.at/en/databases/statcube-statistical-database/legal-points | Yes (that exact wording) | needs check (no API; guest limits) | Manual export only. Press-release PDFs list the top BEV makes monthly |
| — | AustriaTech / BMIMI "Elektromobilität in Zahlen" | aggregator (Statistik Austria) | Charts | web | not checked | — | needs check | — |

### Switzerland (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `ch-astra-neuzu` | NEUZU (new registrations, current year, one row per vehicle) / ASTRA-FEDRO, IVZ (MOFIS) | **primary** | Per vehicle: make, type, type-approval no., fuel, power, CO2 etc. Biweekly. Archives 2011–2018 have fewer attributes. Imported used cars are excluded (they are in GEBR). 🟢 (doc) | Tab-delimited UTF-8 TXT at `https://opendata.astra.admin.ch/ivzod/` (folders 1000-Fahrzeuge_IVZ, 2000/4000 type approvals, 3000 eDatenblatt) | **not stated**. ASTRA's page only says "Datennutzer verpflichten sich zu einem sorgsamen und fachgerechten Umgang mit den Dateninhalten" and "©Bundesamt für Strassen ASTRA" — https://www.astra.admin.ch/fahrzeugdaten | — | **needs check** | The directory blocks scripted clients ("Request Rejected" WAF for curl; WebFetch worked). Doc: https://www.astra.admin.ch/dam/en/sd-web/BakiDqfaJMx8/01%20Overview%20vehicle%20data%20information%20products-20260701.pdf |
| `ch-astra-best` | BEST (fleet, monthly), TYP_ROH (stock by type, quarterly), "Fahrzeugbestand nach Marke und Typ", "E-Fahrzeugbestand nach Gemeinde" (monthly) / ASTRA | primary | Per vehicle / per type. 🟢 (doc) | same | not stated | — | needs check | — |
| `ch-astra-gebr` | **GEBR** (imported used vehicles, current year, monthly) / ASTRA | primary | Per vehicle | same | not stated | — | needs check | Direct measure of the used-EV import flow (DE → CH) |
| `ch-astra-ahoi` | **AHOI** (change of holder / location / re-registration, monthly) / ASTRA | primary | Anonymised per vehicle. ASTRA: "The data set provides the basis for independent evaluations … of the used vehicle market" | `AHOI-yyyymm-MMM.txt` | not stated | — | needs check | The cleanest official used-market dataset in this file, if the licence is confirmed |
| `ch-astra-eDatenblatt` / TG | eDatenblatt (CoC data), 3rd-generation type approvals (JSON) / ASTRA | primary (type approval) | Monthly | same | not stated | — | needs check | Spec source for CH |
| `ch-bfs-strassenfahrzeuge` | "Neue Inverkehrsetzungen von Strassenfahrzeugen" (monthly since 2005 by canton × fuel), stock tables / BFS on opendata.swiss | aggregator of IVZ | Fuel × canton × vehicle type. **No make.** 🟡 | opendata.swiss service | "**Open use. Must provide the source. Use for commercial purposes requires permission of the data owner.**" — https://opendata.swiss/en/dataset/neue-inverkehrsetzungen-von-strassenfahrzeugen-nach-fahrzeuggruppe-und-fahrzeugart2/resource/0088ec81-3b87-4b1f-9391-d0725590e890 (read through WebFetch; the page is JS-rendered) | Yes | **needs check** | **Commercial-use permission needed** (see red flags). The opendata.swiss CKAN API returned 403 to curl |

### Ireland (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| — | National Vehicle File / Department of Transport | **primary** | Per vehicle. Not open | — | — | — | no | DoT's aggregates are published through CSO (DOTA/DOTM tables) |
| `ie-cso-tem28` | TEM28 "New Private Cars Licensed for the First Time" by **Type of Fuel × Make and Model** (332 make+model values) / CSO | aggregator of NVDF (Revenue VRT registrations) | Monthly 2024-01 → 2026-10. Fuel incl. "Electric", PHEV. 🟢 | PxStat JSON-stat/CSV: `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/TEM28/JSON-stat/2.0/en` | "Statistical information on this website is accessible free of charge and licensed under **Creative Commons Attribution (CC BY 4.0)**." — https://cso.ie/en/aboutus/whoweare/copyrightpolicy/ ; data.gov.ie copies are tagged CC BY 4.0 | Yes ("Source: CSO") | **yes** | "Make and Model" is a single combined label ("Audi A3"), so split it. Monthly data is provisional |
| `ie-cso-tem24-25` | TEM24 (new) / **TEM25 (second-hand imports)** private cars by **make** × engine cc × emission band × licensing authority / CSO | aggregator | Monthly since 2022, 41 makes. No fuel in TEM25. 🟢 | PxStat | CC BY 4.0 (as above) | Yes | **yes** | TEM25 shows the used-import flow, mostly from the UK. BEVs fall in emission Band A |
| `ie-cso-dotm05-08` | DOTM05–08 private cars licensed by CO2 band (NEDC/WLTP) / DoT via CSO | aggregator | Monthly stock | PxStat | CC BY 4.0 | Yes | yes | Fuel/BEV only via band |
| `ie-rsa-nct` | "Make Model Year Failures at NCT" / Road Safety Authority | primary (inspection) | Pass/fail by make/model/year | data.gov.ie (only **2015, 2016** sets) | 2015 set: CC BY 4.0 (data.europa.eu); 2016: not stated | Yes | needs check | Stale on the portal. Newer years exist as NCTS PDFs (not checked) 🔴 |
| — | SIMI | not official (industry) | Make/model | web | not open | — | no | — |

### Italy (Tier 2)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `it-mit-parco` | "Parco circolante dei veicoli" by region / MIT – Motorizzazione (Archivio nazionale veicoli) | **primary** | Per vehicle: `tipo veicolo, destinazione, uso, comune/provincia residenza, età/sesso intestatario, marca, cilindrata, alimentazione, kw, data immatricolazione, classe euro, emissioni co2, massa, revisione in regola, assicurazione in regola`. **No model.** Situation at **31/12/2019**. 🟢 (columns from the CSVW metadata) | ZIP CSV per region: `https://dati.mit.gov.it/hfs/parco_circolante_<Regione>.csv.zip`; schema `https://dati.mit.gov.it/hfs/metadata/metadata_parco_circolante.json` | data.europa.eu (harvested from dati.gov.it): "**Creative Commons Attribution 4.0 International**" 🟡 (the MIT page and CKAN API did not render for scripts) | Yes | needs check | **Stale** (2019). Make only. The "revisione in regola" flag is a crude inspection proxy |
| `it-aci-lod` | ACI Linked Open Data, e.g. "Prime iscrizioni di autovetture nuove 2025 per ente territoriale e alimentazione" / Automobile Club d'Italia (PRA) | primary (PRA) / official aggregator | Annual first registrations and fleet by municipality × **fuel**. No make/model. 🟢 | CSV/RDF `http://lod.aci.it/sites/default/files/statistiche_prime_iscrizioni_2025.csv` | dataset metadata: CC BY 4.0. The portal footer, however, says "Copyright © 2018 ACI. Tutti i diritti riservati" | Yes | needs check | The licences conflict. ACI's "Autoritratto" (make/model by province) has no open licence found 🔴. lod.aci.it reset the connection once |
| — | UNRAE, Motus-E, Dataforce | not official | Make/model monthly | PDF | not open | — | no | — |

### Poland (Tier 2, import-fed)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `pl-cepik-api` | API for CEPiK / Ministerstwo Cyfryzacji | **primary** (Centralna Ewidencja Pojazdów) | Per vehicle by voivodeship and date range (make, model, fuel, year, origin incl. **used import**). 🔴 (fields not verified) | REST beta `https://api.cepik.gov.pl/` (Swagger at /doc). **Connection reset from here.** freepublicapis.com reports 0% reliability over 30 days ("This API is Dead") | dane.gov.pl record 1558: **not readable** (robots-blocked to WebFetch, reset to curl). Third-party claim that gov.pl allows commercial use with attribution is **unverified** | — | **needs check** | If it is revived, its import-origin field would be the key to the DE/NL → PL used flow |
| `pl-dane-cepik-static` | "Pojazdy zarejestrowane w Polsce w podziale na województwa", "Marki samochodów osobowych w 2020 roku" / Ministerstwo Cyfryzacji | aggregator of CEPiK | Static yearly tables. 🟡 | dane.gov.pl | not stated in the harvested metadata | — | needs check | Stale |
| — | PZPM / Samar, PSPA "Licznik elektromobilności" | not official | Make/model, imports | PDF | not open | — | no | Samar resells CEPiK-derived data |
| — | GUS (Statistics Poland) BDL | aggregator | Fleet by fuel | — | not checked 🔴 | — | needs check | — |

### Ukraine (Tier 2, volatile, import-fed)

| id | name / publisher | primary or aggregator | contents and granularity | access / format | licence (as stated) + URL | attribution | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| `ua-mvs-registrations` | "Інформація про зареєстровані транспортні засоби (включаючи VIN)" (current) and "Відомості про транспортні засоби та їх власників" (yearly `reestrTZ2013…2026` ZIPs) / Головний сервісний центр МВС (MVS) | **primary** | **One row per registration operation**: `koatuu, person (P/legal), operCodeOperas, dReg, dep, brand, model, vin, makeYear, color, kind, purpose, body, fuel, capacity, powerKwt, ownWeight, totalWeight`. Operation codes distinguish **first registration of new cars imported from abroad**, re-registration to a new owner (trade-in, sale contracts) and deregistration. Updated 2026-10-16. 🟢 (header read) | CSV `https://data.gov.ua/dataset/348dbb24-a545-4d8c-95d5-18d35c593ca1/resource/2cc4ffd4-ce98-45eb-8c8c-c661d22b6a22/download/registeredvehicles.csv`; yearly ZIPs under dataset `06779371-…` | data.gov.ua CKAN `license_title`: "**Creative Commons Attribution**" (both datasets) — https://data.gov.ua/api/3/action/package_show?id=00a6c5c6-ff57-406c-a6e5-795acbaca5c3 | Yes (MVS / ГСЦ МВС) | **yes** | **Contains VIN**: never republish it, aggregate only. Fuel label for BEV is "ЕЛЕКТРО" (🟡). Operation-code text is Ukrainian and needs a code map. The market is volatile (2026 VAT change), so treat trends with care |
| — | State Customs Service (customs.gov.ua) import declarations | primary (customs) | EV imports | not checked 🔴 | — | — | needs check | Also try Eurostat Comext exports from EU partners (below) |
| — | Ukrautoprom, Institute for Car Market Research (eauto.org.ua) | not official | Monthly EV import tallies, built on MVS data | web | not open | — | no | — |

## Other growing EU EV markets (compact)

| country | id | name / publisher | primary / aggregator | contents | access | licence (as stated) | usable | gotchas |
|---|---|---|---|---|---|---|---|---|
| **LU** | `lu-snca-parc` | Parc Automobile du Luxembourg + Opérations Delta / SNCA | **primary** | **Per vehicle**, monthly: `LIBMRQ` (make), `TYPCOM` (commercial name), `PVRVAR/PVRVER`, `DATCIRPRM` (first registration anywhere), **`PAYPVN` (country of origin)**, `CODCRB`, `CO2WLTP`, **`CONSELEC`, `AUTOELEC` (electric range)**, `PKWELECNET`. Delta file = monthly changes (used-market proxy). 🟢 | XML/XLSX, e.g. `https://download.data.public.lu/resources/parc-automobile-du-luxembourg/20261105-085825/parc-automobile-202611.xml` | data.public.lu: `cc-zero` | **yes** | Small market (12.7k BEVs in 2025) but a model dataset for our schema. Large leasing/cross-border share |
| **CZ** | `cz-rsv-vypisvozidel`, `…technickeprohlidky`, **`…vozidladovoz`** | Registr silničních vozidel: vehicle technical data, technical inspections, **imported vehicles**, decommissioned / Ministerstvo dopravy (dataovozidlech.cz) | **primary** | Per vehicle: `Datum 1. registrace`, **`Datum 1. registrace v ČR`**, make, type, variant, version, **VIN**, `Obchodní označení`, fuel, **`Plně elektrické vozidlo`**, hybrid class, CO2, consumption … 🟢 (header read) | CSV `https://download.dataovozidlech.cz/vypiszregistru/vypisvozidel` (large, >40 MB in 40 s) | data.gov.cz terms: `narrowMatch` **CC0**, "neobsahuje autorská díla", database "není chráněna zvláštním právem", inspections "neobsahuje osobní údaje" | **yes** | Contains VIN (aggregate only). Inspection data may include odometer (🟡 not read). Excellent import tracking |
| **LT** | `lt-regitra-parkas`, `lt-transeksta-ctadb`, `lt-regitra-tpsais` | Registered vehicles / Regitra; roadworthiness tests / TRANSEKSTA (weekly since 2015); vehicle transactions / Regitra | primary | Fleet snapshot, inspections with pseudonymised IDs and VIN, transactions with amounts | `https://www.regitra.lt/wp-content/uploads/failai/Atviri_TP_parko_duomenys.zip`, `https://get.data.gov.lt/datasets/gov/transeksta/ctadb` | data.gov.lt: CC BY 4.0 🟡 (metadata) | needs check (fields) | The **transactions** dataset may contain **prices**. Worth a look 🔴 |
| **LV** | `lv-csdd-tl` | CSDD uzskaitē esošie transportlīdzekļi / CSDD | primary | Irregular snapshots (2017, 2021, 2023, Feb 2025): cars, motorcycles, trailers | data.gov.lv TXT | data.gov.lv: `CC0-1.0` 🟡 | needs check (fields) | Irregular cadence |
| **EE** | `ee-transpordiamet-esmareg` | First-registered vehicles / Transpordiamet | primary | `REG_KP; KAT; MARK; MUDEL; ESMAREG (first-registration year); ARV; SH_UUED…`, daily updates. **No fuel.** 🟢 (header read) | andmed.eesti.ee API → S3 CSV | **not stated** in the API record | needs check | `ESMAREG` older than the period means a used import |
| **IS** | `is-hagstofa-sam30120` | Number of vehicles by weight and energy source / Statistics Iceland | aggregator (Samgöngustofa) | Annual, fuel-level | PxWeb `https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/5_samgongur/3_okutaekiogvegir/1_okutaeki/SAM30120.px` | not checked 🔴 | needs check | Samgöngustofa's make/model dashboards have no open licence found. EEA covers IS |
| **SI** | `si-mzi-prvic-registrirana` | Vehicles registered for the first time, by month / Ministrstvo za infrastrukturo | primary | Was per vehicle with full technical data | podatki.gov.si | — | **no** | "**vehicle data will not be published on the OPSI portal until further notice**" (GDPR / ZVOP-2) |
| **HU** | `hu-ksh-forgalomba` | First registrations of new and used vehicles by type, quarterly / KSH | aggregator | No make/model | KSH | not stated in metadata 🔴 | needs check | — |
| **GR** | — | No national open vehicle data found (only regional garages) | — | — | — | — | no | EEA only |

## EU-level sources and which gaps they fill

| id | publisher | fills | licence | notes |
|---|---|---|---|---|
| `eea-co2-cars` (see R-02) | EEA / DG CLIMA | **Annual make + commercial name + type/variant/version + Wh/km + electric range** of new registrations for **all EU-27 + IS + NO**. The only open make/model source for **DK, SE, PT, IT, AT (model), PL, GR, HU, SI** | CC BY 4.0 (verified in R-02) | **Does not cover CH or UA** (both outside Regulation 2019/631; 🟡). The UK is only covered until 2020 |
| `eurostat-road_eqr_carpda` / `road_eqs_carpda` | Eurostat | Annual new registrations / stock by fuel (incl. "Electricity", PHEV) for every country incl. CH, IS, NO. Fetched for SE 2025 🟢 | **not verified this session** (Eurostat copyright page timed out). Usually reported as CC BY 4.0 🟡 | Sanity totals only. No make |
| `eurostat-comext` | Eurostat | Import/export flows of CN **8703 80** (BEV cars) by partner → PL/UA/CZ inflows from DE/NL | not verified 🟡 | 🟡 CN 8703 80 has no new vs used split, so it cannot isolate used EVs. Use national registers (CZ dovoz, ES PROCEDENCIA, FI used imports, CH GEBR, LU PAYPVN) instead |
| `eafo` | EC DG MOVE | Monthly BEV/PHEV per country | third-party rights unclear (R-02) | Cross-check only |

## Recommended source per field per country

| field | DK | SE | FI | PT | ES | AT | CH | IE | IT | PL | UA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fleet by make/model/year | DMR dump (check) | none → EEA flows | **Traficom vehicle file** | none | **DGT parque microdata** | none (STATcube make×fuel) | **ASTRA BEST** (check) | none (CSO stock by band only) | MIT parco (make, 2019) | CEPiK (down) | **MVS register** (derive) |
| New registrations make/model | **EEA** | **EEA** | **Traficom PxWeb 106** (monthly) | **EEA** | **DGT matriculaciones** (daily) | Statistik Austria OGD (make) + **EEA** | **ASTRA NEUZU** | **CSO TEM28** (monthly) | **EEA** | **EEA** | **MVS** (op. codes) |
| Used-market transactions | **DST BIL56** (fuel) | none | snapshot diff of Traficom file | none | **DGT transferencias** | none | **ASTRA AHOI** | none | none | none | **MVS** (re-registration codes) |
| Used imports | — | — | **Traficom used-import tables** (make × fuel × origin) | **INE 0014603** (fuel) | DGT `PROCEDENCIA` | — | **ASTRA GEBR** | **CSO TEM25** (make) | — | CEPiK (down) / Comext | MVS import codes |
| BEV flag | DST `DRIV=El` | SCB fuel "El" | `kayttovoima` | INE fuel | `PROPULSION`/`CATELECT` | STATcube | NEUZU fuel | TEM28 "Electric" | `alimentazione` | — | `fuel` |
| Specs (range, Wh/km) | EEA | EEA | Traficom WVTA + EEA | EEA | **DGT `AUTONOMIA`/`CONSUMO`** | EEA | ASTRA eDatenblatt (check) | EEA | EEA | EEA | none |
| Odometer / inspection | none open | none | **Traficom `matkamittarilukema` + inspection-by-model tables** | none | none | none | none | RSA NCT (stale) | MIT `revisione in regola` | none | none |
| Catalogue price | none | none | none | none | none | none | none | none | none | none | none |

Rule of thumb, same as R-02: go primary where the primary is open (FI, ES, CH, UA, CZ, LU). Use the national aggregator only for fuel totals. Use **EEA for make/model wherever the national side is closed** (DK, SE, PT, IT, PL).

## Adapters to build next (ranked)

1. **`traficom`** (FI): one quarterly ZIP CSV, CC BY 4.0, per vehicle with odometer. Add the PxWeb model × fuel, used-import and inspection-by-model tables. Highest value per hour, and it serves a Tier 1b market at 50% BEV share.
2. **`eea-co2` extension** (already #4 in R-02): just widen the country filter to DK, SE, PT, IT, AT, PL, IE, ES, FI, IS. This unlocks make/model for every closed country at zero extra licence risk.
3. **`dgt-matraba`** (ES): parque monthly + matriculaciones + transferencias. Pipe-delimited, CC BY 4.0 (metadata). Gives range per vehicle and the used-transfer market. Handle the "¡" masking.
4. **`cso-pxstat`** (IE): TEM28/TEM25 JSON-stat, CC BY 4.0. Small and clean.
5. **`astra-ivz`** (CH): NEUZU/BEST/GEBR/AHOI. **Build only after the licence is confirmed in writing** (see red flags). The WAF needs a browser-like client or manual download.
6. **`snca`** (LU) and **`rsv-cz`** (CZ): CC0 per-vehicle. Cheap, good schema test beds, and CZ has import data.
7. **`mvs-ua`** (UA): CC BY per-operation CSV. Map operation codes and drop VIN at ingestion.
8. **`dst-statbank`** (DK fuel totals + used trade) and **`scb-pxweb`** (SE fuel totals): sanity totals only.
9. **`statistik-austria-ogd`** (AT make-level): low value next to EEA.
10. Parked: **DMR XML** (DK, terms + FTP), **CEPiK** (PL, API down), **ACI/MIT** (IT, stale or unclear), **Regitra/TRANSEKSTA** (LT, check fields/prices).

## Licence red flags

- **CH ASTRA: no licence stated** for the open IVZ datasets. There is only "©Bundesamt für Strassen ASTRA" and a duty of "sorgsamen und fachgerechten Umgang". **Email ASTRA** before ingesting NEUZU/BEST/GEBR/AHOI.
- **CH BFS (opendata.swiss): "Use for commercial purposes requires permission of the data owner."** If EV Finder ever carries affiliate links or ads, that is commercial use. Ask, or don't use.
- **DK DMR dump:** the terms could not be verified, and FTP is not reachable through our proxy. Do not ingest until Motorstyrelsen confirms the terms.
- **SE SCB: CC0, but "If you yourself have processed data from Statistics Sweden, do not state the source."** This has the same flavour as RDW's clause (R-02). We may still show "derived from public Swedish registration statistics" without naming SCB. The "Sweden's official statistics" logo/text may not be used on processed data.
- **ES DGT / datos.gob.es:** CC BY 4.0 is in the EU-portal metadata only. The DGT sede requires faithful reproduction "sin manipular ni alterar los contenidos". datos.gob.es forbids "desnaturalizar el sentido" and implying endorsement. Our derived figures are fine, but don't present them as DGT's own numbers.
- **PT INE:** CC BY 4.0, but the series' stated source is **ACAP** (industry), so third-party origin.
- **IT ACI:** dataset metadata says CC BY 4.0 while the portal footer says "Tutti i diritti riservati". The licences conflict.
- **Personal data:** the CZ, UA and LT files contain **VIN** (LT also has pseudonymised IDs). Store aggregates only, never republish VIN, and add a pipeline rule to drop VIN at ingest. **SI** stopped publishing for GDPR reasons, and other countries could follow, so keep snapshots.
- **PL CEPiK:** licence unverified and the API is unreachable.
- **DST:** reuse allowed incl. commercial, attribution required, **no logo**.

## Ranking: best open vehicle data (for choosing next markets)

Data quality only. Combine it with market size from the table at the top.

1. **FI** 🟢: per-vehicle CC BY 4.0 with odometer, plus model × fuel monthly, used imports by origin and inspection by model. A complete used-EV toolkit.
2. **ES** 🟢/🟡: per-vehicle fleet, registrations and **transfers** with model/version and range. CC BY 4.0 per metadata. A big market (≈100k BEV/yr).
3. **CZ** 🟢: per-vehicle register, inspections and imports, CC0. Small EV market, but a growing import hub.
4. **LU** 🟢: per-vehicle CC0 with WLTP range and monthly deltas. Tiny market.
5. **CH** 🟡: per-vehicle new, fleet, used-import and holder-change datasets. Top quality, but **licence unstated**.
6. **UA** 🟢: per-operation CC BY incl. VIN and import codes. Volatile market.
7. **IE** 🟢: CSO make+model × fuel monthly + used imports by make, CC BY 4.0. Aggregate only.
8. **LT / LV** 🟡: open registers (CC BY / CC0), fields not yet inspected.
9. **AT** 🟢: make-only OGD (CC BY 4.0) + STATcube. Needs EEA for models.
10. **DK** 🟢 (fuel only) / 🔴 (DMR): fuel-level and used-trade totals. Make/model needs EEA unless the DMR terms clear.
11. **SE** 🟢: CC0 but explicitly no make/model. EEA only.
12. **IT** 🟡: stale 2019 make-level fleet. EEA only.
13. **PT** 🟡: fuel-level via ACAP. EEA only.
14. **PL** 🔴: API down, licence unknown. EEA only.
15. **EE, IS, HU, GR, SI**: thin, unlicensed or suspended.

Implication: among Menno's tiers, **FI and ES** give the best data per market today. **IE** is easy. **DK and SE** have strong markets (82% and 43% BEV share) but weak open data, so they would launch on EEA plus DST/SCB totals. **CH** is worth one email to ASTRA.

## "See listings" marketplaces (names only, no scraping)

DK: Bilbasen, DBA · SE: Blocket · FI: Nettiauto, Tori · PT: Standvirtual, OLX · ES: coches.net, Wallapop, Milanuncios, AutoScout24.es · AT: Willhaben, AutoScout24.at, Gebrauchtwagen.at · CH: AutoScout24.ch, tutti.ch · IE: DoneDeal, Carzone · IT: Subito, AutoScout24.it · PL: Otomoto, OLX · UA: AUTO.RIA · LU: Luxauto · CZ: Sauto, TipCars · LT: Autoplius · LV: ss.lv · EE: auto24 · HU: Hasznaltauto.hu · SI: Avto.net · GR: Car.gr

## Sources (retrieved 2026-11-15)

- ACEA 2025 full-year press release (EU BEV 1,880,370, 17.4%): https://www.acea.auto/pc-registrations/new-car-registrations-1-8-in-2025-battery-electric-17-4-market-share/ 🟢
- Per-country BEV tables (ACEA-based, aggregator): https://www.best-selling-cars.com/europe/2025-full-year-europe-bev-electric-car-sales-per-european-country/ , https://www.best-selling-cars.com/europe/2026-q3-europe-battery-electric-car-sales-by-european-country/ 🟡
- Traficom open data (CC BY 4.0 statement, ZIP URL): https://tieto.traficom.fi/en/datatraficom/open-data ; avoindata record https://avoindata.suomi.fi/data/en/dataset/ajoneuvojen-avoin-data ; WVTA description https://tieto.traficom.fi/files/media/file/Aineistokuvaus.pdf ; PxWeb https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/ 🟢
- Transportstyrelsen open data and terms: https://www.transportstyrelsen.se/sv/om-oss/statistik-och-analys/oppna-data/ , …/villkor-och-regler/ , …/villkorad-data-utifran-trafikslag/ 🟢
- Trafikanalys quality declaration (no make/model): https://trafa.se/globalassets/statistik/vagtrafik/fordon/manad/kvalitetsdeklaration-2025-manad.pdf ; official-statistics logo rule https://prod.trafa.se/en/pages/statistics/ 🟢
- SCB open data CC0: https://www.scb.se/en/About-us/about-the-website-and-terms-of-use/open-data-api/ 🟢
- DST source rules: https://www.dst.dk/en/Statistik/brug-statistikken/kildeangivelse ; StatBank API https://api.statbank.dk/v1/tableinfo/BIL56 🟢
- DMR weekly XML via public FTP (secondary evidence): https://api.synsbasen.dk/v1/docs 🟡
- ASTRA vehicle data products overview: https://www.astra.admin.ch/dam/en/sd-web/BakiDqfaJMx8/01%20Overview%20vehicle%20data%20information%20products-20260701.pdf ; terms page https://www.astra.admin.ch/fahrzeugdaten ; FAQ https://www.astra.admin.ch/de/faq-fahrzeugdaten ; directory https://opendata.astra.admin.ch/ivzod/ 🟢 (licence not stated)
- BFS on opendata.swiss (commercial-use permission): https://opendata.swiss/en/dataset/neue-inverkehrsetzungen-von-strassenfahrzeugen-nach-fahrzeuggruppe-und-fahrzeugart2/resource/0088ec81-3b87-4b1f-9391-d0725590e890 🟡
- Statistik Austria OGD metadata (CC BY 4.0): https://data.statistik.gv.at/web/meta.jsp?dataset=OGD_fkfzul0759_OD_PkwNZL_1 ; STATcube legal points https://www.statistik.at/en/databases/statcube-statistical-database/legal-points 🟢
- CSO copyright (CC BY 4.0): https://cso.ie/en/aboutus/whoweare/copyrightpolicy/ ; PxStat TEM28/TEM25: https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/TEM28/JSON-stat/2.0/en 🟢
- RSA NCT make/model (2015/2016) via data.europa.eu: dataset ids `3c088c59-003a-41fb-8358-79b999032f86`, `b8e6919f-35ef-4cc8-b694-4cbd5d4e3298` 🟡
- DGT microdata pages and layout: https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Microdatos-de-parque-de-vehiculos-mensual/ ; https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/Interfaz-de-Salida-Fichero-Parque-Mensual.pdf ; DGT IP notice https://sede.dgt.gob.es/es/contenido/derechos-sobre-la-propiedad-intelectual/ ; datos.gob.es aviso legal https://datos.gob.es/es/aviso-legal ; EU-portal records `mir-e00130502-ds-parque-000002`, `mir-e00130502-ds-matrabaaltas-000001`, `mir-e00130502-ds-matrabatrans-000001` (CC BY 4.0) 🟢/🟡
- INE Portugal via data.europa.eu: `ine-0014603`, `ine-0002134` 🟡
- MIT parco circolante: https://dati.mit.gov.it/hfs/metadata/metadata_parco_circolante.json ; EU-portal record `e9b45e54-943f-4bfb-8dff-b3e3026743fa` 🟡 ; ACI LOD http://lod.aci.it/ (record `cc3ea62c-3dde-489f-95af-b5f08d921de0`) 🟡
- CEPiK API record (data.europa.eu): `https-dane-gov-pl-pl-dataset-1558-api-dla-bazy-centralnej-ewidencji-pojazdow-i-kierowcow-cepik` ; status https://freepublicapis.com/cepik-api 🔴
- Ukraine MVS datasets: https://data.gov.ua/api/3/action/package_show?id=00a6c5c6-ff57-406c-a6e5-795acbaca5c3 , https://data.gov.ua/api/3/action/package_show?id=06779371-308f-42d7-895e-5a39833375f0 🟢
- Luxembourg SNCA: https://data.public.lu/api/1/datasets/parc-automobile-du-luxembourg/ , https://data.public.lu/api/1/datasets/operations-delta-des-vehicules-au-luxembourg/ 🟢
- Czech RSV: https://download.dataovozidlech.cz/vypiszregistru/vypisvozidel ; terms (CC0 narrowMatch) https://data.gov.cz/zdroj/datové-sady/66003008/77ff7dc0d7f61ae70726e0a38286b483/distribuce/3b219b77240f8aac2dad9d33b9844236/podmínky-užití 🟢
- Lithuania (data.gov.lt via data.europa.eu): `https-data-gov-lt-datasets-1211-`, `-2721-`, `-2812-~~1` 🟡 ; Latvia CSDD https://data.gov.lv/dati/api/3/action/package_show?id=3a2edf7a-f265-4f64-b275-87ed229ab401 🟡 ; Estonia https://andmed.eesti.ee/api/v2/datasets/9bfa509b-1539-4a06-a6a3-cda6e2e378f1 🟢 (no licence) ; Slovenia suspension: data.europa.eu `prvic-registrirana-vozila-po-mesecih` 🟢 ; Iceland PxWeb https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/5_samgongur/3_okutaekiogvegir/1_okutaeki/ 🟡
- Eurostat road_eqr_carpda API: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/road_eqr_carpda 🟢 (data) / licence 🔴 not verified

Blocked during research: FTP to DMR (proxy is HTTPS-only); opendata.astra.admin.ch (WAF rejects curl); ckan.opendata.swiss API (403); api.cepik.gov.pl, api.dane.gov.pl, www.gov.pl (connection resets); dane.gov.pl (robots-disallowed for WebFetch); datos.gob.es (Incapsula); statistik.at open-data page; Eurostat copyright page (permission prompt timed out).
