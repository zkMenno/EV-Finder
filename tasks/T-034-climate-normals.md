# T-034 Climate normals + town search data
Role: WS1   Lane: pipeline   Wave: 7
Status: review (WS1, 2026-11-15)

## Goal
January (and cold-snap P10) temperatures per town for the winter default.

## Acceptance criteria
- [x] Meteostat licence confirmed per source before ingest (else Copernicus ERA5 monthly means)
- [x] GeoNames cities (CC BY 4.0) for launch countries with rounded coordinates
- [x] Attribution recorded in data/sources.yaml

## Inputs
docs/spec/trip-fit.md §7.

## Out of scope
Routing.

## Handoff notes
**WS1, 2026-11-15 (PR `t-034-climate-normals`).**
- Adapters: `sources/geonames` (cities5000 + alternatenames per country → names in en/nl/de/
  fr/es/it; fetch checks the readme licence line), `sources/meteostat` (bulk v2: stations,
  normals, daily; fetch checks the licence page; tries up to 4 stations per town until one
  has a full 1991–2020 January), `sources/era5_land` (stub, REQUIRES_ENV CDSAPI_KEY).
- Release: `release/towns.py` → `towns/<cc>.json` (be 24 KB, nl 20 KB, de 115 KB gzip).
  Shape: `sources`, `provenance.{towns,climate}`, `stations{id: …}`, `towns[{id, name,
  names, country, lat, lon, population, admin1, elevation_m, station_id, station_km}]`.
  Schema def requested from WS0 (TownsRelease).
- Live run today: 7,654 towns, 7,203 with climate, 451 without a station in 60 km (mostly
  FR/UK; ERA5-Land closes these), 10 without P10. Spot checks vs national normals: De Bilt
  Jan 3.6 °C (KNMI 3.4), Uccle 3.8, Berlin-Dahlem 1.0, Paris-Montsouris 5.3.
- 🟡 Meteostat bulk rows don't name their provider, so credit is generic and confidence
  medium. Licence basis: R-27 (Meteostat's own redistribution = CC BY 4.0).
- Proposed for DECISIONS (WS0): P10 = 10th percentile of January daily mean temperature
  1991–2020 (R-27 §6); towns take the nearest station within 60 km / 250 m, no interpolation.
- Next: ERA5-Land loader once the key arrives (Q-093) as primary, Meteostat as the second
  source per town; WS2 swaps `src/fixtures/towns.sample.json` for the release files.

## Review
