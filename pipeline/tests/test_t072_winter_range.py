"""T-072: winter range per variant in the release rows."""

from __future__ import annotations

import copy
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.derive.shortlist import derived_values, load_params
from ev_pipeline.derive.winter import FIELD, attach_winter_range, band_labels
from ev_pipeline.opendata.bundle import VALUE_FIELDS
from ev_pipeline.release.validate import RANGES, ROW_NUMBER_FIELDS, provenance_errors
from ev_pipeline.schema_models import PublishedVariant

FIX = Path(__file__).parent / "fixtures" / "release"
TAXONOMY = Path(__file__).parents[2] / "data" / "taxonomy"


def _cells(wh_by_band: dict[str, float]) -> list[dict[str, Any]]:
    return [
        {"road_band": road, "temperature_band_id": band, "wh_km": wh}
        for band, wh in wh_by_band.items()
        for road in ("town", "rural", "motorway")
    ]


def _row(vid: str = "car-a", net: float | None = 60.0) -> dict[str, Any]:
    return {
        "variant_id": vid,
        "battery_kwh_net": net,
        "wltp_range_km": 400.0,
        "provenance": {
            "battery_kwh_net": {
                "source_ids": ["openev"],
                "confidence": "medium",
                "fact_ids": ["f1"],
            },
            "wltp_range_km": {"source_ids": ["eea"], "confidence": "high", "fact_ids": ["f2"]},
        },
    }


MATRIX = {
    "variants": [
        {"variant_id": "car-a", "usable_kwh": 60.0, "cells": _cells({"t1": 240.0, "t5": 160.0})}
    ]
}


def test_winter_range_is_usable_kwh_over_the_winter_cell() -> None:
    rows = [_row()]
    log = attach_winter_range(rows, MATRIX)
    assert rows[0][FIELD] == 250.0  # 60 kWh x 1000 / 240 Wh/km
    assert log["filled"] == 1 and log["band"] == "t1"


def test_row_and_shortlist_use_the_same_number() -> None:
    rows = [_row()]
    attach_winter_range(rows, MATRIX)
    shortlist = derived_values(rows[0], MATRIX["variants"][0], load_params())
    assert rows[0][FIELD] == shortlist["winter_range_km"]


def test_provenance_is_a_low_confidence_estimate_from_the_inputs() -> None:
    rows = [_row()]
    attach_winter_range(rows, MATRIX, band_labels={"t1": "-5 °C and colder"})
    p = rows[0]["provenance"][FIELD]
    assert p["source_ids"] == ["openev", "eea", "model-estimate"]
    assert p["fact_ids"] == ["f1", "f2"]
    assert p["estimate"] is True and p["derived"] is True and p["confidence"] == "low"
    assert "-5 °C and colder" in p["note"] and "Q-059" in p["note"]
    assert provenance_errors(rows) == []


def test_no_matrix_entry_or_no_battery_leaves_it_empty() -> None:
    rows = [_row("car-b"), _row("car-a", net=None)]
    matrix = copy.deepcopy(MATRIX)
    matrix["variants"][0]["usable_kwh"] = None
    log = attach_winter_range(rows, matrix)
    assert all(FIELD not in r and FIELD not in r["provenance"] for r in rows)
    assert log["filled"] == 0
    assert attach_winter_range([_row()], None)["filled"] == 0


def test_rerun_is_idempotent_and_clears_a_stale_value() -> None:
    rows = [_row()]
    attach_winter_range(rows, MATRIX)
    first = copy.deepcopy(rows)
    attach_winter_range(rows, MATRIX)
    assert rows == first
    attach_winter_range(rows, {"variants": []})
    assert FIELD not in rows[0] and FIELD not in rows[0]["provenance"]


def test_field_is_wired_everywhere_it_must_be() -> None:
    assert FIELD in PublishedVariant.model_fields
    assert FIELD in ROW_NUMBER_FIELDS and FIELD in RANGES
    assert FIELD in [f for f, _, _ in VALUE_FIELDS]


def test_band_label_comes_from_the_taxonomy() -> None:
    assert band_labels(TAXONOMY)["t1"] == "-5 °C and colder"
    assert band_labels(Path("/nonexistent")) == {}


@pytest.mark.parametrize("vid", ["tesla-model-3-gen1-lr"])
def test_release_build_ships_winter_range_with_provenance(tmp_path: Path, vid: str) -> None:
    from ev_pipeline.release.build import build_release

    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    res = build_release(d, now=datetime(2026, 11, 17, 1, 0, tzinfo=UTC))
    row = next(r for r in res.catalogue["rows"] if r["variant_id"] == vid)
    assert row[FIELD] is not None
    assert 0 < row[FIELD] < row["real_range_km"]
    assert row["provenance"][FIELD]["estimate"] is True
    assert res.sections["real_range_winter_km"]["filled"] >= 1
