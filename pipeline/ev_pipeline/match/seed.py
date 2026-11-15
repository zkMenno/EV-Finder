"""Load the hand-curated seed: data/seed/models.yaml (+ optional data/seed/variants.yaml)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.match.normalise import key, tokens
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, FactField, Source

# Make spellings seen in registration data that the seed cannot know about. Keys are
# normalised (see normalise.key). Kept tiny on purpose: add a line when unmatched.csv shows one.
MAKE_ALIASES: dict[str, str] = {
    "vw": "volkswagen",
    "mercedesbenz": "mercedes",
    "vauxhall": "opel",
    "bmwi": "bmw",
    "teslamotors": "tesla",
}

SEED_MANUAL_SOURCE_ID = "seed-manual"


@dataclass
class SeedGeneration:
    id: str
    model_id: str
    name: str
    year_start: int
    year_end: int | None
    uncertain: bool = False
    notes: str | None = None
    change_markers: list[dict[str, Any]] = field(default_factory=list)

    def covers(self, year: int) -> bool:
        return self.year_start <= year and (self.year_end is None or year <= self.year_end)


@dataclass
class SeedModel:
    id: str
    make_id: str
    name: str
    segment: str | None
    body: str | None
    aliases: list[str]
    generations: list[SeedGeneration]


@dataclass
class SeedMake:
    id: str
    name: str
    models: list[SeedModel]


@dataclass
class Seed:
    makes: dict[str, SeedMake]
    make_keys: dict[str, str]  # normalised make key -> make id
    models: dict[str, SeedModel]
    generations: dict[str, SeedGeneration]

    def make_id_for(self, make: str) -> str | None:
        k = key(make)
        if k in self.make_keys:
            return self.make_keys[k]
        return self.make_keys.get(MAKE_ALIASES.get(k, ""))


def parse_seed(data: dict[str, Any]) -> Seed:
    makes: dict[str, SeedMake] = {}
    make_keys: dict[str, str] = {}
    models: dict[str, SeedModel] = {}
    gens: dict[str, SeedGeneration] = {}
    for mk in data.get("makes", []):
        make_models: list[SeedModel] = []
        for md in mk.get("models", []):
            mgens: list[SeedGeneration] = []
            for g in md.get("generations", []):
                years = g.get("years") or [None, None]
                sg = SeedGeneration(
                    id=g["id"],
                    model_id=md["id"],
                    name=g.get("name", g["id"]),
                    year_start=int(years[0]),
                    year_end=None if years[1] is None else int(years[1]),
                    uncertain=bool(g.get("uncertain", False)),
                    notes=g.get("notes"),
                    change_markers=list(g.get("change_markers") or []),
                )
                mgens.append(sg)
                gens[sg.id] = sg
            sm = SeedModel(
                id=md["id"],
                make_id=mk["id"],
                name=md["name"],
                segment=md.get("segment"),
                body=md.get("body"),
                aliases=list(md.get("name_aliases") or []),
                generations=sorted(mgens, key=lambda g: g.year_start),
            )
            make_models.append(sm)
            models[sm.id] = sm
        makes[mk["id"]] = SeedMake(id=mk["id"], name=mk["name"], models=make_models)
        make_keys[key(mk["name"])] = mk["id"]
        make_keys[key(mk["id"])] = mk["id"]
    return Seed(makes=makes, make_keys=make_keys, models=models, generations=gens)


def load_seed(path: Path) -> Seed:
    return parse_seed(yaml.safe_load(path.read_text(encoding="utf-8")))


# --- seed-manual variants (data/seed/variants.yaml) ------------------------------------

# Units implied by field name in variants.yaml (metric, see AGENTS.md data rule 6).
CANONICAL_UNITS: dict[str, str] = {
    "battery_kwh_net": "kWh",
    "battery_kwh_gross": "kWh",
    "wltp_range_km": "km",
    "epa_range_km": "km",
    "real_range_km": "km",
    "consumption_kwh_100km": "kWh/100km",
    "ac_kw": "kW",
    "dc_peak_kw": "kW",
    "dc_avg_10_80_kw": "kW",
    "power_kw": "kW",
    "accel_0_100_s": "s",
    "top_speed_kmh": "km/h",
    "boot_l": "l",
    "frunk_l": "l",
    "length_mm": "mm",
    "width_mm": "mm",
    "height_mm": "mm",
    "wheelbase_mm": "mm",
    "weight_kg": "kg",
    "towing_kg": "kg",
    "seats": "count",
    "registered_count": "count",
    "dc_curve": "kW",
    "dc_minutes_10_80": "min",
    "dc_peak_kw_claim": "kW",
    "consumption_motorway_kwh_100km": "kWh/100km",
    "real_range_summer_km": "km",
    "real_range_motorway_km": "km",
    "real_range_winter_km": "km",
    "voltage_nominal_v": "V",
    "voltage_max_v": "V",
    "warranty_years": "years",
    "warranty_km": "km",
    # id-valued fields (Decision 010): values are taxonomy ids, unit "id".
    "chemistry_id": "id",
    "cooling_id": "id",
    "cell_format": "id",
    "charger_400v_behaviour": "id",
    # price_new: unit is the currency code, so it cannot be implied.
}


@dataclass
class ManualVariant:
    """A hand-entered variant: id and generation are given, so it skips name matching."""

    id: str
    generation_id: str
    name: str
    year_start: int | None
    year_end: int | None
    record: SourceRecord


def parse_manual_variants(
    data: dict[str, Any], retrieved_at: date
) -> tuple[list[ManualVariant], list[str]]:
    """Returns (variants, problems). Problems are human-readable and go to validation.csv."""
    src = data.get("source") or {}
    source = Source(
        id=src.get("id", SEED_MANUAL_SOURCE_ID),
        name=src.get("name", "EV Finder seed (hand-entered, unchecked)"),
        licence=src.get("licence", "CC-BY-4.0"),
        url=src.get("url"),
        attribution=src.get("attribution"),
    )
    out: list[ManualVariant] = []
    problems: list[str] = []
    valid_fields = {f.value for f in FactField}
    for v in data.get("variants") or []:
        vid = v.get("id")
        gid = v.get("generation_id")
        if not vid or not gid:
            problems.append(f"variant without id/generation_id: {v!r:.80}")
            continue
        years = v.get("years") or [None, None]
        specs: dict[FactField, SpecValue] = {}
        for fname, value in (v.get("specs") or {}).items():
            if value is None:
                continue
            if fname not in valid_fields:
                problems.append(f"{vid}: unknown field {fname}")
                continue
            if fname == "price_new" or fname not in CANONICAL_UNITS:
                problems.append(f"{vid}: {fname} needs an explicit unit; skipped")
                continue
            if fname == "dc_curve" and isinstance(value, list):
                curve = {"points": value, "status": "estimated"}
                specs[FactField(fname)] = SpecValue(value=json.dumps(curve), unit="kW")
                continue
            if isinstance(value, bool) or not isinstance(value, int | float):
                problems.append(f"{vid}: {fname} is not a number ({value!r})")
                continue
            specs[FactField(fname)] = SpecValue(value=float(value), unit=CANONICAL_UNITS[fname])
        conf = v.get("confidence", "low")
        record = SourceRecord(
            source=source,
            record_key=vid,
            kind="spec",
            make="",
            model="",
            variant_name=v.get("name"),
            year=years[0],
            drivetrain=v.get("drivetrain"),
            specs=specs,
            retrieved_at=retrieved_at,
            confidence=Confidence(conf),
        )
        out.append(
            ManualVariant(
                id=vid,
                generation_id=gid,
                name=v.get("name") or vid,
                year_start=years[0],
                year_end=years[1] if len(years) > 1 else None,
                record=record,
            )
        )
    return out, problems


def load_manual_variants(path: Path) -> tuple[list[ManualVariant], list[str]]:
    # No retrieval date in the file: use its modification date (stable while the file is).
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).date()
    return parse_manual_variants(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, mtime)


def model_alias_keys(model: SeedModel) -> set[str]:
    """Normalised keys a source may use for this model, with and without the make name."""
    make_toks = tokens(model.make_id)
    out: set[str] = set()
    for name in [model.name, *model.aliases]:
        toks = tokens(name)
        if not toks:
            continue
        out.add("".join(toks))
        if toks[: len(make_toks)] == make_toks and len(toks) > len(make_toks):
            out.add("".join(toks[len(make_toks) :]))
    return out
