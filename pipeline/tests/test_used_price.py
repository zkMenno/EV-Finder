"""T-081: used price bands per variant, build year and country. Fixtures only, no network."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from ev_pipeline.derive import used_price as up

GEN = "2026-11-15T01:00:00Z"
CURVE = up.load_params()["curves"]["default"]


def fact(vid: str, cc: str, amount: float, src: str = "rdw", unit: str = "EUR") -> dict[str, Any]:
    return {
        "field": "price_new",
        "subject_type": "variant",
        "subject_id": vid,
        "value": amount,
        "country": cc,
        "unit": unit,
        "source": {"id": src},
    }


def row(vid: str = "m-gen1-a", ys: int = 2022, ye: int | None = None) -> dict[str, Any]:
    return {"variant_id": vid, "generation_id": "m-gen1", "year_start": ys, "year_end": ye}


def run(
    tmp_path: Path,
    rows: list[dict[str, Any]],
    facts: list[tuple[dict[str, Any], int | None]],
    **over: Any,
) -> up.UsedPriceResult:
    p = up.load_params()
    p.update(over)
    pf = tmp_path / "params.yaml"
    pf.write_text(yaml.safe_dump(p))
    return up.build_used_prices(
        rows, [f for f, _ in facts], [y for _, y in facts], tmp_path, 9, GEN, pf
    )


def bands(res: up.UsedPriceResult, vid: str, cc: str) -> dict[int, dict[str, Any]]:
    assert res.document
    v = next((v for v in res.document["variants"] if v["variant_id"] == vid), None)
    return {b["build_year"]: b for b in ((v or {}).get("bands", {}).get(cc) or [])}


def test_curve_anchors_and_interpolation() -> None:
    assert up.kept_share(3, CURVE) == pytest.approx(0.515)
    assert up.kept_share(3.5, CURVE) == pytest.approx((0.515 + 0.465) / 2)
    assert up.kept_share(13, CURVE) is None  # beyond max_age: no band
    assert up.kept_share(11, CURVE) == pytest.approx(0.277 * 0.277 / 0.301)


def test_age_from_mid_build_year() -> None:
    assert up.age_at(2023, date(2026, 7, 1), 7) == pytest.approx(3.0, abs=0.01)
    assert up.age_at(2026, date(2026, 3, 1), 7) == 0.0


def test_model_band_uses_that_years_list_price(tmp_path: Path) -> None:
    res = run(
        tmp_path,
        [row(ys=2022, ye=2023)],
        [(fact("m-gen1-a", "NL", 50000), 2022), (fact("m-gen1-a", "NL", 40000), 2023)],
    )
    b = bands(res, "m-gen1-a", "NL")
    age = up.age_at(2022, date(2026, 11, 15), 7)
    med = 50000 * up.kept_share(age, CURVE)  # type: ignore[operator]
    assert b[2022]["median"] == round(med / 100) * 100
    assert b[2022]["p25"] == round(med * 0.88 / 100) * 100
    assert b[2022]["samples"] == 0 and b[2022]["estimate"] is True and b[2022]["method"] == "model"
    assert b[2022]["list_basis"] == "year" and b[2023]["list_price"] == 40000
    assert b[2022]["currency"] == "EUR"


def test_nearest_year_within_gap_and_low_confidence(tmp_path: Path) -> None:
    res = run(tmp_path, [row(ys=2020, ye=2024)], [(fact("m-gen1-a", "NL", 40000), 2022)])
    b = bands(res, "m-gen1-a", "NL")
    assert b[2020]["list_basis"] == "nearest_year" and b[2020]["confidence"] == "low"
    assert b[2024]["list_basis"] == "nearest_year"
    res2 = run(tmp_path, [row(ys=2019, ye=2019)], [(fact("m-gen1-a", "NL", 40000), 2022)])
    assert bands(res2, "m-gen1-a", "NL") == {}  # 3 years away: no list price, no guess


def test_cross_country_vat_adjusted_not_for_uk(tmp_path: Path) -> None:
    res = run(tmp_path, [row(ys=2024, ye=2024)], [(fact("m-gen1-a", "NL", 48400), 2024)])
    de = bands(res, "m-gen1-a", "DE")[2024]
    assert de["list_basis"] == "from_nl_vat_adjusted"
    assert de["list_price"] == round(48400 / 1.21 * 1.19 / 100) * 100
    assert de["confidence"] == "low"
    assert bands(res, "m-gen1-a", "UK") == {}


def test_own_country_price_beats_cross_country(tmp_path: Path) -> None:
    res = run(
        tmp_path,
        [row(ys=2024, ye=2024)],
        [(fact("m-gen1-a", "NL", 48400), 2024), (fact("m-gen1-a", "DE", 45000, "openev"), 2024)],
    )
    de = bands(res, "m-gen1-a", "DE")[2024]
    assert de["list_basis"] == "year" and de["list_source_ids"] == ["openev"]


def test_uk_band_in_gbp(tmp_path: Path) -> None:
    res = run(
        tmp_path, [row(ys=2024, ye=2024)], [(fact("m-gen1-a", "UK", 40000, "x", "GBP"), 2024)]
    )
    assert bands(res, "m-gen1-a", "UK")[2024]["currency"] == "GBP"


def test_facts_without_year_or_bad_value_are_ignored(tmp_path: Path) -> None:
    res = run(
        tmp_path,
        [row(ys=2024, ye=2024)],
        [(fact("m-gen1-a", "NL", 48400), None), (fact("m-gen1-a", "NL", 0), 2024)],
    )
    assert bands(res, "m-gen1-a", "NL") == {}
    assert res.log["bands"]["NL not enough data"] == 1


def test_old_build_years_extrapolated_low_confidence(tmp_path: Path) -> None:
    res = run(tmp_path, [row(ys=2019, ye=2019)], [(fact("m-gen1-a", "NL", 40000), 2019)])
    assert bands(res, "m-gen1-a", "NL")[2019]["confidence"] == "low"


def write_samples(tmp_path: Path, doc: dict[str, Any], name: str = "nl-m-gen1.yaml") -> None:
    d = tmp_path / "manual" / "prices"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(yaml.safe_dump(doc))


SRC = {
    "name": "AutoScout24 NL (our pre-filled search)",
    "url": "https://www.autoscout24.nl/lst/m/one",
}


def test_fresh_variant_samples_replace_model_and_are_backtested(tmp_path: Path) -> None:
    write_samples(
        tmp_path,
        {
            "country": "NL",
            "variant_id": "m-gen1-a",
            "observed_at": "2026-11-01",
            "currency": "EUR",
            "source": SRC,
            "rows": [{"build_year": 2022, "n": 12, "p25": 22000, "median": 24000, "p75": 26000}],
        },
    )
    res = run(tmp_path, [row(ys=2022, ye=2022)], [(fact("m-gen1-a", "NL", 50000), 2022)])
    b = bands(res, "m-gen1-a", "NL")[2022]
    assert b["method"] == "samples" and b["samples"] == 12 and b["estimate"] is False
    bt = res.document["backtest"]  # type: ignore[index]
    assert bt["rows_compared"] == 1 and bt["gate"] is False
    model = 50000 * up.kept_share(up.age_at(2022, date(2026, 11, 15), 7), CURVE)  # type: ignore[operator]
    assert bt["rows"][0]["error"] == pytest.approx(model / 24000 - 1, abs=1e-3)


def test_too_few_or_stale_samples_keep_the_model_band(tmp_path: Path) -> None:
    write_samples(
        tmp_path,
        {
            "country": "NL",
            "variant_id": "m-gen1-a",
            "observed_at": "2026-01-01",
            "currency": "EUR",
            "source": SRC,
            "rows": [
                {"build_year": 2022, "n": 12, "median": 24000},
                {"build_year": 2023, "n": 3, "median": 30000},
            ],
        },
    )
    res = run(
        tmp_path,
        [row(ys=2022, ye=2023)],
        [(fact("m-gen1-a", "NL", 50000), 2022), (fact("m-gen1-a", "NL", 50000), 2023)],
    )
    b = bands(res, "m-gen1-a", "NL")
    assert b[2022]["method"] == "model" and b[2023]["method"] == "model"
    assert res.document["backtest"]["rows_compared"] == 2  # type: ignore[index]


def test_generation_samples_give_generation_bands_and_backtest(tmp_path: Path) -> None:
    write_samples(
        tmp_path,
        {
            "country": "NL",
            "generation_id": "m-gen1",
            "observed_at": "2026-11-01",
            "currency": "EUR",
            "source": SRC,
            "rows": [{"build_year": 2022, "n": 20, "p25": 20000, "median": 23000, "p75": 25000}],
        },
    )
    rows = [row("m-gen1-a", 2022, 2022), row("m-gen1-b", 2022, 2022)]
    res = run(
        tmp_path,
        rows,
        [(fact("m-gen1-a", "NL", 40000), 2022), (fact("m-gen1-b", "NL", 60000), 2022)],
    )
    doc = res.document
    assert doc and doc["generation_bands"][0]["samples"] == 20
    assert doc["generation_bands"][0]["period"] == "2026-11"
    assert bands(res, "m-gen1-a", "NL")[2022]["method"] == "model"  # never spread onto variants
    assert doc["backtest"]["rows"][0]["subject"] == "m-gen1"


def test_bad_sample_files_are_reported_not_fatal(tmp_path: Path) -> None:
    write_samples(
        tmp_path,
        {
            "country": "NL",
            "variant_id": "m-gen1-a",
            "observed_at": "2026-11-01",
            "currency": "EUR",
            "source": {"name": "x"},
            "rows": [{"build_year": 2022}],
        },
    )
    write_samples(tmp_path, {"country": "NL"}, "b.yaml")
    res = run(tmp_path, [row()], [])
    assert len(res.log["sample_problems"]) == 2


def test_no_samples_note_and_coverage_lines(tmp_path: Path) -> None:
    res = run(tmp_path, [row(ys=2024, ye=2024)], [(fact("m-gen1-a", "NL", 40000), 2024)])
    assert res.document["backtest"]["note"] == "No manual samples yet"  # type: ignore[index]
    text = "\n".join(up.coverage_lines(res.log))
    assert "| NL | 1 | 0 | 0 |" in text and "no samples yet" in text
    json.dumps(res.document)


def test_release_ships_used_prices_and_qa_backtest(tmp_path: Path) -> None:
    from test_t059_sections import NOW
    from test_t059_sections import data_dir as make_data_dir

    from ev_pipeline.release.build import build_release, write_release

    d = make_data_dir.__wrapped__(tmp_path)  # type: ignore[attr-defined]
    res = build_release(d, now=NOW)
    assert res.used_prices is not None
    out = write_release(res, d, extras={})
    assert (out / up.FILE_NAME).exists()
    qa = json.loads((out / "qa.json").read_text())
    assert qa["backtest_used_prices"]["gate"] is False
    assert "## Used price bands (T-081, estimates)" in (out / "coverage.md").read_text()
