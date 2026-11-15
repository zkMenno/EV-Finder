"""KilowattApp "Open EV Data" adapter (MIT License with Attribution Requirement).

Raw layout (github.com/KilowattApp/open-ev-data, data/v2/README.md):

    LICENSE                    MIT + clause 2: visible attribution required
    data/v2/brands.json        {meta, brands: [{id, name, models_file}]}
    data/v2/models/<brand>.json {brand_id, brand_name, models: [vehicle, ...]}

`data/ev-data.json` (v1) holds the same 1,321 vehicles with the same ids (checked
2026-11-15); we read v2 because upstream calls it the current format.

Each car becomes one spec SourceRecord (confidence medium): usable battery, AC kW, DC peak
kW, average consumption (kWh/100km). A DC charging curve becomes a separate record
(confidence low, status `estimated`) so the curve can carry its own confidence. Upstream
does not document how curves were obtained, and its own tool generates template curves
(`lib/vehicle_creator/charging_details.rb`), so nothing is labelled `measured`.

Dropped on purpose (counted in the run log):
  * vehicle_type motorbike / microcar: not in our car catalogue;
  * curves with `is_default_charging_curve: true` (generated from a template), and
    unflagged curves whose shape is one of two generic templates (TEMPLATE_SHAPES);
  * DC data where dc max_power == usable_battery_size: a placeholder (1C) seen on 567 cars,
    e.g. Tesla Model 3 2023 "57.5 kW", Leaf 2022 "39 kW";
  * AC kW above 43 (these are DC figures in the AC field), consumption outside 10-40.
`charging_voltage` (400/800) is an architecture label, not a nominal voltage: not emitted.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import ChargeCurve, Conditions, Confidence, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "kilowatt-openev"
DIR = "kilowatt_openev"
REPO_URL = "https://github.com/KilowattApp/open-ev-data"
ATTRIBUTION = "Open EV Data (https://github.com/KilowattApp/open-ev-data)"

SOURCE = Source(
    id=NAME,
    name="Open EV Data (KilowattApp)",
    url=REPO_URL,
    licence="MIT-with-attribution",
    attribution=ATTRIBUTION,
)

AC_MAX_KW = 43.0
# Unflagged curves with exactly these shapes ((SoC %, share of peak kW)) are generic
# templates, not vehicle curves: 292 of the 729 non-placeholder, non-default curves on
# 2026-11-15 (174 + 118 cars), across unrelated makes. Treated like default curves.
TEMPLATE_SHAPES = {
    ((0.0, 1.0), (50.0, 1.0), (80.0, 0.6), (100.0, 0.3)),
    ((0.0, 1.0), (50.0, 1.0), (80.0, 0.5), (100.0, 0.2)),
}
CONSUMPTION_RANGE = (10.0, 40.0)  # kWh/100km, plausible for passenger cars


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if value > 0 else None


def load_vehicles(raw_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    """(models file relative to raw_dir, vehicle) for every vehicle listed in brands.json."""
    v2 = raw_dir / "data" / "v2"
    brands = json.loads((v2 / "brands.json").read_text(encoding="utf-8"))
    out: list[tuple[str, dict[str, Any]]] = []
    for models_file in sorted({b["models_file"] for b in brands["brands"]}):
        path = v2 / models_file
        doc = json.loads(path.read_text(encoding="utf-8"))
        rel = str(path.relative_to(raw_dir))
        out.extend((rel, vehicle) for vehicle in doc.get("models", []))
    return out


def dc_placeholder(vehicle: dict[str, Any]) -> bool:
    """DC max_power equal to the usable battery size is a 1C placeholder, not a spec."""
    dc_max = _num((vehicle.get("dc_charger") or {}).get("max_power"))
    battery = _num(vehicle.get("usable_battery_size"))
    return dc_max is not None and battery is not None and dc_max == battery


def is_template(curve: ChargeCurve) -> bool:
    points = [p.root for p in curve.points]
    peak = max(kw for _, kw in points)
    return tuple((soc, round(kw / peak, 2)) for soc, kw in points) in TEMPLATE_SHAPES


def charge_curve(dc: dict[str, Any]) -> ChargeCurve | None:
    """The DC curve as a ChargeCurve, or None if it is default, too short or invalid.

    Valid = at least two points, 0 <= SoC <= 100, kW >= 0, no repeated SoC. Points are
    sorted by SoC.
    """
    if dc.get("is_default_charging_curve", False) is not False:
        return None
    points: list[tuple[float, float]] = []
    for p in dc.get("charging_curve") or []:
        soc, kw = p.get("percentage"), p.get("power")
        if not all(isinstance(x, int | float) and not isinstance(x, bool) for x in (soc, kw)):
            return None
        if not 0 <= soc <= 100 or kw < 0:
            return None
        points.append((float(soc), float(kw)))
    points.sort()
    socs = [s for s, _ in points]
    if len(points) < 2 or len(set(socs)) != len(socs) or not any(kw > 0 for _, kw in points):
        return None
    return ChargeCurve(
        points=[[s, kw] for s, kw in points], status="estimated", conditions=Conditions()
    )


def _specs(vehicle: dict[str, Any], stats: Counter[str]) -> dict[FactField, SpecValue]:
    specs: dict[FactField, SpecValue] = {}
    if (battery := _num(vehicle.get("usable_battery_size"))) is not None:
        specs[FactField.battery_kwh_net] = SpecValue(value=battery, unit="kWh")
    ac = _num((vehicle.get("ac_charger") or {}).get("max_power"))
    if ac is not None:
        if ac <= AC_MAX_KW:
            specs[FactField.ac_kw] = SpecValue(value=ac, unit="kW")
        else:
            stats["ac_kw_implausible_dropped"] += 1
    dc = vehicle.get("dc_charger") or {}
    dc_max = _num(dc.get("max_power"))
    if dc_max is not None:
        if dc_placeholder(vehicle):
            stats["dc_placeholder_dropped"] += 1
        else:
            specs[FactField.dc_peak_kw] = SpecValue(value=dc_max, unit="kW")
    cons = _num((vehicle.get("energy_consumption") or {}).get("average_consumption"))
    if cons is not None:
        low, high = CONSUMPTION_RANGE
        if low <= cons <= high:
            specs[FactField.consumption_kwh_100km] = SpecValue(value=cons, unit="kWh/100km")
        else:
            stats["consumption_implausible_dropped"] += 1
    return specs


def normalise_with_stats(
    raw_dir: Path, retrieved_at: date
) -> tuple[list[SourceRecord], Counter[str]]:
    stats: Counter[str] = Counter()
    records: list[SourceRecord] = []
    for rel, vehicle in load_vehicles(raw_dir):
        stats["vehicles_in"] += 1
        if vehicle.get("vehicle_type", "car") != "car":
            stats[f"skipped_{vehicle.get('vehicle_type')}"] += 1
            continue
        key = f"{rel}#{vehicle['id']}"
        year = vehicle.get("release_year")
        common: dict[str, Any] = {
            "source": SOURCE,
            "make": str(vehicle.get("brand", "")).strip(),
            "model": str(vehicle.get("model", "")).strip(),
            "variant_name": str(vehicle.get("variant") or "").strip() or None,
            "year": year if isinstance(year, int) else None,
            "retrieved_at": retrieved_at,
        }
        specs = _specs(vehicle, stats)
        if specs:
            records.append(
                SourceRecord(record_key=key, specs=specs, confidence=Confidence.medium, **common)
            )
        dc = vehicle.get("dc_charger") or {}
        if not dc.get("charging_curve"):
            continue
        if dc.get("is_default_charging_curve", False) is not False:
            stats["curves_default_dropped"] += 1
            continue
        if dc_placeholder(vehicle):
            stats["curves_placeholder_dropped"] += 1
            continue
        curve = charge_curve(dc)
        if curve is None:
            stats["curves_invalid_dropped"] += 1
            continue
        if is_template(curve):
            stats["curves_template_dropped"] += 1
            continue
        stats["curves_kept"] += 1
        records.append(
            SourceRecord(
                record_key=f"{key}#dc_curve",
                specs={FactField.dc_curve: SpecValue(value=curve, unit="kW")},
                confidence=Confidence.low,
                **common,
            )
        )
    stats["records_out"] = len(records)
    return records, stats


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    return normalise_with_stats(raw_dir, retrieved_at)[0]


# --------------------------------------------------------------------------- commands


def fetch_cmd() -> int:
    target = c.raw_dir(DIR)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        clone = Path(tmp) / DIR
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", REPO_URL, str(clone)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"fetch {NAME}: git clone failed: {result.stderr.strip()}")
            return 1
        commit = subprocess.run(
            ["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        licence = (clone / "LICENSE").read_text(encoding="utf-8")
        if "Attribution Requirement" not in licence or ATTRIBUTION not in " ".join(licence.split()):
            print(f"fetch {NAME}: LICENSE no longer matches the recorded terms; not importing")
            return 1
        if target.exists():
            shutil.rmtree(target)
        clone.rename(target)
    c.write_fetch_meta(
        target,
        {"url": REPO_URL, "commit": commit, "licence_file_first_line": licence.splitlines()[0]},
    )
    vehicles = len(load_vehicles(target))
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{REPO_URL}@{commit}",
        output=c.rel(target),
        rows_out=vehicles,
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not (src / "data" / "v2" / "brands.json").is_file():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    meta = c.read_fetch_meta(src)
    records, stats = normalise_with_stats(src, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src) + (f"@{meta['commit']}" if meta.get("commit") else ""),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        stats=dict(sorted(stats.items())),
    )
    return 0
