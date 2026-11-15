"""T-059: fueleconomy EPA range, Wikidata generation years, RDW known issues, charging stats.

Fixtures only (no network). Defect, charging and Wikidata rows below are SYNTHETIC: invented
numbers in the shape the adapters write (see each adapter's docstring).
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from ev_pipeline.derive.known_issues import (
    MIN_COHORT_REPORT_SHARE,
    MIN_REPORTED_CARS,
    age_band,
    build_known_issues,
)
from ev_pipeline.match.matcher import match_records
from ev_pipeline.match.seed import load_seed
from ev_pipeline.merge.generation_years import YEAR_TOLERANCE, corroborate_years
from ev_pipeline.qa.checks import check_licence_gate, check_sections
from ev_pipeline.records import SourceRecord
from ev_pipeline.release.build import build_release, epa_summary, section_gate_errors, write_release
from ev_pipeline.release.charging_stats import build_charging_stats
from ev_pipeline.release.gate import parse_registry
from ev_pipeline.release.validate import ReleaseError, _validator

FIX = Path(__file__).parent / "fixtures" / "release"
REPO_DATA = Path(__file__).resolve().parents[2] / "data"
NOW = datetime(2026, 11, 15, 3, 0, tzinfo=UTC)
SEED = load_seed(FIX / "models.yaml")

EXTRA_SOURCES = [
    {
        "id": "fueleconomy",
        "name": "fueleconomy.gov",
        "licence": "US-Government-Public-Domain",
        "status": "active",
    },
    {"id": "rdw-defects", "name": "RDW APK defects", "licence": "CC0-1.0", "status": "active"},
    {
        "id": "bnetza",
        "name": "BNetzA Ladesaeulenregister",
        "licence": "CC-BY-4.0",
        "status": "active",
        "aliases": ["bnetza-ladesaeulenregister"],
    },
    {
        "id": "eafo",
        "name": "EAFO",
        "licence": "EC reuse policy, third-party content unclear",
        "status": "blocked",
    },
]


def _registry(extra: list[dict[str, Any]] | None = None):
    base = yaml.safe_load((FIX / "sources.yaml").read_text(encoding="utf-8"))
    base["sources"] = list(base["sources"]) + (EXTRA_SOURCES if extra is None else extra)
    return parse_registry(base)


# --- licence gate aliases (Q-075) ---------------------------------------------------------


def test_alias_is_gated_like_its_registry_entry() -> None:
    reg = _registry()
    assert reg.canonical("bnetza-ladesaeulenregister") == "bnetza"
    assert reg.releasable("bnetza-ladesaeulenregister")
    assert reg.source_object("bnetza-ladesaeulenregister")["id"] == "bnetza"
    assert reg.reason_blocked("eafo") == "status blocked"
    assert reg.reason_blocked("unknown-alias") == "not in data/sources.yaml"


def test_alias_of_a_blocked_source_is_blocked_and_clashes_are_ignored() -> None:
    reg = _registry(
        [
            {"id": "a", "name": "A", "licence": "CC0-1.0", "status": "blocked", "aliases": ["x"]},
            {"id": "b", "name": "B", "licence": "CC0-1.0", "status": "active", "aliases": ["y"]},
            {"id": "c", "name": "C", "licence": "CC0-1.0", "status": "active", "aliases": ["y"]},
            # an alias equal to another entry's id never redirects that entry
            {"id": "d", "name": "D", "licence": "CC0-1.0", "status": "active", "aliases": ["a"]},
        ]
    )
    assert reg.reason_blocked("x") == "status blocked"
    assert reg.reason_blocked("y") == "not in data/sources.yaml"  # two owners: ignored
    assert reg.reason_blocked("a") == "status blocked"


# --- Wikidata generation years -------------------------------------------------------------


def _wd(model: str, boundary: str, year: int, item: str = "Q1") -> SourceRecord:
    return SourceRecord.model_validate(
        {
            "source": {"id": "wikidata", "name": "Wikidata", "licence": "CC0-1.0"},
            "record_key": f"wikidata:{model}/{item}#production_{boundary}:P571",
            "kind": "corroboration",
            "make": "x",
            "model": model,
            "variant_name": f"label {item}",
            "year": year,
            "retrieved_at": "2026-11-15",
            "confidence": "low",
        }
    )


def test_years_agree_within_tolerance_on_the_nearest_generation() -> None:
    res = corroborate_years(
        [
            _wd("renault-zoe", "start", 2012, "Q1"),  # ph1 2013: 1 year off -> agrees
            _wd("renault-zoe", "end", 2024, "Q2"),  # ph2 ends 2024
            _wd("renault-zoe", "start", 2017, "Q3"),  # nearest start 2019 (ph2): 2 off
        ],
        SEED,
    )
    ph1, ph2 = res.by_generation["renault-zoe-ph1"], res.by_generation["renault-zoe-ph2"]
    assert ph1["corroborated"] is True and ph1["tolerance_years"] == YEAR_TOLERANCE
    assert [c["agrees"] for c in ph2["checks"]] == [True, False]
    assert ph2["corroborated"] is False and ph2["source_ids"] == ["wikidata"]
    assert res.log["agree"] == 2 and res.log["disagree"] == 1
    assert res.log["disagreements"][0]["seed_year"] == 2019
    # never a value: the seed years are untouched
    assert (
        SEED.generations["renault-zoe-ph2"].year_start,
        SEED.generations["renault-zoe-ph2"].year_end,
    ) == (2019, 2024)


def test_end_year_for_a_model_still_on_sale_disagrees_and_unknown_models_skip() -> None:
    res = corroborate_years(
        [_wd("ford-mustang-mach-e", "end", 2025), _wd("bmw-ix", "start", 2021)], SEED
    )
    assert res.by_generation["ford-mustang-mach-e-gen1"]["checks"][0]["agrees"] is False
    assert res.log["skipped"] == {"model not in seed": 1}


def test_matcher_routes_wikidata_years_whatever_the_eea_flag() -> None:
    recs = [_wd("renault-zoe", "start", 2013)]
    for flag in (False, True):
        r = match_records(recs, SEED, eea_corroboration=flag)
        assert len(r.year_records) == 1 and r.corroboration_facts == [] and r.spec_facts == []


# --- RDW known issues ----------------------------------------------------------------------

SRC = {
    "id": "rdw",
    "name": "RDW Open Data: Geconstateerde Gebreken",
    "licence": "CC0-1.0",
    "url": "https://opendata.rdw.nl/d/a34c-vvps",
    "attribution": "Bron: RDW",
}


def _group(make: str, model: str, year: int, sample: int, any_: int) -> dict[str, Any]:
    return {
        "kind": "defect_group",
        "make": make,
        "model": model,
        "year": year,
        "sample_cars": sample,
        "cars_with_any_defect": any_,
        "country": "NL",
        "record_key": f"g:{make}|{model}|{year}",
        "retrieved_at": "2026-11-15",
        "reported_from": "2022-06-02",
        "reported_to": "2026-11-13",
        "confidence": "medium",
        "inspection": "APK",
        "sample_rule": "fixture",
        "source": SRC,
    }


def _code(make: str, model: str, year: int, code: str, cars: int, label: str) -> dict[str, Any]:
    return {
        "kind": "defect_count",
        "make": make,
        "model": model,
        "year": year,
        "defect_code": code,
        "defect_description": label,
        "defect_article": "5.*.1",
        "cars_with_defect": cars,
        "record_key": f"g:{make}|{model}|{year}#defect:{code}",
        "retrieved_at": "2026-11-15",
        "source": SRC,
    }


DEFECTS = [
    _group("TESLA", "MODEL 3", 2020, 100, 50),
    _group("TESLA", "MODEL3", 2020, 50, 20),  # second spelling: summed into the same cohort
    _code("TESLA", "MODEL 3", 2020, "205", 10, "Band onvoldoende profiel"),
    _code("TESLA", "MODEL3", 2020, "205", 5, "Band onvoldoende profiel"),
    _code("TESLA", "MODEL 3", 2020, "516", 2, "Remschijf"),  # 2 cars < MIN_CARS_PER_CODE (3)
    _group("NISSAN", "LEAF", 2020, 50, 30),  # ze1 (2018-2025)
    _code("NISSAN", "LEAF", 2020, "205", 20, "Band onvoldoende profiel"),
    _group("ZOEMAKER", "UNKNOWN", 2020, 100, 0),  # not in the seed: baseline only
    _group("RENAULT", "ZOE", 2019, 40, 20),  # 2019 is shared by ph1 and ph2
    _group("TESLA", "MODEL 3", 2023, 400, 5),  # young cohort: few reports
]


def _known(rows=DEFECTS, gens_with_rows=frozenset(), releasable=lambda s: True):
    return build_known_issues(list(rows), SEED, set(gens_with_rows), releasable)


def test_known_issues_sums_groups_and_rates_per_100_within_the_year() -> None:
    res = _known()
    sec = res.section
    assert (
        sec is not None and sec["source_id"] == "rdw-defects" and res.source["id"] == "rdw-defects"
    )
    m3 = {c["first_registration_year"]: c for c in sec["by_generation"]["tesla-model-3-gen1"]}
    c = m3[2020]
    assert (c["sample_cars"], c["cars_with_any_defect"], c["any_defect_per_100"]) == (150, 70, 46.7)
    assert c["age_years"] == 6 and c["age_band"] == "5-6 years"
    # baseline: every sampled BEV of 2020 (incl. the make not in the seed)
    assert c["cohort"] == {"generations": 2, "sample_cars": 300, "any_defect_per_100": 33.3}
    assert c["defects"] == [
        {"code": "205", "cars_with_defect": 15, "per_100": 10.0, "cohort_per_100": 11.7}
    ]  # code 516 dropped (2 cars)
    assert {x["code"] for x in sec["codes"]} == {"205"}
    assert sec["codes"][0]["label_nl"] == "Band onvoldoende profiel"
    assert res.log["skipped_groups"] == {
        "model not in seed": 1,
        "shared year, generation unknown": 1,
    }


def test_young_or_thin_cohorts_are_marked_few_reports() -> None:
    m3 = {
        c["first_registration_year"]: c
        for c in _known().section["by_generation"]["tesla-model-3-gen1"]
    }
    assert m3[2023]["few_reports"] is True  # 5 of 400 < MIN_COHORT_REPORT_SHARE
    assert m3[2020]["few_reports"] is False
    assert MIN_REPORTED_CARS == 10 and MIN_COHORT_REPORT_SHARE == 0.10


def test_shared_year_placed_only_when_one_generation_has_rows() -> None:
    res = _known(gens_with_rows={"renault-zoe-ph2"})
    assert "renault-zoe-ph2" in res.section["by_generation"]
    assert "renault-zoe-ph1" not in res.section["by_generation"]


def test_small_cohorts_are_dropped() -> None:
    res = _known([_group("TESLA", "MODEL 3", 2020, 19, 5)])
    assert res.section is None and res.log["status"] == "nothing placed"


def test_known_issues_respect_the_licence_gate() -> None:
    res = _known(releasable=lambda s: s != "rdw-defects")
    assert res.section is None and res.log["blocked_sources"] == ["rdw-defects"]


def test_known_issues_section_validates_and_age_bands() -> None:
    errors = list(_validator("KnownIssues").iter_errors(_known().section))
    assert errors == []
    assert [age_band(a) for a in (3, 4, 5, 9, 10)] == [
        "up to 4 years",
        "up to 4 years",
        "5-6 years",
        "7-9 years",
        "10+ years",
    ]


# --- charging stats ------------------------------------------------------------------------

TAXONOMY = {
    "charging_metrics": [{"id": "public-points"}],
    "charging_definitions": [
        {"id": "de-bnetza-ladepunkt", "source_id": "bnetza-ladesaeulenregister"},
        {"id": "afir-recharging-point", "source_id": "eafo"},
    ],
    "power_bands": [{"id": "dc-150-349"}],
}


def _stat(sid: str, definition: str, i: int, **kw: Any) -> dict[str, Any]:
    return {
        "id": f"{sid}:de::2026-0{i}-01:public-points:all",
        "country": "DE",
        "region": None,
        "period_end": f"2026-0{i}-01",
        "metric_id": "public-points",
        "power_band_id": None,
        "value": 1000 + i,
        "unit": "count",
        "source_id": sid,
        "definition_id": definition,
        "confidence": "high",
        "entered_by": "pipeline",
        "retrieved_at": "2026-11-15",
        **kw,
    }


def _stage(staging: Path, name: str, source: str, rows: list[dict], releasable: bool) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    (staging / f"{name}.charging_stats.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )
    meta = {
        "source": source,
        "releasable": releasable,
        "licence": "CC-BY-4.0",
        "attribution": "Bundesnetzagentur.de",
        "download": {"url": "https://example.org/x.xlsx"},
    }
    (staging / f"{name}.charging_stats.meta.json").write_text(json.dumps(meta), encoding="utf-8")


def _charging_staging(tmp: Path) -> Path:
    st = tmp / "staging"
    _stage(
        st,
        "bnetza",
        "bnetza",
        [
            _stat("bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 1),
            _stat(
                "bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 2, power_band_id="dc-150-349"
            ),
            _stat("bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 3, power_band_id="nope"),
            _stat("bnetza-ladesaeulenregister", "nope-definition", 4),
            _stat("bnetza-ladesaeulenregister", "afir-recharging-point", 5),  # other source's def
            _stat("someone-else", "de-bnetza-ladepunkt", 6),
            _stat("bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 7, value=-1),
        ],
        True,
    )
    _stage(st, "eafo", "eafo", [_stat("eafo", "afir-recharging-point", 1)], False)
    return st


def test_charging_stats_ship_aliased_rows_and_keep_eafo_out(tmp_path: Path) -> None:
    res = build_charging_stats(_charging_staging(tmp_path), _registry(), TAXONOMY, 2, "t")
    doc = res.document
    assert doc is not None and len(doc["stats"]) == 2
    assert doc["source_aliases"] == {"bnetza-ladesaeulenregister": "bnetza"}
    assert [s["id"] for s in doc["sources"]] == ["bnetza-ladesaeulenregister"]
    assert all(s["source_id"] != "eafo" for s in doc["stats"])
    files = res.log["files"]
    assert files["eafo"]["gated"] == "status blocked" and files["eafo"]["shipped"] == 0
    assert files["bnetza"]["dropped"] == {
        "definition belongs to another source": 1,
        "fails the ChargingStat schema": 1,
        "source_id someone-else is not bnetza or one of its aliases": 1,
        "unknown definition_id": 1,
        "unknown power_band_id": 1,
    }
    assert list(_validator("ChargingStatsRelease").iter_errors(doc)) == []


def test_eafo_stays_out_even_if_marked_releasable_while_blocked(tmp_path: Path) -> None:
    st = tmp_path / "staging"
    _stage(st, "eafo", "eafo", [_stat("eafo", "afir-recharging-point", 1)], True)
    res = build_charging_stats(st, _registry(), TAXONOMY, 2, "t")
    assert res.document is None and res.log["files"]["eafo"]["gated"] == "status blocked"


def test_charging_stats_need_the_taxonomy_and_a_releasable_meta(tmp_path: Path) -> None:
    st = _charging_staging(tmp_path)
    res = build_charging_stats(st, _registry(), None, 2, "t")
    assert res.document is None
    assert "taxonomy" in res.log["files"]["bnetza"]["gated"]
    _stage(
        st,
        "bnetza",
        "bnetza",
        [_stat("bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 1)],
        False,
    )
    res = build_charging_stats(st, _registry(), TAXONOMY, 2, "t")
    assert res.document is None and "releasable" in res.log["files"]["bnetza"]["gated"]


def test_section_gate_errors_catch_blocked_sources() -> None:
    reg = _registry()
    cat = {
        "known_issues": {"source_id": "eafo"},
        "generations": [{"id": "g", "years_corroboration": {"checks": [{"source_id": "nyland"}]}}],
    }
    charging = {"sources": [{"id": "eafo"}], "stats": [{"source_id": "eafo"}]}
    errs = section_gate_errors(cat, charging, reg.releasable)
    assert len(errs) == 4
    check = check_licence_gate({"sources": [], "rows": [], **cat}, [], reg, charging)
    assert check.status == "fail" and check.details["error_count"] == 4


# --- EPA range: own field, never compared with WLTP ------------------------------------------


def _fe(make: str, model: str, year: int, km: float, n: int) -> str:
    return (
        json.dumps(
            {
                "source": {
                    "id": "fueleconomy",
                    "name": "fueleconomy.gov",
                    "licence": "US-Government-Public-Domain",
                },
                "record_key": f"vehicles.csv:id={n};market=us",
                "kind": "spec",
                "make": make,
                "model": model,
                "year": year,
                "specs": {
                    "epa_range_km": {"value": km, "unit": "km"},
                    "consumption_kwh_100km": {"value": 20.0, "unit": "kWh/100km"},
                },
                "retrieved_at": "2026-11-15",
                "confidence": "medium",
            }
        )
        + "\n"
    )


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for t in ("charging_metrics", "charging_definitions", "power_bands"):
        shutil.copy(REPO_DATA / "taxonomy" / f"{t}.yaml", d / "taxonomy" / f"{t}.yaml")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    shutil.copy(FIX / "field_sources.yaml", d / "field_sources.yaml")
    reg = yaml.safe_load((FIX / "sources.yaml").read_text(encoding="utf-8"))
    reg["sources"] += EXTRA_SOURCES
    (d / "sources.yaml").write_text(yaml.safe_dump(reg, allow_unicode=True), encoding="utf-8")
    st = d / "staging"
    with (st / "openev.records.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "source": {
                        "id": "openev",
                        "name": "OpenEV Data",
                        "licence": "CDLA-Permissive-2.0",
                    },
                    "record_key": "ford/mach-e/2022-er-awd#epa",
                    "kind": "spec",
                    "make": "Ford",
                    "model": "Mustang Mach-E",
                    "variant_name": "Extended Range AWD",
                    "year": 2022,
                    "specs": {"epa_range_km": {"value": 500.0, "unit": "km"}},
                    "retrieved_at": "2026-11-14",
                    "confidence": "medium",
                }
            )
            + "\n"
        )
    (st / "fueleconomy.records.jsonl").write_text(
        _fe("Ford", "Mustang Mach-E AWD", 2022, 505.0, 1)  # within 2 % of OpenEV's EPA
        # Equal to the e-C4's WLTP figure on purpose: must NOT count as WLTP agreement.
        + _fe("Citroen", "e-C4", 2021, 350.0, 2),
        encoding="utf-8",
    )
    (st / "rdw-defects.defects.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in DEFECTS), encoding="utf-8"
    )
    (st / "wikidata.records.jsonl").write_text(
        _wd("renault-zoe", "start", 2013).model_dump_json()
        + "\n"
        + _wd("tesla-model-3", "start", 2017, "Q9").model_dump_json()
        + "\n",
        encoding="utf-8",
    )
    _stage(
        st,
        "bnetza",
        "bnetza",
        [_stat("bnetza-ladesaeulenregister", "de-bnetza-ladepunkt", 1)],
        True,
    )
    _stage(st, "eafo", "eafo", [_stat("eafo", "afir-recharging-point", 1)], False)
    return d


def test_release_ships_all_four_sections(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    cat = res.catalogue
    rows = {r["variant_id"]: r for r in cat["rows"]}
    mach = next(r for v, r in rows.items() if v.startswith("ford-mustang-mach-e-gen1"))
    p = mach["provenance"]["epa_range_km"]
    assert mach["epa_range_km"] == 505.0  # fueleconomy is the EPA primary
    assert p["agreeing_sources"] == 2 and set(p["source_ids"]) == {"fueleconomy", "openev"}
    c4 = next(r for v, r in rows.items() if v.startswith("citroen-e-c4"))
    assert "fueleconomy" not in c4["provenance"]["wltp_range_km"]["source_ids"]
    assert c4["provenance"]["epa_range_km"]["agreeing_sources"] == 1
    assert epa_summary(cat["rows"])["second_source_via_fueleconomy"] == 1
    # generation years: corroboration flag only, years unchanged
    gens = {g["id"]: g for g in cat["generations"]}
    assert gens["renault-zoe-ph1"]["years_corroboration"]["corroborated"] is True
    assert gens["tesla-model-3-gen1"]["years_corroboration"]["corroborated"] is False
    assert gens["tesla-model-3-gen1"]["year_start"] == 2019
    # known issues + sources
    assert "tesla-model-3-gen1" in cat["known_issues"]["by_generation"]
    ids = {s["id"] for s in cat["sources"]}
    assert {"fueleconomy", "wikidata", "rdw-defects"} <= ids
    # charging stats: bnetza via alias, eafo gated
    assert res.charging_stats is not None
    assert {s["source_id"] for s in res.charging_stats["stats"]} == {"bnetza-ladesaeulenregister"}
    assert res.sections["charging_stats"]["files"]["eafo"]["gated"] == "status blocked"
    qa = check_sections(cat, res.charging_stats)
    assert qa.status == "flag" and len(qa.details["generation_years"]["disagreements"]) == 1


def test_release_writes_charging_stats_file_and_coverage(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    out = write_release(res, data_dir, extras={})
    doc = json.loads((out / "charging_stats.json").read_text(encoding="utf-8"))
    assert doc["release"] == res.release and len(doc["stats"]) == 1
    cov = (out / "coverage.md").read_text(encoding="utf-8")
    assert "| epa_range_km |" in cov and "Known issues" in cov and "gated: status blocked" in cov
    qa = json.loads((out / "qa.json").read_text(encoding="utf-8"))
    assert qa["checks"]["licence_gate"]["status"] == "pass"
    assert qa["checks"]["sections"]["details"]["charging_stats"] == {
        "bnetza-ladesaeulenregister": 1
    }


def test_release_fails_closed_when_a_section_source_is_blocked(data_dir: Path) -> None:
    reg = yaml.safe_load((data_dir / "sources.yaml").read_text(encoding="utf-8"))
    for s in reg["sources"]:
        if s["id"] == "rdw-defects":
            s["status"] = "blocked"
    (data_dir / "sources.yaml").write_text(yaml.safe_dump(reg), encoding="utf-8")
    res = build_release(data_dir, now=NOW)
    assert "known_issues" not in res.catalogue
    assert res.sections["known_issues"]["status"] == "gated"
    assert "rdw-defects" not in {s["id"] for s in res.catalogue["sources"]}


def test_release_fails_if_charging_document_breaks_schema(
    data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import ev_pipeline.release.charging_stats as cs

    real = cs._validator

    def broken(name: str):
        v = real(name)
        if name == "ChargingStatsRelease":

            class _V:
                def iter_errors(self, doc):  # noqa: ANN001, ANN202
                    return iter([type("E", (), {"message": "boom"})()])

            return _V()
        return v

    monkeypatch.setattr(cs, "_validator", broken)
    with pytest.raises(ReleaseError, match="charging_stats.json fails the schema"):
        build_release(data_dir, now=NOW)


def test_date_type_in_checks() -> None:
    res = corroborate_years([_wd("renault-zoe", "start", 2013)], SEED)
    assert (
        res.by_generation["renault-zoe-ph1"]["checks"][0]["retrieved_at"]
        == date(2026, 11, 15).isoformat()
    )
