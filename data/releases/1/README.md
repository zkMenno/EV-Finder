# EV Finder catalogue release 1

Generated 2026-11-15T02:34:01+00:00 by `ev release`. Data licence: CC BY 4.0 (see DATA_LICENSE.md); third-party inputs keep their own licences, listed below.

## Counts

- Variants (rows): 218
- Generations with rows: 62 of 66 in the seed
- Facts: 10627
- Quality tiers: single-source 202, sourced 16
- Real-range rungs: body-ratio 161, none 57
- Changes vs previous: +218 / -0 / ~0

## Sources and licences

| Source | Licence | Attribution |
|---|---|---|
| ademe (ADEME – Car Labelling) | Licence-Ouverte-2.0 | ADEME – Car Labelling, Licence Ouverte |
| dft-veh (DfT vehicle licensing statistics: df_VEH0120 (licensed vehicles by make and model)) | OGL-UK-3.0 | Contains public sector information licensed under the Open Government Licence v3.0 (Department for Transport, vehicle licensing statistics). |
| eea (EEA CO2 monitoring of new cars (Reg. 2019/631)) | CC-BY-4.0 | Contains data from the European Environment Agency, CO2 emissions from new passenger cars (Regulation (EU) 2019/631). Copyright holder: Directorate-General for Climate Action (DG CLIMA). CC BY 4.0. |
| fueleconomy (fueleconomy.gov vehicles dataset (US DOE / EPA)) | US-Government-Public-Domain | Data from fueleconomy.gov (U.S. Department of Energy and U.S. Environmental Protection Agency), public domain. |
| kba-fz10 (KBA FZ10 new registrations by make and model series) | dl-de/by-2-0 | © Kraftfahrt-Bundesamt, Flensburg. Datenlizenz Deutschland – Namensnennung – Version 2.0 (FZ10, Neuzulassungen nach Marken und Modellreihen). |
| kilowatt-openev (Open EV Data (KilowattApp)) | MIT-with-attribution | Open EV Data (https://github.com/KilowattApp/open-ev-data) |
| model-estimate (EV Finder estimate models) | CC-BY-4.0 | EV Finder estimate models |
| openev (Open EV Data) | CDLA-Permissive-2.0 | Contains data from OpenEV Data (open-ev-data-dataset), CDLA-Permissive-2.0. |
| rdw (RDW Open Data) | CC0-1.0 | Bron: RDW Open Data (opendata.rdw.nl), CC0. |
| rdw-defects (RDW Open Data: Geconstateerde Gebreken (APK defects)) | CC0-1.0 | Bron: RDW Open Data (opendata.rdw.nl), CC0. |
| seed-manual (EV Finder seed (hand-entered, unchecked)) | CC-BY-4.0 | EV Finder contributors |
| wikidata (Wikidata) | CC0-1.0 | Wikidata (wikidata.org), CC0. |

## Attribution

- Contains data from ADEME – Car Labelling (https://data.ademe.fr/datasets/ademe-car-labelling), licensed Licence-Ouverte-2.0. ADEME – Car Labelling, Licence Ouverte
- Contains data from DfT vehicle licensing statistics: df_VEH0120 (licensed vehicles by make and model) (https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files), licensed OGL-UK-3.0. Contains public sector information licensed under the Open Government Licence v3.0 (Department for Transport, vehicle licensing statistics).
- Contains data from EEA CO2 monitoring of new cars (Reg. 2019/631) (https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b), licensed CC-BY-4.0. Contains data from the European Environment Agency, CO2 emissions from new passenger cars (Regulation (EU) 2019/631). Copyright holder: Directorate-General for Climate Action (DG CLIMA). CC BY 4.0.
- Contains data from fueleconomy.gov vehicles dataset (US DOE / EPA) (https://www.fueleconomy.gov/feg/download.shtml), licensed US-Government-Public-Domain. Data from fueleconomy.gov (U.S. Department of Energy and U.S. Environmental Protection Agency), public domain.
- Contains data from KBA FZ10 new registrations by make and model series (https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz10/fz10_gentab.html), licensed dl-de/by-2-0. © Kraftfahrt-Bundesamt, Flensburg. Datenlizenz Deutschland – Namensnennung – Version 2.0 (FZ10, Neuzulassungen nach Marken und Modellreihen).
- Contains data from Open EV Data (KilowattApp) (https://github.com/KilowattApp/open-ev-data), licensed MIT-with-attribution. Open EV Data (https://github.com/KilowattApp/open-ev-data)
- Contains data from EV Finder estimate models, licensed CC-BY-4.0.
- Contains data from Open EV Data (https://github.com/open-ev-data/open-ev-data-dataset), licensed CDLA-Permissive-2.0. Contains data from OpenEV Data (open-ev-data-dataset), CDLA-Permissive-2.0.
- Contains data from RDW Open Data (https://opendata.rdw.nl/d/8ys7-d773), licensed CC0-1.0. Bron: RDW Open Data (opendata.rdw.nl), CC0.
- Contains data from RDW Open Data: Geconstateerde Gebreken (APK defects) (https://opendata.rdw.nl/d/a34c-vvps), licensed CC0-1.0. Bron: RDW Open Data (opendata.rdw.nl), CC0.
- Contains data from EV Finder seed (hand-entered, unchecked), licensed CC-BY-4.0. EV Finder contributors
- Contains data from Wikidata (https://www.wikidata.org/), licensed CC0-1.0. Wikidata (wikidata.org), CC0.

## Caveats

- Real-range figures on the `body-ratio` rung are PROVISIONAL generic ratios (mild-weather mixed driving), not measurements.
- `seed-manual` values are hand-entered and unchecked (confidence low).
- `registered_count_nl` is per generation: every variant of a generation shows the same RDW total (also in `registrations.NL`, kind fleet).
- `registrations` holds official counts per country, one per source and period: `fleet` = cars on the road (RDW NL, DfT UK), `new_registrations` = first registrations in the period (KBA DE year-to-date, EEA NL/DE/FR/BE per year). They are never added together. `level: model` (DfT has no model year) repeats the whole model's count on every generation.
- Charge curves from KilowattApp are `estimated` (upstream does not say how they were obtained); km-in-N-minutes also uses an estimated motorway consumption.
