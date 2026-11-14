#!/usr/bin/env python3
"""Validate data/seed/models.yaml (schema seed-models/v1).

Usage:
    python3 -I data/seed/validate_seed.py data/seed/models.yaml
    python3 -I data/seed/validate_seed.py --self-test

Stdlib + PyYAML only. Exit code 0 = valid, 1 = errors found.
"""

from __future__ import annotations

import copy
import itertools
import re
import sys
from typing import Any

import yaml

SCHEMA = "seed-models/v1"
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEGMENTS = {"A", "B", "C", "D", "E", "F", "J-small", "J-medium", "J-large"}
BODIES = {"hatchback", "sedan", "estate", "suv", "crossover", "coupe", "mpv"}
MIN_YEAR, MAX_YEAR = 2007, 2027
MAX_OVERLAP_YEARS = 1

# Every model from the overnight brief must be present (by model id).
REQUIRED_MODEL_IDS = [
    "tesla-model-3",
    "tesla-model-y",
    "tesla-model-s",
    "renault-zoe",
    "renault-megane-e-tech",
    "nissan-leaf",
    "volkswagen-e-golf",
    "volkswagen-id3",
    "volkswagen-id4",
    "hyundai-ioniq-electric",
    "hyundai-kona-electric",
    "hyundai-ioniq-5",
    "hyundai-ioniq-6",
    "kia-soul-ev",
    "kia-niro-ev",
    "kia-ev6",
    "bmw-i3",
    "bmw-i4",
    "peugeot-e-208",
    "peugeot-e-2008",
    "opel-corsa-e",
    "fiat-500e",
    "skoda-enyaq",
    "mg-mg4",
    "mg-zs-ev",
    "polestar-2",
    "audi-e-tron",
    "audi-q4-e-tron",
    "mercedes-eqa",
    "mercedes-eqc",
    "jaguar-i-pace",
    "dacia-spring",
    "smart-eq-fortwo",
    "honda-e",
    "mini-cooper-se",
    "cupra-born",
    "byd-atto-3",
    "volvo-xc40-recharge",
    "ford-mustang-mach-e",
    "citroen-e-c4",
]

# Generations the brief explicitly asks for (by id).
REQUIRED_GENERATION_IDS = [
    "nissan-leaf-ze0",
    "nissan-leaf-ze1",
    "tesla-model-3-highland",
    "tesla-model-y-juniper",
]


def _is_year(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and MIN_YEAR <= v <= MAX_YEAR


def validate(doc: Any) -> list[str]:
    errors: list[str] = []
    err = errors.append
    if not isinstance(doc, dict):
        return ["document root must be a mapping"]
    if doc.get("schema") != SCHEMA:
        err(f"schema must be {SCHEMA!r}, got {doc.get('schema')!r}")
    makes = doc.get("makes")
    if not isinstance(makes, list) or not makes:
        return errors + ["makes must be a non-empty list"]

    seen: dict[str, str] = {}

    def check_id(value: Any, where: str, prefix: str | None = None) -> None:
        if not isinstance(value, str) or not ID_RE.match(value):
            err(f"{where}: id {value!r} must be lowercase a-z0-9 with single hyphens")
            return
        if value in seen:
            err(f"{where}: duplicate id {value!r} (first used at {seen[value]})")
        else:
            seen[value] = where
        if prefix and not value.startswith(prefix + "-"):
            err(f"{where}: id {value!r} should start with {prefix + '-'!r}")

    model_ids: set[str] = set()
    for mi, make in enumerate(makes):
        mw = f"makes[{mi}]"
        if not isinstance(make, dict):
            err(f"{mw}: must be a mapping")
            continue
        check_id(make.get("id"), mw)
        mw = f"make {make.get('id')}"
        if not isinstance(make.get("name"), str) or not make["name"].strip():
            err(f"{mw}: name required")
        models = make.get("models")
        if not isinstance(models, list) or not models:
            err(f"{mw}: models must be a non-empty list")
            continue
        for model in models:
            if not isinstance(model, dict):
                err(f"{mw}: model entries must be mappings")
                continue
            check_id(model.get("id"), f"{mw} model", make.get("id"))
            w = f"model {model.get('id')}"
            model_ids.add(str(model.get("id")))
            if not isinstance(model.get("name"), str) or not model["name"].strip():
                err(f"{w}: name required")
            if model.get("segment") not in SEGMENTS:
                err(f"{w}: segment {model.get('segment')!r} not in {sorted(SEGMENTS)}")
            if model.get("body") not in BODIES:
                err(f"{w}: body {model.get('body')!r} not in {sorted(BODIES)}")
            aliases = model.get("name_aliases", [])
            if not isinstance(aliases, list) or not all(
                isinstance(a, str) and a.strip() for a in aliases
            ):
                err(f"{w}: name_aliases must be a list of non-empty strings")
            elif len({a.casefold() for a in aliases}) != len(aliases):
                err(f"{w}: name_aliases contains duplicates")
            gens = model.get("generations")
            if not isinstance(gens, list) or not gens:
                err(f"{w}: generations must be a non-empty list")
                continue
            spans: list[tuple[int, float, str]] = []
            for gen in gens:
                if not isinstance(gen, dict):
                    err(f"{w}: generation entries must be mappings")
                    continue
                check_id(gen.get("id"), f"{w} generation", model.get("id"))
                gw = f"generation {gen.get('id')}"
                if not isinstance(gen.get("name"), str) or not gen["name"].strip():
                    err(f"{gw}: name required")
                unc = gen.get("uncertain")
                if not isinstance(unc, bool):
                    err(f"{gw}: uncertain must be true or false")
                notes = gen.get("notes")
                if notes is not None and (
                    not isinstance(notes, str) or not notes.strip()
                ):
                    err(f"{gw}: notes must be a non-empty string when present")
                if unc is True and not notes:
                    err(f"{gw}: uncertain: true needs notes saying what is uncertain")
                years = gen.get("years")
                if not (isinstance(years, list) and len(years) == 2):
                    err(f"{gw}: years must be [start, end]")
                    continue
                start, end = years
                if not _is_year(start):
                    err(f"{gw}: start year {start!r} invalid")
                    continue
                if end is not None and not _is_year(end):
                    err(f"{gw}: end year {end!r} invalid (use null for still on sale)")
                    continue
                if end is not None and end < start:
                    err(f"{gw}: years out of order {years}")
                    continue
                end_f = float("inf") if end is None else end
                spans.append((start, end_f, str(gen.get("id"))))
                markers = gen.get("change_markers", [])
                if not isinstance(markers, list):
                    err(f"{gw}: change_markers must be a list")
                    continue
                last = 0
                for cm in markers:
                    if not (
                        isinstance(cm, dict)
                        and _is_year(cm.get("year"))
                        and isinstance(cm.get("text"), str)
                        and cm["text"].strip()
                    ):
                        err(f"{gw}: change marker {cm!r} needs year and text")
                        continue
                    if not (start <= cm["year"] <= end_f):
                        err(f"{gw}: change marker year {cm['year']} outside {years}")
                    if cm["year"] < last:
                        err(f"{gw}: change markers not in year order")
                    last = cm["year"]
            spans.sort()
            for (s1, e1, g1), (s2, e2, g2) in itertools.pairwise(spans):
                overlap = min(e1, e2) - max(s1, s2) + 1  # shared calendar years
                if overlap > MAX_OVERLAP_YEARS:
                    shown = "open-ended" if overlap == float("inf") else int(overlap)
                    err(
                        f"model {model.get('id')}: {g1} and {g2} overlap by {shown} years"
                    )

    for mid in REQUIRED_MODEL_IDS:
        if mid not in model_ids:
            err(f"required model missing: {mid}")
    for gid in REQUIRED_GENERATION_IDS:
        if gid not in seen:
            err(f"required generation missing: {gid}")
    return errors


def stats(doc: dict) -> dict[str, int]:
    makes = doc["makes"]
    models = [m for mk in makes for m in mk["models"]]
    gens = [g for m in models for g in m["generations"]]
    return {
        "makes": len(makes),
        "models": len(models),
        "generations": len(gens),
        "uncertain_generations": sum(1 for g in gens if g.get("uncertain")),
        "models_with_uncertain": sum(
            1 for m in models if any(g.get("uncertain") for g in m["generations"])
        ),
    }


def self_test() -> int:
    """Check that the validator catches each rule on small inline fixtures."""
    good = {
        "schema": SCHEMA,
        "makes": [
            {
                "id": "x",
                "name": "X",
                "models": [
                    {
                        "id": "x-a",
                        "name": "A",
                        "segment": "B",
                        "body": "hatchback",
                        "generations": [
                            {
                                "id": "x-a-1",
                                "name": "1",
                                "years": [2015, 2019],
                                "uncertain": False,
                            },
                            {
                                "id": "x-a-2",
                                "name": "2",
                                "years": [2019, None],
                                "uncertain": True,
                                "notes": "n",
                            },
                        ],
                    }
                ],
            }
        ],
    }
    global REQUIRED_MODEL_IDS, REQUIRED_GENERATION_IDS
    saved = (REQUIRED_MODEL_IDS, REQUIRED_GENERATION_IDS)
    REQUIRED_MODEL_IDS, REQUIRED_GENERATION_IDS = ["x-a"], []
    failures = 0

    def expect(name: str, doc: Any, should_pass: bool, needle: str = "") -> None:
        nonlocal failures
        errs = validate(doc)
        ok = (not errs) if should_pass else any(needle in e for e in errs)
        if not ok:
            failures += 1
            print(f"SELF-TEST FAIL {name}: {errs}")

    def mutate(fn) -> dict:
        d = copy.deepcopy(good)
        fn(d)
        return d

    def gens(d: dict) -> list:
        return d["makes"][0]["models"][0]["generations"]

    try:
        expect("good", good, True)
        expect(
            "dup id",
            mutate(lambda d: gens(d)[1].update(id="x-a-1")),
            False,
            "duplicate id",
        )
        expect(
            "bad id",
            mutate(lambda d: gens(d)[0].update(id="x-a-Gen_1")),
            False,
            "lowercase",
        )
        expect(
            "order",
            mutate(lambda d: gens(d)[0].update(years=[2019, 2015])),
            False,
            "out of order",
        )
        expect(
            "overlap",
            mutate(lambda d: gens(d)[1].update(years=[2017, None])),
            False,
            "overlap",
        )
        expect(
            "open overlap",
            mutate(lambda d: gens(d)[0].update(years=[2015, None])),
            False,
            "overlap",
        )
        expect(
            "uncertain no notes",
            mutate(lambda d: gens(d)[1].pop("notes")),
            False,
            "needs notes",
        )
        expect(
            "missing model",
            mutate(lambda d: d["makes"][0]["models"][0].update(id="x-b")),
            False,
            "required model missing",
        )
        expect(
            "bad segment",
            mutate(lambda d: d["makes"][0]["models"][0].update(segment="SUV")),
            False,
            "segment",
        )
    finally:
        REQUIRED_MODEL_IDS, REQUIRED_GENERATION_IDS = saved
    print("self-test:", "FAILED" if failures else "ok")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        return self_test()
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    errors = validate(doc)
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"{len(errors)} error(s)")
        return 1
    st = stats(doc)
    print("OK", ", ".join(f"{k}={v}" for k, v in st.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
