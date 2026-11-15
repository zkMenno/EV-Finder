"""Top-40 used EV models (ADDENDUM-6 P5): the ranking behind `data/seed/top40.yaml` and the
coverage report for those 40 models.

Run from `pipeline/`:

    uv run python -m ev_pipeline.qa.top40 build      # staging -> data/seed/top40.yaml
    uv run python -m ev_pipeline.qa.top40 coverage   # top40.yaml + latest release -> JSON
    uv run python -m ev_pipeline.qa.top40 coverage --md   # the same as Markdown tables

**Used window.** "Used" = fleet age 2-8 years in VIEW_YEAR (2026): first admission
USED_FIRST_YEAR..USED_LAST_YEAR (2018-2024, both inclusive). Only RDW (NL) carries the year of
first admission, so only NL can be cut to that window exactly.

**Ranking (PROVISIONAL, QUESTIONS Q-074).** Per country with a used-fleet count, a model's share
of that country's BEV total in the same source and period; the score is the mean of those
shares (countries: RANK_SOURCES). Today that is NL (RDW fleet, first admission 2018-2024) and
UK (DfT VEH0120 licensed BEV fleet, newest quarter, **all ages**: VEH0120 has no year, so
cars under 2 years old are included). DE/FR/BE have only *new* registrations in staging
(KBA FZ10 2025 and 2026 YTD, EEA 2025): those are listed as context per pick but are not
used-fleet counts, so they never enter the score. Counts of different sources, periods or
kinds are never added together.

**Grouping.** A count record is placed on a seed model with the release matcher's own model
lookup (`find_model_noted`, scoped aliases on), at model level (no generation needed). A
record the seed cannot place gets a proposed id `<make>-<model key>` from PROPOSED_RULES
(source-specific series names, e.g. KBA "X1" = BEV column of the X1 series = iX1) or the
generic first-token rule in `_generic_model_key`; those ids are flagged `in_seed: false`.

Coverage (`coverage`) reads the latest release catalogue: per headline field, how many of the
40 models have 2+ agreeing sources / 1 source / an estimate only / nothing (a model takes the
level that a majority of its variants reach; see `model_level`). Registrations are counted
per country from top40.yaml (sources with a count, not "agreeing": periods differ).
Generation years: Wikidata production start/end years (corroboration records) against the
seed generation boundaries (`generation_years_check`).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.match.matcher import (
    COUNT_KIND,
    count_period,
    find_by_source_alias,
    find_model_noted,
    match_view,
)
from ev_pipeline.match.normalise import key, tokens
from ev_pipeline.match.seed import MAKE_ALIASES, Seed, load_seed
from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import FactField

VIEW_YEAR = 2026
USED_MIN_AGE, USED_MAX_AGE = 2, 8
USED_FIRST_YEAR = VIEW_YEAR - USED_MAX_AGE  # 2018
USED_LAST_YEAR = VIEW_YEAR - USED_MIN_AGE  # 2024
TOP_N = 40
COVERAGE_TARGET = 0.80

COUNT_SOURCES = ("rdw", "dft-veh", "kba-fz10", "eea")
# Sources whose counts are a used-fleet measure and enter the score, with their country.
RANK_SOURCES = {"rdw": "NL", "dft-veh": "UK"}
COUNTRIES = ("NL", "DE", "FR", "BE", "UK")

# Make spellings of makes the seed lacks (or uses differently), normalised key -> make id.
MAKE_CANON: dict[str, str] = {
    **MAKE_ALIASES,
    "volkswagenvw": "volkswagen",
    "mercedesbenz": "mercedes",
    "mgroewe": "mg",
    "bmwag": "bmw",
    "bayermotwerkebmw": "bmw",
    "audiag": "audi",
    "audisport": "audi",
    "hyundaigenesis": "hyundai",
    "skodaauto": "skoda",
    "vauxhall": "opel",
}

# Source-specific series names for records the seed cannot place:
# (source id or "*", make id, regex on the model key after the make) -> (proposed id, name).
# KBA FZ10 reports Modellreihen; its BEV column of a mixed series is the electric model.
PROPOSED_RULES: list[tuple[str, str, str, str, str]] = [
    ("kba-fz10", "bmw", r"x1", "bmw-ix1", "BMW iX1"),
    ("kba-fz10", "bmw", r"x2", "bmw-ix2", "BMW iX2"),
    ("kba-fz10", "bmw", r"x3", "bmw-ix3", "BMW iX3"),
    ("kba-fz10", "bmw", r"5er", "bmw-i5", "BMW i5"),
    ("kba-fz10", "bmw", r"7er", "bmw-i7", "BMW i7"),
    ("kba-fz10", "mercedes", r"glb", "mercedes-eqb", "Mercedes EQB / GLB"),
    ("kba-fz10", "mercedes", r"claklasse", "mercedes-cla", "Mercedes CLA (EV)"),
    ("kba-fz10", "mercedes", r"eklasse", "mercedes-eqe", "Mercedes EQE"),
    ("kba-fz10", "mercedes", r"sklasse", "mercedes-eqs", "Mercedes EQS"),
    ("kba-fz10", "mercedes", r"vklasse", "mercedes-eqv", "Mercedes EQV"),
    ("kba-fz10", "mercedes", r"glkglc", "mercedes-glc", "Mercedes GLC (EV)"),
    ("kba-fz10", "seat", r"tavascan", "cupra-tavascan", "Cupra Tavascan"),
    ("kba-fz10", "seat", r"raval", "cupra-raval", "Cupra Raval"),
    ("kba-fz10", "citroen", r"c3", "citroen-ec3", "Citroen e-C3"),
    ("kba-fz10", "audi", r"a6", "audi-a6-e-tron", "Audi A6 e-tron"),
    ("kba-fz10", "audi", r"q6", "audi-q6-e-tron", "Audi Q6 e-tron"),
    ("kba-fz10", "toyota", r"bz4", "toyota-bz4x", "Toyota bZ4X"),
    ("kba-fz10", "renault", r"r5", "renault-5", "Renault 5 E-Tech"),
    ("kba-fz10", "renault", r"r4", "renault-4", "Renault 4 E-Tech"),
    ("kba-fz10", "opel", r"grandlandx?", "opel-grandland", "Opel Grandland Electric"),
    ("kba-fz10", "opel", r"mokka", "opel-mokka", "Opel/Vauxhall Mokka Electric"),
    ("kba-fz10", "mini", r"mini", "mini-unsplit", "MINI (KBA series, not split)"),
    ("kba-fz10", "volkswagen", r"up", "volkswagen-e-up", "VW e-up!"),
    ("*", "audi", r"(rs)?etrongt.*", "audi-e-tron-gt", "Audi e-tron GT"),
    ("*", "audi", r"s?q6.*", "audi-q6-e-tron", "Audi Q6 e-tron"),
    ("*", "audi", r"s?a6.*", "audi-a6-e-tron", "Audi A6 e-tron"),
    ("*", "audi", r"s?q8.*", "audi-e-tron", "Audi e-tron / Q8 e-tron"),
    ("*", "citroen", r"ec3aircross.*", "citroen-ec3-aircross", "Citroen e-C3 Aircross"),
    ("*", "citroen", r"ec3.*", "citroen-ec3", "Citroen e-C3"),
    ("*", "byd", r"dolphinsurf.*", "byd-dolphin-surf", "BYD Dolphin Surf"),
    ("*", "byd", r"sealu.*", "byd-seal-u", "BYD Seal U"),
    ("*", "byd", r"sealion7.*", "byd-sealion-7", "BYD Sealion 7"),
    ("*", "volkswagen", r"e?up.*", "volkswagen-e-up", "VW e-up!"),
    ("*", "skoda", r"citigo.*", "skoda-citigo-e", "Skoda Citigo-e iV"),
    ("*", "seat", r"mii.*", "seat-mii-electric", "Seat Mii electric"),
    ("*", "opel", r"(e)?mokka.*", "opel-mokka", "Opel/Vauxhall Mokka Electric"),
    ("*", "opel", r"amperae.*", "opel-ampera-e", "Opel Ampera-e"),
    ("*", "opel", r"grandland.*", "opel-grandland", "Opel Grandland Electric"),
    ("*", "peugeot", r"e?3008.*", "peugeot-e-3008", "Peugeot e-3008"),
    ("*", "peugeot", r"e?5008.*", "peugeot-e-5008", "Peugeot e-5008"),
    ("*", "peugeot", r"e?308.*", "peugeot-e-308", "Peugeot e-308"),
    ("*", "mercedes", r"eqb.*", "mercedes-eqb", "Mercedes EQB / GLB"),
    ("*", "mercedes", r"evito.*", "mercedes-evito", "Mercedes eVito Tourer"),
    ("*", "mercedes", r"cla.*", "mercedes-cla", "Mercedes CLA (EV)"),
    ("*", "mini", r"countryman.*", "mini-countryman-e", "MINI Countryman E"),
    ("*", "mini", r"aceman.*", "mini-aceman", "MINI Aceman"),
    ("*", "renault", r"(renault)?5.*", "renault-5", "Renault 5 E-Tech"),
    ("*", "renault", r"(renault)?4.*", "renault-4", "Renault 4 E-Tech"),
    ("*", "renault", r"scenic.*", "renault-scenic-e-tech", "Renault Scenic E-Tech"),
    ("*", "renault", r"twingo.*", "renault-twingo-electric", "Renault Twingo Electric"),
    ("*", "volvo", r"ex40.*", "volvo-xc40-recharge", "Volvo XC40 / EX40"),
    ("*", "volvo", r"(c40|ec40).*", "volvo-c40", "Volvo C40 / EC40"),
    ("*", "smart", r"(hashtag)?1.*", "smart-1", "smart #1"),
    ("*", "jaguar", r"ipace.*", "jaguar-i-pace", "Jaguar I-Pace"),
]

# Display names for proposed ids the generic rule produces.
PROPOSED_NAMES: dict[str, str] = {
    "volkswagen-id7": "VW ID.7",
    "volkswagen-id5": "VW ID.5",
    "volkswagen-idbuzz": "VW ID. Buzz",
    "skoda-elroq": "Skoda Elroq",
    "bmw-ix1": "BMW iX1",
    "bmw-ix2": "BMW iX2",
    "bmw-ix3": "BMW iX3",
    "bmw-ix": "BMW iX",
    "bmw-i5": "BMW i5",
    "bmw-i7": "BMW i7",
    "kia-ev3": "Kia EV3",
    "kia-ev9": "Kia EV9",
    "volvo-ex30": "Volvo EX30",
    "volvo-ex90": "Volvo EX90",
    "ford-explorer": "Ford Explorer EV",
    "ford-puma": "Ford Puma Gen-E",
    "ford-capri": "Ford Capri EV",
    "tesla-modelx": "Tesla Model X",
    "toyota-bz4x": "Toyota bZ4X",
    "nissan-ariya": "Nissan Ariya",
    "mazda-mx30": "Mazda MX-30",
    "jeep-avenger": "Jeep Avenger EV",
    "porsche-taycan": "Porsche Taycan",
    "porsche-macan": "Porsche Macan Electric",
    "mercedes-eqe": "Mercedes EQE",
    "mercedes-eqs": "Mercedes EQS",
    "mercedes-eqv": "Mercedes EQV",
    "mg-5": "MG5 Electric",
    "mg-s5": "MG S5 EV",
    "byd-seal": "BYD Seal",
    "byd-dolphin": "BYD Dolphin",
    "hyundai-inster": "Hyundai Inster",
    "hyundai-ioniq9": "Hyundai Ioniq 9",
    "cupra-tavascan": "Cupra Tavascan",
    "polestar-4": "Polestar 4",
    "opel-frontera": "Opel/Vauxhall Frontera Electric",
    "xpeng-g6": "Xpeng G6",
    "xpeng-g9": "Xpeng G9",
    "leapmotor-t03": "Leapmotor T03",
    "leapmotor-c10": "Leapmotor C10",
    "omoda-e5": "Omoda E5",
    "jaecoo-5": "Jaecoo 5 EV",
    "honda-eny1": "Honda e:Ny1",
    "aiways-u5": "Aiways U5",
    "zeekr-001": "Zeekr 001",
    "citroen-jumpy": "Citroen e-Jumpy / e-SpaceTourer",
    "opel-vivaro": "Opel Vivaro-e Life",
}

_JOIN_ALWAYS = {"id", "e", "model"}
_ALPHA = re.compile(r"^[a-z]+$")


@dataclass
class Placement:
    model_id: str
    name: str
    in_seed: bool


def canon_make(seed: Seed, make: str, source_id: str) -> str:
    made = seed.make_id_for(make, source_id, scoped=True)
    if made is not None:
        return made
    k = key(make)
    return MAKE_CANON.get(k, k)


def _model_tokens(make_id: str, make: str, model: str) -> list[str]:
    toks = tokens(model)
    for strip in (tokens(make), [make_id], tokens(make_id.replace("-", " "))):
        if strip and toks[: len(strip)] == strip and len(toks) > len(strip):
            toks = toks[len(strip) :]
            break
    if toks and toks[0].startswith(make_id) and len(toks[0]) > len(make_id):
        toks = [toks[0][len(make_id) :], *toks[1:]]  # "MG5" -> "5", "POLESTAR4" -> "4"
    return toks


def _generic_model_key(toks: list[str]) -> str:
    """First token; joined with the next when the first is a prefix word ("ID 7", "MODEL X",
    "E C3") or a short letter code before a single digit or number ("MX 30", "IONIQ 9")."""
    if not toks:
        return ""
    first = toks[0]
    if len(toks) > 1:
        nxt = toks[1]
        if first in _JOIN_ALWAYS:
            return first + nxt
        if _ALPHA.match(first) and nxt.isdigit() and (len(first) <= 2 or len(nxt) == 1):
            return first + nxt
    return first


def propose(seed: Seed, rec: SourceRecord) -> Placement:
    sid = rec.source.id.root
    view = match_view(rec)
    make_id = canon_make(seed, rec.make, sid)
    toks = _model_tokens(make_id, rec.make, view.model)
    mkey = "".join(toks)
    for rule_sid, rule_make, pattern, pid, name in PROPOSED_RULES:
        if rule_sid in ("*", sid) and rule_make == make_id and re.fullmatch(pattern, mkey):
            return Placement(pid, name, pid in seed.models)
    pid = f"{make_id}-{_generic_model_key(toks) or 'unknown'}"
    if pid in seed.models:
        return Placement(pid, _seed_name(seed, pid), True)
    return Placement(pid, PROPOSED_NAMES.get(pid, f"{rec.make.title()} {view.model}"), False)


def _seed_name(seed: Seed, model_id: str) -> str:
    m = seed.models[model_id]
    return f"{seed.makes[m.make_id].name} {m.name}"


def place(seed: Seed, rec: SourceRecord) -> Placement:
    """Seed model via the release matcher's model lookup, else a proposed id."""
    sid = rec.source.id.root
    view = match_view(rec)
    make_id = seed.make_id_for(rec.make, sid, scoped=True)
    if make_id is None:
        model, _ = find_by_source_alias(seed, view, True)
    else:
        model, _, _ = find_model_noted(seed, make_id, view, True)
    if model is not None:
        return Placement(model.id, _seed_name(seed, model.id), True)
    return propose(seed, rec)


# --- ranking ------------------------------------------------------------------------------


def _count(rec: SourceRecord) -> int:
    sv = rec.specs.get(FactField.registered_count)
    return int(sv.value) if sv is not None and isinstance(sv.value, int | float) else 0


def _bucket_of(rec: SourceRecord) -> tuple[str, str, str, str] | None:
    """(country, source, period label, kind) for a count record, or None when out of scope."""
    sid = rec.source.id.root
    if sid not in COUNT_SOURCES or rec.country is None:
        return None
    kind = COUNT_KIND.get(sid, "new_registrations")
    if sid == "rdw":
        if rec.year is None or not USED_FIRST_YEAR <= rec.year <= USED_LAST_YEAR:
            return None
        period = (
            f"first admission {USED_FIRST_YEAR}-{USED_LAST_YEAR}, "
            f"fleet on {rec.retrieved_at.isoformat()}"
        )
    else:
        period = count_period(rec)
    return rec.country.value, sid, period, kind


@dataclass
class _Model:
    placement: Placement
    counts: Counter[tuple[str, str, str, str]] = field(default_factory=Counter)
    names: dict[str, Counter[str]] = field(default_factory=lambda: defaultdict(Counter))


def rank(records: Iterable[SourceRecord], seed: Seed, top_n: int = TOP_N) -> dict[str, Any]:
    models: dict[str, _Model] = {}
    totals: Counter[tuple[str, str, str, str]] = Counter()
    retrieved: dict[str, str] = {}
    for rec in records:
        if rec.kind != "registration_count":
            continue
        b = _bucket_of(rec)
        n = _count(rec)
        if b is None or n <= 0:
            continue
        totals[b] += n
        sid = b[1]
        retrieved[sid] = max(retrieved.get(sid, ""), rec.retrieved_at.isoformat())
        p = place(seed, rec)
        m = models.setdefault(p.model_id, _Model(p))
        m.counts[b] += n
        raw = f"{rec.make}|{match_view(rec).model}"
        m.names[sid][raw] += n

    rank_buckets = [b for b in totals if RANK_SOURCES.get(b[1]) == b[0]]
    scored = []
    for m in models.values():
        shares = {b[0]: m.counts[b] / totals[b] for b in rank_buckets if totals[b]}
        score = sum(shares.values()) / len(rank_buckets) if rank_buckets else 0.0
        scored.append((score, shares, m))
    scored.sort(key=lambda t: (-t[0], t[2].placement.model_id))

    picks = []
    for i, (score, shares, m) in enumerate(scored[:top_n], 1):
        counts: dict[str, list[dict[str, Any]]] = {}
        for b, n in sorted(m.counts.items()):
            country, sid, period, kind = b
            counts.setdefault(country, []).append(
                {
                    "source": sid,
                    "period": period,
                    "kind": kind,
                    "count": n,
                    "share_pct": round(100 * n / totals[b], 3),
                    "used_in_rank": b in rank_buckets,
                }
            )
        picks.append(
            {
                "rank": i,
                "model_id": m.placement.model_id,
                "name": m.placement.name,
                "in_seed": m.placement.in_seed,
                "score_pct": round(100 * score, 3),
                "rank_share_pct": {c: round(100 * s, 3) for c, s in sorted(shares.items())},
                "counts": {c: counts[c] for c in COUNTRIES if c in counts},
                "source_names": {
                    sid: [f"{n} {nm}" for nm, n in names.most_common(4)]
                    for sid, names in sorted(m.names.items())
                },
            }
        )
    next_up = [
        {"rank": i, "model_id": m.placement.model_id, "name": m.placement.name,
         "in_seed": m.placement.in_seed, "score_pct": round(100 * s, 3)}
        for i, (s, _, m) in enumerate(scored[top_n : top_n + 10], top_n + 1)
    ]  # fmt: skip
    seed_outside = sorted(
        (
            {"model_id": m.placement.model_id, "rank": i, "score_pct": round(100 * s, 3)}
            for i, (s, _, m) in enumerate(scored, 1)
            if m.placement.in_seed and i > top_n
        ),
        key=lambda d: d["rank"],
    )
    return {
        "totals": [
            {
                "country": c,
                "source": s,
                "period": p,
                "kind": k,
                "cars": n,
                "used_in_rank": (c, s, p, k) in rank_buckets,
            }
            for (c, s, p, k), n in sorted(totals.items())
        ],  # fmt: skip
        "retrieved_at": retrieved,
        "models": picks,
        "next_10": next_up,
        "seed_models_outside_top": seed_outside,
    }


METHOD = {
    "used_window": {
        "view_year": VIEW_YEAR,
        "fleet_age_years": [USED_MIN_AGE, USED_MAX_AGE],
        "first_admission_years": [USED_FIRST_YEAR, USED_LAST_YEAR],
        "note": "Both ends inclusive. Applied to RDW (NL), the only staged source with the "
        "year of first admission. DfT VEH0120 (UK) has no year: its count is the whole "
        "licensed BEV fleet at quarter end, cars under 2 years included.",
    },
    "score": "Mean over ranking countries of the model's share (%) of that country's staged "
    "BEV total in the same source and period. Ranking countries: NL (rdw, first admission "
    f"{USED_FIRST_YEAR}-{USED_LAST_YEAR}) and UK (dft-veh, licensed fleet, all ages). "
    "Counts of different sources, periods or kinds are never added.",
    "context_only": "DE (kba-fz10 2025 and 2026 YTD; eea 2025), FR and BE (eea 2025) and the "
    "EEA NL row are NEW registrations, not a used fleet, so they are listed but never "
    "scored. A DE/FR/BE used proxy needs KBA FZ10 and EEA files for 2018-2024 (QUESTIONS Q-074).",
    "grouping": "Seed models via the release matcher's model lookup (scoped aliases on), at "
    "model level. Other records: proposed id <make>-<model key> from PROPOSED_RULES or the "
    "generic first-token rule in pipeline/ev_pipeline/qa/top40.py; in_seed false.",
    "known_limits": [
        "KBA series 'MINI' is not split into Cooper E / Aceman / Countryman: it is listed "
        "as mini-unsplit and not given to mini-cooper-se.",
        "KBA series names (X1, 5ER, GLB, ...) are read from the BEV column and mapped by "
        "PROPOSED_RULES (reviewed by hand, not by a source).",
        "Mixed-generation names stay at model level (BMW iX3 holds the old G08 and the "
        "2025+ iX3 in DfT and KBA; RDW 2018-2024 is G08 only).",
    ],
}


def build_doc(staging: Path, seed_path: Path, top_n: int = TOP_N) -> dict[str, Any]:
    seed = load_seed(seed_path)
    records = list(_read_staging(staging, COUNT_SOURCES))
    ranked = rank(records, seed, top_n)
    return {
        "schema": "top40/v1",
        "generated_by": "pipeline/ev_pipeline/qa/top40.py build",
        "generated_on": date.today().isoformat(),
        "inputs": {
            "staging": [f"data/staging/{s}.records.jsonl" for s in COUNT_SOURCES],
            "seed": "data/seed/models.yaml",
            "retrieved_at": ranked["retrieved_at"],
        },
        "method": METHOD,
        "totals": ranked["totals"],
        "summary": {
            "models": len(ranked["models"]),
            "in_seed": sum(1 for m in ranked["models"] if m["in_seed"]),
            "not_in_seed": sum(1 for m in ranked["models"] if not m["in_seed"]),
        },
        "models": ranked["models"],
        "next_10": ranked["next_10"],
        "seed_models_outside_top": ranked["seed_models_outside_top"],
    }


def _read_staging(staging: Path, sources: Iterable[str]) -> Iterable[SourceRecord]:
    for sid in sources:
        path = staging / f"{sid}.records.jsonl"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield SourceRecord.model_validate_json(line)


HEADER = """\
# Top-40 used EV models for NL, DE, FR, BE, UK (ADDENDUM-6 P5).
# GENERATED by `uv run python -m ev_pipeline.qa.top40 build` (pipeline/) from the staged
# registration counts; do not edit by hand. Method and limits under `method:`.
# Counts are cars per source and period; they are never added across sources or kinds.
"""


def write_yaml(doc: dict[str, Any], path: Path) -> None:
    path.write_text(
        HEADER + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


# --- coverage -----------------------------------------------------------------------------

LEVELS = ("two_plus", "one", "estimate", "none")
SPEC_FIELDS = {
    "battery_kwh_net": "Battery usable (kWh)",
    "wltp_range_km": "WLTP range",
    "ac_kw": "AC kW",
    "dc_peak_kw": "DC peak kW",
    "dc_avg_10_80_kw": "DC average 10-80 % / curve",
    "real_range_km": "Real range",
}
# Which source could fill a gap per field (pointers, not values; status per data/sources.yaml).
FILLERS: dict[str, str] = {
    "battery_kwh_net": "openev (2023+), kilowatt-openev; owner tests (permission pending)",
    "wltp_range_km": "openev, ademe (FR line-up), rdw fuel table (adapter live, Q-068), "
    "eea per type (adapter extension)",
    "ac_kw": "openev, kilowatt-openev",
    "dc_peak_kw": "openev, kilowatt-openev; fastned (waiting)",
    "dc_avg_10_80_kw": "openev 10-80 % time; kilowatt-openev curves (estimated); "
    "fastned / owner tests (permission pending)",
    "real_range_km": "real-world tests (permission pending); model-estimate only",
    "price_new.NL": "rdw catalogusprijs (imported)",
    "price_new.DE": "openev (2023+); maker-docs (blocked, Q-008)",
    "price_new.FR": "ademe (current line-up)",
    "price_new.BE": "none open (R-02); maker-docs (blocked)",
    "price_new.UK": "openev GBP list prices (2023+); maker-docs (blocked)",
    "price_used": "none in data/sources.yaml (partner feeds / indices, Decision 004)",
    "registrations.DE": "kba-fz10 + eea (new registrations only; no open DE fleet by model)",
    "registrations.FR": "eea (new registrations only; no open FR fleet by model)",
    "registrations.BE": "eea (new registrations only; be-mobilit blocked)",
    "registrations.NL": "rdw fleet + eea new",
    "registrations.UK": "dft-veh fleet only (no UK row in EEA after Brexit)",
    "generation_years": "rdw first-admission years per type approval (adapter extension); "
    "eea back years; wikidata (sparse: few car items carry dates)",
}


def row_level(row: dict[str, Any], f: str) -> str:
    """Level of one value: 2+ agreeing outside sources / 1 / estimate / none."""
    if f.startswith("price_new."):
        c = f.split(".", 1)[1]
        value = (row.get("price_new") or {}).get(c)
    else:
        value = row.get(f)
    p = (row.get("provenance") or {}).get(f)
    if value is None or p is None:
        return "none"
    if p.get("estimate"):
        return "estimate"
    outside = [s for s in p.get("source_ids") or [] if s not in ("model-estimate", "seed-manual")]
    if not outside:
        return "estimate"  # seed-manual only: hand-entered, unchecked
    return "two_plus" if (p.get("agreeing_sources") or 1) >= 2 else "one"


def model_level(levels: list[str]) -> str:
    """A model reaches the best level that a majority of its variants reach (none if no rows)."""
    if not levels:
        return "none"
    for i, lvl in enumerate(LEVELS[:-1]):
        good = sum(1 for x in levels if LEVELS.index(x) <= i)
        if good * 2 > len(levels):
            return lvl
    return "none"


_WD_KEY = re.compile(r"^wikidata:(?P<model>[^/]+)/(?P<qid>Q\d+)#(?P<b>production_(start|end)):")


def generation_years_check(
    model_id: str, generations: list[dict[str, Any]], wikidata: Iterable[SourceRecord]
) -> dict[str, Any]:
    """Wikidata production years vs the seed generation boundaries of one model.

    A start year agrees when it is within YEAR_TOLERANCE of some generation's start; an end
    year likewise with some generation's end. Level: two_plus = every Wikidata year agrees
    (the seed is hand-entered, Wikidata is the outside source), one = some disagree
    (review), none = no Wikidata year or no seed generation (model not in the seed)."""
    gens = [g for g in generations if g.get("model_id") == model_id]
    starts = {g["year_start"] for g in gens if g.get("year_start") is not None}
    ends = {g["year_end"] for g in gens if g.get("year_end") is not None}
    checks = []
    for r in wikidata:
        m = _WD_KEY.match(r.record_key)
        if m is None or m["model"] != model_id or r.year is None:
            continue
        pool = starts if m["b"] == "production_start" else ends
        ok = any(abs(r.year - y) <= YEAR_TOLERANCE for y in pool) if gens else None
        checks.append({"item": m["qid"], "label": r.variant_name, "boundary": m["b"],
                       "year": r.year, "agrees": ok})  # fmt: skip
    if not checks or not gens:  # no Wikidata year, or no seed generations to compare with
        return {"level": "none", "checks": checks}
    level = "two_plus" if all(c["agrees"] for c in checks) else "one"
    return {"level": level, "checks": checks}


YEAR_TOLERANCE = 1


def coverage(
    top: dict[str, Any],
    catalogue: dict[str, Any],
    wikidata: Iterable[SourceRecord] = (),
) -> dict[str, Any]:
    wikidata = list(wikidata)
    rows_by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in catalogue.get("rows", []):
        rows_by_model[r["model_id"]].append(r)
    fields = list(SPEC_FIELDS) + [f"price_new.{c}" for c in COUNTRIES]
    per_model = []
    tally: dict[str, Counter[str]] = {f: Counter() for f in fields}
    tally["price_used"] = Counter()
    for c in COUNTRIES:
        tally[f"registrations.{c}"] = Counter()
    tally["generation_years"] = Counter()
    year_review: list[dict[str, Any]] = []
    for m in top.get("models", []):
        rows = rows_by_model.get(m["model_id"], [])
        lv: dict[str, str] = {}
        for f in fields:
            lv[f] = model_level([row_level(r, f) for r in rows])
            tally[f][lv[f]] += 1
        lv["price_used"] = "none"  # no used-price field or source exists yet
        tally["price_used"]["none"] += 1
        for c in COUNTRIES:
            srcs = {e["source"] for e in m.get("counts", {}).get(c, []) if e["count"] > 0}
            lvl = "two_plus" if len(srcs) >= 2 else "one" if srcs else "none"
            lv[f"registrations.{c}"] = lvl
            tally[f"registrations.{c}"][lvl] += 1
        gy = generation_years_check(m["model_id"], catalogue.get("generations", []), wikidata)
        lv["generation_years"] = gy["level"]
        tally["generation_years"][gy["level"]] += 1
        year_review += [
            {"model_id": m["model_id"], **c} for c in gy["checks"] if c["agrees"] is False
        ]
        per_model.append(
            {
                "rank": m["rank"],
                "model_id": m["model_id"],
                "in_seed": m["in_seed"],
                "variants_in_release": len(rows),
                "levels": lv,
            }
        )
    n = len(top.get("models", [])) or 1
    by_field = {
        f: {
            **{lvl: t[lvl] for lvl in LEVELS},
            "share_two_plus": round(t["two_plus"] / n, 3),
            "meets_target": t["two_plus"] / n >= COVERAGE_TARGET,
            "could_fill": FILLERS.get(f, ""),
        }
        for f, t in tally.items()
    }
    return {
        "release": catalogue.get("release"),
        "models": len(top.get("models", [])),
        "target_share_two_plus": COVERAGE_TARGET,
        "rule": "a model takes the best level a majority of its release variants reach "
        "(2+ agreeing outside sources > 1 source > estimate or seed-manual only > none); "
        "a model not in the release is none. Registrations: number of sources with a "
        "count per country (periods differ, so 'sources present', not 'agreeing').",
        "generation_years_disagreeing": year_review,
        "fields_meeting_target": sorted(f for f, v in by_field.items() if v["meets_target"]),
        "by_field": by_field,
        "per_model": per_model,
    }


FIELD_LABELS = {
    **SPEC_FIELDS,
    **{f"price_new.{c}": f"New price {c}" for c in COUNTRIES},
    "price_used": "Used price (any country)",
    **{f"registrations.{c}": f"Registrations {c}" for c in COUNTRIES},
    "generation_years": "Generation years vs Wikidata",
}


def coverage_md(cov: dict[str, Any]) -> str:
    lines = [
        "| Field | 2+ sources | 1 source | Estimate / seed-only | None | Share 2+ (target "
        f"{100 * cov['target_share_two_plus']:.0f} %) | Could fill the gap |",
        "|---|---|---|---|---|---|---|",
    ]
    for f, v in cov["by_field"].items():
        lines.append(
            f"| {FIELD_LABELS.get(f, f)} | {v['two_plus']} | {v['one']} | {v['estimate']} | "
            f"{v['none']} | {100 * v['share_two_plus']:.0f} % | {v['could_fill']} |"
        )
    return "\n".join(lines) + "\n"


def top40_section(catalogue: dict[str, Any], data_dir: Path) -> dict[str, Any]:
    """The qa.json `top40` section: coverage of the models in data/seed/top40.yaml."""
    path = data_dir / "seed" / "top40.yaml"
    if not path.exists():
        return {"status": "skipped", "note": "data/seed/top40.yaml not found"}
    top = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    wd = _read_staging(data_dir / "staging", ["wikidata"])
    return {"status": "info", "list": "data/seed/top40.yaml", **coverage(top, catalogue, wd)}


# --- command line -------------------------------------------------------------------------


def _latest_catalogue(data_dir: Path) -> dict[str, Any]:
    from ev_pipeline.release.publish import local_catalogue

    latest = (data_dir / "releases" / "latest").read_text(encoding="utf-8").strip()
    path = local_catalogue(data_dir, int(latest))  # T-064: fetched by manifest if needed
    if path is None:
        raise FileNotFoundError(f"release {latest} has no catalogue.json or manifest.json")
    return json.loads(path.read_text("utf-8"))


def main(argv: list[str] | None = None) -> int:
    from ev_pipeline.sources._common import data_dir

    ap = argparse.ArgumentParser(prog="python -m ev_pipeline.qa.top40")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="rank the staged counts -> data/seed/top40.yaml")
    p_cov = sub.add_parser("coverage", help="coverage of the top 40 in the latest release")
    p_cov.add_argument("--md", action="store_true", help="Markdown table instead of JSON")
    args = ap.parse_args(argv)
    d = data_dir()
    if args.cmd == "build":
        doc = build_doc(d / "staging", d / "seed" / "models.yaml")
        write_yaml(doc, d / "seed" / "top40.yaml")
        s = doc["summary"]
        print(f"top40: {s['models']} models, {s['in_seed']} in seed, {s['not_in_seed']} not")
        return 0
    top = yaml.safe_load((d / "seed" / "top40.yaml").read_text(encoding="utf-8"))
    cov = coverage(top, _latest_catalogue(d), _read_staging(d / "staging", ["wikidata"]))
    print(coverage_md(cov) if args.md else json.dumps(cov, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
