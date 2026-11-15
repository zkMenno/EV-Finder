# R-27 Climate normals and town search: licences

**Question:** can we publish a January mean temperature and a cold-snap (10th-percentile) temperature per town, plus a town search list, under our CC BY output? Which sources, which licence, what attribution? (Feeds T-034, spec `docs/spec/trip-fit.md` §3 Step 3 and §7.)

**Answer:** yes. 🟢 **Meteostat is CC BY 4.0, not CC BY-NC.** Its licence page allows commercial use and asks us to credit Meteostat *and* the original provider. The "NC" wording people remember is still in an old docstring inside the Meteostat Python package. 🟢 **ERA5 and ERA5-Land are now CC BY 4.0 too**: Copernicus replaced the "Licence to use Copernicus Products" with CC BY on 2 July 2025, and the CDS catalogue lists ERA5-Land monthly means and the ERA5-Land daily statistics as `CC-BY-4.0`. CC BY lets us publish our own derived January mean and P10 under CC BY, as long as we credit the source and say we changed it. 🟢 **GeoNames is CC BY 4.0** and fine for town search. 🔴 **Eurostat GISCO LAU and E-OBS are non-commercial only**, so we skip them.

**Recommendation:**
1. Primary source: **ERA5-Land daily statistics, 1991–2020** (9 km grid). It gives one licence and one method for every country, NO/US/AU included. Compute the January mean and the P10 of January daily mean temperature per grid cell, then look up each town's cell.
2. Second source per headline field: **Meteostat station normals**. Keep only rows whose provider has a named open licence (DWD, NOAA, GeoSphere, ECCC, MET Norway, ERA5-Land), and use the national services below where they are open.
3. Town list: **GeoNames `cities1000` or `cities5000`**, coordinates rounded.
4. Natural Earth (public domain) is a fallback only. It covers big places, not villages.

## 1. Meteostat

| Point | Finding | Conf. |
|---|---|---|
| Licence | "published under the terms of the Creative Commons Attribution 4.0 International (CC BY 4.0) license"; share and adapt "for any purpose, even commercially" | 🟢 |
| Attribution | "You must give credit to Meteostat and its meteorological data providers." Example: `Source: Meteostat (meteostat.net), Deutscher Wetterdienst (dwd.de)`. If the provider is unknown: `Source: Meteostat and its data providers (dev.meteostat.net/providers)` | 🟢 |
| Scope | The licence covers "only … data redistributed by Meteostat". Data fetched straight from a weather service through the Python library carries that provider's own terms | 🟢 |
| Terms of service | Free to use; no accuracy guarantee; "not intended to be used in any context where human life or property may be at risk"; access can be blocked without notice | 🟢 |
| Per-provider licences (from the provider table in package `meteostat` 2.2.3, `providers/index.py`) | DWD (hourly, daily, monthly, POI, MOSMIX, CLIMAT): CC BY 4.0 · NOAA ISD Lite, GHCN-Daily, GHCN-Hourly: CC0 1.0 · GeoSphere Austria: CC BY 4.0 · ECCC: "Data Servers End-use Licence" · MET Norway forecast: NLOD 2.0 · ERA5-Land: CC BY 4.0 · **METAR: no licence named** · all flagged `commercial=True` | 🟢 (code read) |
| Where the NC confusion comes from | The `utils/data.py` docstring in the same package still says "Creative Commons Attribution-NonCommercial 4.0". The licence page is the binding text | 🟢 |
| Normals | In v2, `normals()` is computed client-side from monthly data (default period 1961–1990, which we must set to 1991–2020). It returns monthly means, **not P10**. P10 needs daily data | 🟢 |
| Old docs page `dev.meteostat.net/bulk/normals.html` | Not opened (fetch blocked this session) | 🔴 |

**Ingest rule:** record the provider per row. Drop or flag rows sourced from METAR (no named licence). Show the combined credit line in the footer and on the Nerd panel.

## 2. Copernicus ERA5 / C3S

| Point | Finding | Conf. |
|---|---|---|
| Licence change | ECMWF forum: the Licence to use Copernicus Products in CDS, ADS and EWDS was "replaced with the Creative Commons Attribution License (CC-BY)" on 2 July 2025; using the data after that date means accepting it | 🟢 |
| Per-dataset check (CDS catalogue API, `license` field) | `reanalysis-era5-land-monthly-means` → CC-BY-4.0 (DOI 10.24381/cds.68d2bb30) · `reanalysis-era5-single-levels-monthly-means` → CC-BY-4.0 (10.24381/cds.f17050d7) · `derived-era5-land-daily-statistics` → CC-BY-4.0 (10.24381/cds.e9c9c792) · `derived-era5-single-levels-daily-statistics` → CC-BY-4.0 (10.24381/cds.4991cf48) | 🟢 |
| Attribution wording (CDS "how to acknowledge" page, updated 3 Jul 2025) | `[Generated using/Contains modified] Copernicus Climate Change Service information [year]` + "Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains." Plus the dataset citation from its CDS "References" tab | 🟢 wording / 🟡 the page doesn't say the disclaimer is required, but it costs nothing |
| Derived climatologies under CC BY? | CC BY 4.0 allows adaptation and redistribution, commercial use included, with credit and a note of changes. So our January mean and P10 can be published under CC BY 4.0 with the line "Contains modified Copernicus Climate Change Service information 2026" | 🟡 reasoned from the CC BY terms; no Copernicus text addresses derived products specifically |
| ERA5-Land paper | Muñoz-Sabater et al. (2021), ESSD 13, 4349–4383, doi:10.5194/essd-13-4349-2021; 9 km resolution | 🟢 |
| Old licence | `apps.ecmwf.int/datasets/licences/era5` still shows the legacy text ("Generated using / Contains modified Copernicus Climate Change Service information" + disclaimer). Same attribution, so nothing breaks | 🟢 |
| Caveat | A 9 km grid cell smooths valleys, coasts and towns; snap on cell, then optionally correct by the elevation difference (lapse rate) | 🟡 |
| **E-OBS** (gridded, CDS) | Licence is "other": "strictly for use in non-commercial research and education projects only" → **do not use** | 🟢 |

## 3. Town search data

| Source | Licence | Attribution | Use? | Conf. |
|---|---|---|---|---|
| **GeoNames** dumps | Readme: "licensed under a Creative Commons Attribution 4.0 License"; export page: "commercial usage is allowed", "as is" | "You should give credit to GeoNames when using data or web services with a link or another reference to GeoNames." Ours: `Town names and locations: GeoNames (geonames.org), CC BY 4.0` | ✅ primary. `cities5000` = pop > 5,000 or admin seat (~50k); `cities15000` (~25k); `cities1000`/`cities500` for villages | 🟢 |
| **Natural Earth** populated places | "All versions of Natural Earth raster + vector map data … are in the public domain" | None required; credit anyway | Fallback only (larger places) | 🟢 licence / 🟡 coverage |
| **Eurostat GISCO** LAU / NUTS / cities | "Use is granted on condition that the data is not used for commercial purposes"; notice `© EuroGeographics for the administrative boundaries` (FR: `© EuroGeographics pour les limites administratives`, DE: `© EuroGeographics bezüglich der Verwaltungsgrenzen`) in map legend and intro page. LAU includes population per LAU | ❌ skip: affiliate/partner revenue (WS5) makes us commercial. Commercial use needs a EuroGeographics licence | 🟢 |

## 4. National met services (Jan mean + P10)

P10 is never published ready-made. We compute it from daily data (P10 of the 1991–2020 January daily means), so "available" means daily data is open.

| Country | Service / dataset | Jan mean | Daily data for P10 | Licence | Conf. |
|---|---|---|---|---|---|
| NL | KNMI Data Platform: "Climate normals 1991–2020 day normals by station (AWS)" and "per 10 days"; daily station data (etmaalgegevens; the dataset page is marked DEPRECATED; successor not checked) | ✅ | ✅ | CC BY 4.0 ("No use limitations") | 🟢 licence / 🟡 exact variables not listed on the pages opened |
| DE | DWD CDC opendata: `multi_annual/mean_91-20/Temperatur_1991-2020.txt` (+ station list); `daily/kl` station daily; HYRAS-DE daily grids (`air_temperature_mean/min/max`) | ✅ | ✅ (stations + grid) | CC BY 4.0 (CDC Terms of use, status May 2024; details dwd.de/copyright) | 🟢 |
| FR | Météo-France via meteo.data.gouv.fr: "Données climatologiques de base – quotidiennes", all stations since opening; also homogenised series and SAFRAN-SIM2 reanalysis | 🟡 compute from daily; a ready normals dataset not confirmed | ✅ | Licence Ouverte / Open Licence 2.0 (data.gouv.fr dataset page) | 🟢 daily / 🔴 normals product not checked (search budget ran out) |
| BE | KMI-IRM AWS daily observations (Belgian Climate Centre portal), from 1995 | ✅ (compute) | ✅ | CC BY 4.0 (publisher KMI) | 🟢 |
| BE | KMI 5×5 km daily gridded Tmin/Tmax from 1961 | — | — | "alleen beschikbaar voor wetenschappelijk onderzoek" (research only) → ❌ | 🟢 |
| BE | KMI homogenised monthly temperature series (61 stations) | ✅ | ❌ | Not stated on the news page | 🟡 |
| UK | Met Office **HadUK-Grid**: 1 km; daily tasmax/tasmin 1960–present; monthly; 1991–2020 climatology | ✅ | ✅ (daily mean = (tasmax+tasmin)/2) | Open Government Licence v3; footer "© Crown Copyright" | 🟢 licence / 🟡 whether CEDA download needs an account |
| UK | Met Office **MIDAS Open** daily temperature (max/min air temp) | ✅ | ✅ | OGL v3, "Permitted Use: Any"; **needs a CEDA account** → ask Menno before registering; cite "Met Office (2024): MIDAS Open: UK daily temperature data, v202407" (record marked superseded, use the newest version) | 🟢 |
| NO | MET Norway (Frost API) | ✅ | ✅ | NLOD and CC BY 4.0; credit "Data from The Norwegian Meteorological Institute" / "Based on data from MET Norway". Frost access terms not opened | 🟢 licence / 🔴 registration need |
| US | NOAA NCEI U.S. Climate Normals 1991–2020 (daily) | ✅ (Tmin/Tmax normals) | Percentiles listed only for precipitation, not temperature → compute from GHCN-Daily | Metadata page names no licence; Meteostat tags GHCN-Daily CC0 1.0; US federal works are normally public domain. Cite Palecki et al. (2021), doi:10.25921/d3w1-ef83 | 🟡 |
| AU | Bureau of Meteorology | — | — | Default terms are **not open**: personal or internal use only unless a page says CC BY; commercial or redistribution needs permission → ❌ use ERA5-Land for AU | 🟢 |

**Why ERA5-Land first:** national services are open in NL/DE/FR/BE/UK/NO, but each has its own format, station density and licence line. ERA5-Land covers all of them, plus AU, under one licence. National data then becomes the second source the product rules want for headline fields.

## 5. Open points for WS1 (T-034)

- 🟡 Define P10 as the 10th percentile of **January daily mean** temperature, 1991–2020 (matches how consumption tests quote ambient temperature). Log it in DECISIONS if WS1 agrees.
- 🔴 Ask Menno before creating any CEDA (MIDAS Open), MET Norway Frost or CDS account. Downloading ERA5-Land very likely needs a CDS account (🟡 from prior knowledge, not checked this session), so this is the first question for QUESTIONS.md.
- 🟡 Show one credit block: Copernicus line + Meteostat + providers + GeoNames, in the footer and on the Nerd panel.

## Sources (all opened 2026-11-15)

- Meteostat licence: https://dev.meteostat.net/license 🟢
- Meteostat terms: https://dev.meteostat.net/terms 🟢
- Meteostat sources page (WMO Resolution 40 note only): https://dev.Meteostat.net/sources.html
- Meteostat `License` class: https://dev.meteostat.net/python/api/meteostat.License
- Meteostat Python 2.2.3 wheel from PyPI (`meteostat/providers/index.py`, `utils/data.py`, `api/normals.py`) read locally
- ECMWF forum, CC-BY replaces Copernicus licence: https://forum.ecmwf.int/t/cc-by-licence-to-replace-licence-to-use-copernicus-products-on-02-july-2025/13464
- CDS catalogue API: https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-land-monthly-means (and `/reanalysis-era5-single-levels-monthly-means`, `/derived-era5-land-daily-statistics`, `/derived-era5-single-levels-daily-statistics`, `/insitu-gridded-observations-europe`)
- CC-BY licence page (EWDS copy): https://ewds.climate.copernicus.eu/licences/cc-by
- CDS how to acknowledge and cite: https://confluence.ecmwf.int/spaces/CKB/pages/197704114/How+to+acknowledge+and+cite+a+Climate+Data+Store+CDS+catalogue+entry+and+the+data+published+as+part+of+it
- Legacy ERA5 licence: https://apps.ecmwf.int/datasets/licences/era5
- ERA5-Land paper: https://essd.copernicus.org/articles/13/4349/2021/essd-13-4349-2021.html
- E-OBS licence: https://ads.atmosphere.copernicus.eu/licences/licence-to-use-E-OBS-products
- GeoNames export page: http://www.geonames.org/export/ · readme: http://download.geonames.org/export/dump/readme.txt
- Natural Earth: https://www.naturalearthdata.com/about/
- GISCO statistical units (copyright notice): https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units · LAU: https://ec.europa.eu/eurostat/en/web/gisco/geodata/statistical-units/local-administrative-units
- KNMI 10-day normals: https://dataplatform.knmi.nl/dataset/climate-normals-1991-2020-per-10-days-by-station-1 · day normals: https://nationaalgeoregister.nl/geonetwork/srv/metadata/5a1b6db0-0682-11ec-9fb2-059654019e08 · daily: https://dataplatform.knmi.nl/dataset/groups/etmaalgegevensknmistations-1
- DWD CDC terms: https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf · normals folder: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/multi_annual/mean_91-20/ · HYRAS daily: https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/hyras_de/
- Météo-France daily: https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-quotidiennes · launch post: https://www.data.gouv.fr/posts/lancement-de-meteo-data-gouv-fr
- KMI AWS daily: https://data-portal.climatecentre.be/dataset/observations-quotidiennes-des-stations-meteorologiques-automatiques-aws · KMI release news: https://www.meteo.be/nl/info/nieuwsoverzicht/lancering-van-historische-klimaatgegevens-in-opendata-in-samenwerking-met-het-belgian-climate-centre
- HadUK-Grid: https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/overview · https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets
- MIDAS Open: https://catalogue.ceda.ac.uk/uuid/b7c6295b72c54fa9bcd8308fea2727e7/
- MET Norway licensing: https://www.met.no/en/free-meteorological-data/Licensing-and-crediting
- NOAA daily normals: https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C01621/html
- BOM copyright: https://www.bom.gov.au/copyright
- Not opened: dev.meteostat.net/bulk/normals.html (fetch blocked), cds.climate.copernicus.eu/licences (used the catalogue API instead), Météo-France normals product, Frost terms.

## Ready-to-import `data/sources.yaml` rows

```yaml
  - {id: era5-land, name: "ERA5-Land daily statistics + monthly means (C3S)", owner: ECMWF / Copernicus Climate Change Service, licence: CC-BY-4.0, access: api, cadence: yearly, status: active,
     terms: "CC BY since 2025-07-02 (CDS catalogue license field checked 2026-11-15). Credit: 'Contains modified Copernicus Climate Change Service information 2026' + EC/ECMWF disclaimer + DOI 10.24381/cds.e9c9c792 / 10.24381/cds.68d2bb30. Download likely needs a CDS account (not checked; ask Menno)."}
  - {id: meteostat, name: Meteostat climate data, owner: Meteostat, licence: CC-BY-4.0, access: bulk, cadence: yearly, status: active,
     terms: "Licence page checked 2026-11-15. Credit Meteostat AND the original provider per row. Drop rows from METAR (no named licence). Normals = monthly means only; P10 needs daily."}
  - {id: geonames, name: GeoNames cities, owner: GeoNames, licence: CC-BY-4.0, access: bulk, cadence: monthly, status: active,
     terms: "Readme checked 2026-11-15; commercial use allowed. Credit 'GeoNames (geonames.org), CC BY 4.0'. Round coordinates."}
  - {id: natural-earth, name: Natural Earth populated places, owner: Natural Earth, licence: Public-Domain, access: bulk, cadence: ad hoc, status: active,
     terms: "Fallback town list only (large places)."}
  - {id: knmi, name: KNMI climate normals 1991-2020 + daily station data, owner: KNMI (NL), licence: CC-BY-4.0, access: api, cadence: yearly, status: active,
     terms: "Licence in dataset metadata, checked 2026-11-15. Daily dataset page marked deprecated; find the current successor before ingest (not checked)."}
  - {id: dwd-cdc, name: DWD Climate Data Center (normals 1991-2020, daily kl, HYRAS-DE), owner: Deutscher Wetterdienst (DE), licence: CC-BY-4.0, access: bulk, cadence: yearly, status: active,
     terms: "CDC Terms of use (status May 2024), checked 2026-11-15. Credit 'Deutscher Wetterdienst'."}
  - {id: meteofrance-daily, name: "Météo-France données climatologiques de base (quotidiennes)", owner: Météo-France (FR), licence: Licence-Ouverte-2.0, access: bulk, cadence: monthly, status: active,
     terms: "Licence on data.gouv.fr dataset page, checked 2026-11-15. Credit 'Météo-France'."}
  - {id: kmi-aws, name: KMI-IRM AWS daily observations, owner: KMI-IRM (BE), licence: CC-BY-4.0, access: api, cadence: yearly, status: active,
     terms: "Belgian Climate Centre portal, checked 2026-11-15. From 1995. The 5 km gridded product is research-only: not used."}
  - {id: haduk-grid, name: Met Office HadUK-Grid (1 km, daily + 1991-2020 climatology), owner: Met Office (UK), licence: OGL-UK-3.0, access: bulk, cadence: yearly, status: active,
     terms: "Checked 2026-11-15. Credit wording not stated on the pages opened (footer shows '© Crown Copyright'); confirm OGL attribution and whether CEDA download needs an account."}
  - {id: midas-open, name: Met Office MIDAS Open daily temperature, owner: Met Office (UK), licence: OGL-UK-3.0, access: bulk, cadence: yearly, status: blocked,
     terms: "Licence fine; needs a CEDA account (ask Menno first)."}
  - {id: metno-frost, name: MET Norway observations (Frost), owner: MET Norway (NO), licence: CC-BY-4.0, access: api, cadence: yearly, status: blocked,
     terms: "NLOD + CC BY 4.0 (checked 2026-11-15). Credit 'Based on data from MET Norway'. Access registration not checked; ask Menno before signing up."}
  - {id: noaa-normals, name: NOAA NCEI U.S. Climate Normals 1991-2020 + GHCN-Daily, owner: NOAA NCEI (US), licence: US-Government-Public-Domain (to confirm), access: bulk, cadence: decadal, status: blocked,
     terms: "Metadata names no licence; Meteostat tags GHCN-D CC0. Cite doi:10.25921/d3w1-ef83."}
  - {id: bom, name: Bureau of Meteorology climate data, owner: BoM (AU), licence: none, access: manual, cadence: ad hoc, status: blocked,
     terms: "Default terms: personal/internal use only unless a page says CC BY. Use ERA5-Land for AU."}
  - {id: eobs, name: E-OBS gridded observations, owner: ECA&D / KNMI, licence: none, access: bulk, cadence: yearly, status: blocked,
     terms: "Non-commercial research and education only."}
  - {id: gisco-lau, name: Eurostat GISCO LAU / NUTS / cities, owner: Eurostat / EuroGeographics, licence: none, access: bulk, cadence: yearly, status: blocked,
     terms: "Non-commercial only; '© EuroGeographics for the administrative boundaries'. Commercial use needs a EuroGeographics licence."}
```
