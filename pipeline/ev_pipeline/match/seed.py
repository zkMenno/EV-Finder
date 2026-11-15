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
    "mgroewe": "mg",  # KBA FZ10 files MG as "MG ROEWE"
    "opelvauxhall": "opel",  # KilowattApp
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
    # Names that start like this model but are a different car ("e-tron GT" vs "e-tron").
    # A record whose name contains one of these (as whole tokens) never matches this model.
    name_excludes: list[str] = field(default_factory=list)
    # Bare trade names ("KONA", "208") that mean this electric model only in sources that hold
    # nothing but BEVs (matcher.BEV_FILTERED_SOURCES). Exact whole-name match, never a prefix.
    bev_only_aliases: list[str] = field(default_factory=list)
    # Names one source uses for this model, valid for that source only (`source_aliases:
    # {kba-fz10: ["4ER", {name: "ID.4, ID.5", note: "..."}]}`). Prefix match like
    # `name_aliases`; an alias may start with a make the seed lacks ("SEAT BORN"). A `note`
    # travels with the matched counts into the release provenance.
    source_aliases: dict[str, list[SourceAlias]] = field(default_factory=dict)
    # Q-021: one explicit, general list of names per source (`aliases_by_source`), used when
    # scoped aliases are on (matcher.scoped_aliases_enabled). Replaces `bev_only_aliases` and
    # `source_aliases` for a model that has it; a model without it keeps the legacy keys.
    # Keys are source ids, or several joined by commas ("rdw,eea"). Entries: a bare string
    # (whole-name match) or {name, match: exact|prefix, note}. `None` = key absent.
    aliases_by_source: dict[str, list[SourceAlias]] | None = None


ALIAS_MATCH_MODES = ("exact", "prefix")


@dataclass(frozen=True)
class SourceAlias:
    name: str
    note: str | None = None
    match: str = "prefix"  # exact: whole name only; prefix: leading tokens (like name_aliases)


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
    # Q-021: make spellings one source uses (`make_aliases_by_source` on a make in models.yaml,
    # e.g. EEA "VOLKSWAGEN, VW", OpenEV "MG Motor"): source id -> normalised key -> make id.
    # Used only when scoped aliases are on.
    make_source_keys: dict[str, dict[str, str]] = field(default_factory=dict)

    def make_id_for(
        self, make: str, source_id: str | None = None, scoped: bool = False
    ) -> str | None:
        k = key(make)
        if k in self.make_keys:
            return self.make_keys[k]
        if scoped and source_id is not None:
            hit = self.make_source_keys.get(source_id, {}).get(k)
            if hit is not None:
                return hit
        return self.make_keys.get(MAKE_ALIASES.get(k, ""))


def parse_seed(data: dict[str, Any]) -> Seed:
    makes: dict[str, SeedMake] = {}
    make_keys: dict[str, str] = {}
    models: dict[str, SeedModel] = {}
    gens: dict[str, SeedGeneration] = {}
    make_source_keys: dict[str, dict[str, str]] = {}
    for mk in data.get("makes", []):
        for sids, names in (mk.get("make_aliases_by_source") or {}).items():
            for sid in [x.strip() for x in str(sids).split(",") if x.strip()]:
                for n in names or []:
                    k = key(str(n))
                    prev = make_source_keys.setdefault(sid, {}).get(k)
                    if not k or (prev is not None and prev != mk["id"]):
                        raise ValueError(f"make alias {n!r} for {sid}: empty or on two makes")
                    make_source_keys[sid][k] = mk["id"]
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
                name_excludes=list(md.get("name_excludes") or []),
                bev_only_aliases=list(md.get("bev_only_aliases") or []),
                source_aliases=_parse_source_aliases(md.get("source_aliases")),
                aliases_by_source=(
                    _parse_aliases_by_source(md["aliases_by_source"], md["id"])
                    if "aliases_by_source" in md
                    else None
                ),
            )
            make_models.append(sm)
            models[sm.id] = sm
        makes[mk["id"]] = SeedMake(id=mk["id"], name=mk["name"], models=make_models)
        make_keys[key(mk["name"])] = mk["id"]
        make_keys[key(mk["id"])] = mk["id"]
    return Seed(
        makes=makes,
        make_keys=make_keys,
        models=models,
        generations=gens,
        make_source_keys=make_source_keys,
    )


def _parse_source_aliases(raw: Any) -> dict[str, list[SourceAlias]]:
    out: dict[str, list[SourceAlias]] = {}
    for sid, items in (raw or {}).items():
        for it in items or []:
            if isinstance(it, str):
                out.setdefault(str(sid), []).append(SourceAlias(it))
            elif isinstance(it, dict) and it.get("name"):
                out.setdefault(str(sid), []).append(SourceAlias(str(it["name"]), it.get("note")))
            else:
                raise ValueError(f"bad source_aliases entry for {sid}: {it!r}")
    return out


def _parse_aliases_by_source(raw: Any, model_id: str) -> dict[str, list[SourceAlias]]:
    """`aliases_by_source` (Q-021). A bare string is a whole-name (exact) alias, the safe
    default for bare trade names like "KONA"; a dict may ask for `match: prefix`."""
    out: dict[str, list[SourceAlias]] = {}
    for keys, items in (raw or {}).items():
        sids = [s.strip() for s in str(keys).split(",") if s.strip()]
        if not sids:
            raise ValueError(f"{model_id}: aliases_by_source has an empty source key")
        for it in items or []:
            if isinstance(it, str | int | float) and not isinstance(it, bool):
                alias = SourceAlias(str(it), None, "exact")
            elif isinstance(it, dict) and it.get("name") is not None:
                mode = str(it.get("match", "exact"))
                if mode not in ALIAS_MATCH_MODES:
                    raise ValueError(f"{model_id}: aliases_by_source match {mode!r} unknown")
                alias = SourceAlias(str(it["name"]), it.get("note"), mode)
            else:
                raise ValueError(f"{model_id}: bad aliases_by_source entry for {keys}: {it!r}")
            for sid in sids:
                out.setdefault(sid, []).append(alias)
    return out


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
    # Decision 023: separate fields, never used to fill WLTP / kerb weight / peak power.
    "nedc_range_km": "km",
    "nedc_consumption_kwh_100km": "kWh/100km",
    "wltp_range_km_worst": "km",
    "wltp_consumption_kwh_100km_worst": "kWh/100km",
    "mass_running_order_kg": "kg",
    "power_30min_kw": "kW",
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
    # Q-062: the names other sources give this same car (`source_names: {openev: [Standard,
    # "Standard Range"]}` in variants.yaml; keys may be "a,b"). Source id -> normalised keys.
    # A record of that source with that variant name in this generation joins this variant
    # instead of making a near-duplicate row of its own.
    source_names: dict[str, set[str]] = field(default_factory=dict)


def parse_source_names(raw: Any, vid: str) -> dict[str, set[str]]:
    """`source_names` of one seed-manual variant -> source id -> normalised name keys."""
    out: dict[str, set[str]] = {}
    if raw is None:
        return out
    if not isinstance(raw, dict):
        raise ValueError(f"{vid}: source_names must map source ids to lists of names")
    for keys, names in raw.items():
        sids = [x.strip() for x in str(keys).split(",") if x.strip()]
        if not sids or not isinstance(names, list):
            raise ValueError(f"{vid}: bad source_names entry {keys!r}: {names!r}")
        for n in names:
            k = key(str(n))
            if not k:
                raise ValueError(f"{vid}: empty name in source_names for {keys}")
            for sid in sids:
                out.setdefault(sid, set()).add(k)
    return out


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
                source_names=parse_source_names(v.get("source_names"), vid),
            )
        )
    return out, problems


def load_manual_variants(path: Path) -> tuple[list[ManualVariant], list[str]]:
    # No retrieval date in the file: use its modification date (stable while the file is).
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).date()
    return parse_manual_variants(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, mtime)


def _with_and_without_make(model: SeedModel, names: list[str]) -> set[str]:
    make_toks = tokens(model.make_id)
    out: set[str] = set()
    for name in names:
        toks = tokens(name)
        if not toks:
            continue
        out.add("".join(toks))
        if toks[: len(make_toks)] == make_toks and len(toks) > len(make_toks):
            out.add("".join(toks[len(make_toks) :]))
    return out


def model_bev_only_keys(model: SeedModel) -> set[str]:
    """Normalised whole-name keys of `bev_only_aliases` (with and without the make name)."""
    return _with_and_without_make(model, model.bev_only_aliases)


def model_exclude_tokens(model: SeedModel) -> list[list[str]]:
    """Token lists of `name_excludes`; matched as a contiguous run anywhere in a name."""
    return [t for t in (tokens(n) for n in model.name_excludes) if t]


def model_source_alias_keys(model: SeedModel, source_id: str) -> dict[str, SourceAlias]:
    """Normalised keys of this model's aliases for one source (with and without the make)."""
    out: dict[str, SourceAlias] = {}
    for a in model.source_aliases.get(source_id, []):
        for k in _with_and_without_make(model, [a.name]):
            out[k] = a
    return out


def model_scoped_alias_keys(
    model: SeedModel, source_id: str
) -> tuple[dict[str, SourceAlias], dict[str, SourceAlias]]:
    """(prefix keys, exact keys) of this model's `aliases_by_source` for one source, with and
    without the make name. Empty when the model has no `aliases_by_source`."""
    prefix: dict[str, SourceAlias] = {}
    exact: dict[str, SourceAlias] = {}
    for a in (model.aliases_by_source or {}).get(source_id, []):
        target = exact if a.match == "exact" else prefix
        for k in _with_and_without_make(model, [a.name]):
            target[k] = a
    return prefix, exact


def model_alias_keys(model: SeedModel) -> set[str]:
    """Normalised keys a source may use for this model, with and without the make name."""
    return _with_and_without_make(model, [model.name, *model.aliases])
