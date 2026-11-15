"""ERA5-Land adapter (CC BY 4.0), STUB until the Copernicus CDS key arrives (T-034, Q-093).

Decision 036 makes ERA5-Land daily statistics 1991-2020 the primary climate source; Meteostat
is the second. The key reaches the server env file through WS4 (never the repo). Until then
`ev refresh` skips this source (REQUIRES_ENV) and `ev fetch era5-land` says what is missing.

Planned request (CDS dataset `derived-era5-land-daily-statistics`, R-27):
- variable `2m_temperature`, statistic `daily_mean`, time zone UTC+00:00, frequency 1-hourly;
- months 01..12 (January for the mean + P10, the rest for the monthly means), years 1991-2020;
- area = bounding box of the launch countries (REQUEST_AREA), netCDF.
Then per 0.1° grid cell: monthly mean of daily means and the P10 of January daily means, the
same definitions as the Meteostat adapter, so `release/towns.py` can take a grid cell per town
(no station distance) and keep Meteostat as the second source per headline field.
Credit: "Contains modified Copernicus Climate Change Service information [year]" + the EC /
ECMWF disclaimer + DOI 10.24381/cds.e9c9c792.
"""

from __future__ import annotations

import os

NAME = "era5-land"
DIR = "era5_land"
STAGING_SUFFIX = ".climate.jsonl"
REQUIRES_ENV = ["CDSAPI_KEY"]
DATASET = "derived-era5-land-daily-statistics"
REQUEST = {
    "variable": ["2m_temperature"],
    "daily_statistic": "daily_mean",
    "time_zone": "utc+00:00",
    "frequency": "1_hourly",
    "year": [str(y) for y in range(1991, 2021)],
    "month": [f"{m:02d}" for m in range(1, 13)],
}
REQUEST_AREA = [61.0, -8.7, 41.3, 15.1]  # N, W, S, E: UK, NL, BE, DE, FR (mainland)
ATTRIBUTION = "Contains modified Copernicus Climate Change Service information {year}"


def fetch_cmd(client: object | None = None) -> int:
    if not os.environ.get("CDSAPI_KEY"):
        print(f"fetch {NAME}: needs CDSAPI_KEY (Copernicus CDS key via WS4, Q-093); skipped")
        return 1
    print(f"fetch {NAME}: stub. The CDS key is set, but the loader is not built yet (T-034).")
    return 1


def normalise_cmd(from_fixtures: bool) -> int:
    print(f"normalise {NAME}: stub, nothing to normalise yet (T-034)")
    return 1
