"""OpenEV Data adapter (CDLA-Permissive-2.0).

Raw layout (github.com/open-ev-data/open-ev-data-dataset, docs/ARCHITECTURE.md):

    src/<make>/<model>/base.json
    src/<make>/<model>/<year>/<vehicle>.json             year base vehicle
    src/<make>/<model>/<year>/<vehicle>_<variant>.json   variant delta (has a `variant` key)

A canonical vehicle = base.json <- year base <- variant (objects deep-merge, arrays and
scalars replace). Each canonical vehicle becomes one spec SourceRecord; each EUR/GBP list
price for NL/DE/FR/BE/UK becomes an extra, country-scoped price record.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "openev"
REPO_URL = "https://github.com/open-ev-data/open-ev-data-dataset"

SOURCE = Source(
    id="openev",
    name="Open EV Data",
    url=REPO_URL,
    licence="CDLA-Permissive-2.0",
    attribution="Contains data from OpenEV Data (open-ev-data-dataset), CDLA-Permissive-2.0.",
)

# OpenEV body.style -> our Body enum values. Unlisted styles (pickup, quadricycle) stay unset.
BODY_MAP = {
    "hatchback": "hatchback",
    "sedan": "sedan",
    "fastback": "sedan",
    "wagon": "estate",
    "estate": "estate",
    "shooting_brake": "estate",
    "suv": "suv",
    "mini_suv": "suv",
    "suv_coupe": "suv",
    "crossover": "crossover",
    "coupe": "coupe",
    "mpv": "mpv",
    "minivan": "mpv",
    "van": "mpv",
    "convertible": "cabrio",
    "cabrio": "cabrio",
    "roadster": "cabrio",
}
DRIVETRAIN_MAP = {"fwd": "fwd", "rwd": "rwd", "awd": "awd", "4wd": "awd"}
# Countries we publish prices for, and the currency each must be in. OpenEV uses ISO "GB".
PRICE_COUNTRIES = {"NL": "EUR", "DE": "EUR", "FR": "EUR", "BE": "EUR", "GB": "GBP", "UK": "GBP"}
TRUSTED_SOURCE_TYPES = {"oem", "regulatory"}
GENERIC_CHEMISTRY = {"li-ion", "li_ion", "lithium-ion", "lithium_ion", "other", "unknown"}
COOLING_IDS = {"liquid", "air", "passive", "refrigerant", "none"}


# --------------------------------------------------------------------------- compile


def deep_merge(low: Any, high: Any) -> Any:
    """OpenEV merge rule: objects merge by key; scalars and arrays from `high` replace."""
    if isinstance(low, dict) and isinstance(high, dict):
        out = dict(low)
        for key, value in high.items():
            out[key] = deep_merge(low[key], value) if key in low else value
        return out
    return high


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_vehicles(src_root: Path) -> list[tuple[list[Path], dict[str, Any]]]:
    """Return (layer files, merged record) for every canonical vehicle under `src_root`."""
    out: list[tuple[list[Path], dict[str, Any]]] = []
    for base_path in sorted(src_root.glob("*/*/base.json")):
        model_dir = base_path.parent
        base = _load(base_path)
        for year_dir in sorted(p for p in model_dir.iterdir() if p.is_dir() and p.name.isdigit()):
            files = {p.stem: (p, _load(p)) for p in sorted(year_dir.glob("*.json"))}
            year_bases = {stem for stem, (_, d) in files.items() if "variant" not in d}
            for stem, (path, doc) in files.items():
                layers = [base_path]
                merged = base
                if "variant" in doc:
                    # Parent = the longest year-base stem that prefixes this file name. Some
                    # upstream files break the `<vehicle>_<variant>` naming rule; with no
                    # parent the variant compiles on top of base.json alone.
                    parents = [s for s in year_bases if stem.startswith(s + "_")]
                    if parents:
                        ppath, pdoc = files[max(parents, key=len)]
                        layers.append(ppath)
                        merged = deep_merge(merged, pdoc)
                layers.append(path)
                merged = deep_merge(merged, doc)
                merged.setdefault("year", int(year_dir.name))
                out.append((layers, merged))
    return out


# --------------------------------------------------------------------------- mapping


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if value > 0 else None


def _rated(rec: dict[str, Any], cycle: str) -> float | None:
    for entry in rec.get("range", {}).get("rated", []):
        if entry.get("cycle") == cycle:
            return _num(entry.get("range_km"))
    return None


def dc_avg_10_80(rec: dict[str, Any]) -> float | None:
    """Average DC power over 10->80 %: net kWh x 0.7 / hours.

    Uses a published 10-80 % charging time when present, else integrates a power_by_soc
    curve that covers 10-80 %. Needs the net capacity; returns None otherwise.
    """
    net = _num(rec.get("battery", {}).get("pack_capacity_kwh_net"))
    if net is None:
        return None
    minutes = dc_minutes_10_80(rec)
    if minutes:
        return round(net * 0.7 / (minutes / 60), 1)
    curve = rec.get("charging", {}).get("dc_charge_curve") or {}
    points = sorted(
        (p["soc_percent"], p["power_kw"])
        for p in curve.get("points", [])
        if curve.get("curve_type") == "power_by_soc" and _num(p.get("power_kw"))
    )
    if len(points) < 2 or points[0][0] > 10 or points[-1][0] < 80:
        return None

    def power_at(soc: float) -> float:
        for (s0, p0), (s1, p1) in zip(points, points[1:], strict=False):
            if s0 <= soc <= s1:
                return p0 if s1 == s0 else p0 + (p1 - p0) * (soc - s0) / (s1 - s0)
        return points[-1][1]

    hours = sum((net / 100) / power_at(soc + 0.5) for soc in range(10, 80))
    return round(net * 0.7 / hours, 1)


def _specs(rec: dict[str, Any]) -> dict[FactField, SpecValue]:
    specs: dict[FactField, SpecValue] = {}

    def put(field: FactField, value: Any, unit: str) -> None:
        number = _num(value)
        if number is not None:
            specs[field] = SpecValue(value=number, unit=unit)

    battery = rec.get("battery", {})
    put(FactField.battery_kwh_net, battery.get("pack_capacity_kwh_net"), "kWh")
    put(FactField.battery_kwh_gross, battery.get("pack_capacity_kwh_gross"), "kWh")
    put(FactField.wltp_range_km, _rated(rec, "wltp"), "km")
    put(FactField.epa_range_km, _rated(rec, "epa"), "km")

    eff = rec.get("efficiency", {})
    wh_km = _num(eff.get("energy_consumption_wh_per_km"))
    # The efficiency block has no cycle field: only take it when its note says WLTP.
    if wh_km is not None and "wltp" in str(eff.get("notes", "")).lower():
        put(FactField.consumption_kwh_100km, round(wh_km / 10, 2), "kWh/100km")

    charging = rec.get("charging", {})
    put(FactField.ac_kw, charging.get("ac", {}).get("max_power_kw"), "kW")
    put(FactField.dc_peak_kw, charging.get("dc", {}).get("max_power_kw"), "kW")
    put(FactField.dc_avg_10_80_kw, dc_avg_10_80(rec), "kW")

    powertrain = rec.get("powertrain", {})
    power = _num(powertrain.get("system_power_kw"))
    if power is None:
        motors = [_num(m.get("power_kw")) for m in powertrain.get("motors", [])]
        power = sum(m for m in motors if m) or None
    put(FactField.power_kw, power, "kW")

    perf = rec.get("performance", {})
    put(FactField.accel_0_100_s, perf.get("acceleration_0_100_kmh_s"), "s")
    put(FactField.top_speed_kmh, perf.get("top_speed_kmh"), "km/h")

    capacity = rec.get("capacity", {})
    put(FactField.boot_l, capacity.get("cargo_l"), "l")
    put(FactField.frunk_l, capacity.get("frunk_l"), "l")
    put(FactField.towing_kg, capacity.get("towing_braked_kg"), "kg")

    dims = rec.get("dimensions", {})
    put(FactField.length_mm, dims.get("length_mm"), "mm")
    put(FactField.width_mm, dims.get("width_mm"), "mm")
    put(FactField.height_mm, dims.get("height_mm"), "mm")
    put(FactField.wheelbase_mm, dims.get("wheelbase_mm"), "mm")

    put(FactField.weight_kg, rec.get("weights", {}).get("curb_weight_kg"), "kg")
    put(FactField.seats, rec.get("body", {}).get("seats"), "count")

    put(FactField.dc_minutes_10_80, dc_minutes_10_80(rec), "min")
    put(FactField.voltage_nominal_v, battery.get("pack_voltage_nominal_v"), "V")
    put(FactField.voltage_max_v, battery.get("pack_voltage_max_v"), "V")
    warranty = battery.get("warranty", {})
    put(FactField.warranty_years, warranty.get("years"), "years")
    put(FactField.warranty_km, warranty.get("distance_km"), "km")
    if chemistry := chemistry_id(battery):
        specs[FactField.chemistry_id] = SpecValue(value=chemistry, unit="id")
    cooling = battery.get("thermal_management")
    if cooling in COOLING_IDS:
        specs[FactField.cooling_id] = SpecValue(value=cooling, unit="id")
    # dc_curve: no OpenEV record carries `dc_charge_curve` (2026-11-15), and SpecValue cannot
    # hold a ChargeCurve yet (Q-009), so curves are not emitted.
    return specs


def chemistry_id(battery: dict[str, Any]) -> str | None:
    """Lowercase chemistry id (nmc, lfp, nca, ...). Generic "li-ion" is not a chemistry."""
    for value in (battery.get("cathode_material"), battery.get("chemistry")):
        text = str(value or "").strip().lower()
        if text and text not in GENERIC_CHEMISTRY:
            return text
    return None


def dc_minutes_10_80(rec: dict[str, Any]) -> float | None:
    """Fastest published 10->80 % DC charging time, in minutes."""
    times = [
        float(t["time_min"])
        for t in rec.get("charging", {}).get("charging_time", {}).get("dc", [])
        if t.get("from_soc_percent") == 10
        and t.get("to_soc_percent") == 80
        and _num(t.get("time_min"))
    ]
    return min(times) if times else None


def _variant_name(rec: dict[str, Any]) -> str | None:
    trim = rec.get("trim", {})
    trim_name = (trim.get("name") or "").strip()
    variant_name = ((rec.get("variant") or {}).get("name") or "").strip()
    if not variant_name:
        return trim_name or None
    # Variants often restate the trim ("Long Range" + "Long Range"): keep the longer label.
    if trim.get("slug") in (None, "base") or trim_name.lower() in variant_name.lower():
        return variant_name
    if variant_name.lower() in trim_name.lower():
        return trim_name
    return f"{trim_name} {variant_name}"


def _confidence(rec: dict[str, Any]) -> Confidence:
    types = {s.get("type") for s in rec.get("sources", [])}
    return Confidence.medium if types & TRUSTED_SOURCE_TYPES else Confidence.low


def _prices(rec: dict[str, Any]) -> list[tuple[Country, SpecValue]]:
    out: dict[Country, SpecValue] = {}
    for entry in rec.get("pricing", {}).get("msrp", []):
        country, currency = entry.get("country"), entry.get("currency")
        amount = _num(entry.get("amount"))
        if amount is None or PRICE_COUNTRIES.get(country or "") != currency:
            continue
        ours = Country("UK" if country == "GB" else country)
        out.setdefault(ours, SpecValue(value=amount, unit=currency))
    return sorted(out.items(), key=lambda kv: kv[0].value)


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for layers, rec in compile_vehicles(raw_dir / "src"):
        key = "+".join(str(p.relative_to(raw_dir)) for p in layers)
        drivetrain = DRIVETRAIN_MAP.get(rec.get("powertrain", {}).get("drivetrain", ""))
        common: dict[str, Any] = {
            "source": SOURCE,
            "make": rec.get("make", {}).get("name", ""),
            "model": rec.get("model", {}).get("name", ""),
            "variant_name": _variant_name(rec),
            "year": rec.get("year"),
            "body": BODY_MAP.get(rec.get("body", {}).get("style", "")),
            "drivetrain": drivetrain,
            "retrieved_at": retrieved_at,
            "confidence": _confidence(rec),
        }
        records.append(SourceRecord(record_key=key, specs=_specs(rec), **common))
        for country, price in _prices(rec):
            records.append(
                SourceRecord(
                    record_key=f"{key}#price_new:{country.value}",
                    country=country,
                    specs={FactField.price_new: price},
                    **common,
                )
            )
    return records


# --------------------------------------------------------------------------- commands


def fetch_cmd() -> int:
    target = c.raw_dir(NAME)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        clone = Path(tmp) / NAME
        try:
            cmd = net.git_clone_cmd(NAME, REPO_URL, str(clone))
        except (net.FetchBlocked, ValueError) as exc:
            print(f"fetch {NAME}: refusing to clone: {exc}")
            return 1
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"fetch {NAME}: git clone failed: {result.stderr.strip()}")
            return 1
        commit = subprocess.run(
            ["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        if target.exists():
            shutil.rmtree(target)
        clone.rename(target)
    licence_head = (target / "LICENCE").read_text(encoding="utf-8").splitlines()[0]
    c.write_fetch_meta(
        target, {"url": REPO_URL, "commit": commit, "licence_file_first_line": licence_head}
    )
    files = len(list((target / "src").rglob("*.json")))
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{REPO_URL}@{commit}",
        output=c.rel(target),
        rows_out=files,
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / NAME if from_fixtures else c.raw_dir(NAME)
    if not (src / "src").is_dir():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    meta = c.read_fetch_meta(src)
    records = normalise(src, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src) + (f"@{meta['commit']}" if meta.get("commit") else ""),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
    )
    return 0
