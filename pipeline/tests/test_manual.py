"""P7 manual facts: file format, validation rules, `ev manual check`, licence gate."""

from __future__ import annotations

import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from ev_pipeline.commands.manual import check
from ev_pipeline.manual.facts import (
    MANUAL_SOURCE_ID,
    expected_unit,
    load_manual_dir,
    parse_manual_file,
)
from ev_pipeline.release.build import build_release
from ev_pipeline.release.gate import load_registry

FIX = Path(__file__).parent / "fixtures" / "manual"
REPO_DATA = Path(__file__).resolve().parents[2] / "data"
TODAY = date(2026, 11, 15)
NOW = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)
RELEASE_FIX = Path(__file__).parent / "fixtures" / "release"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Same layout as test_release.data_dir: the release fixtures in a scratch data dir."""
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(RELEASE_FIX / "staging", d / "staging")
    shutil.copytree(RELEASE_FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / f"{n}.yaml")
    return d


def _with_manual(d: Path, *topics: str) -> Path:
    for t in topics:
        shutil.copytree(FIX / t, d / "manual" / t)
    return d


def _set_manual_registry(d: Path, entry: dict | None) -> None:
    p = d / "sources.yaml"
    reg = yaml.safe_load(p.read_text())
    reg["sources"] = [s for s in reg["sources"] if s["id"] != MANUAL_SOURCE_ID]
    if entry is not None:
        reg["sources"].append(entry)
    p.write_text(yaml.safe_dump(reg))


BLOCKED = {
    "id": "manual",
    "name": "Manual entries",
    "licence": "none (individual facts cited by URL and date)",
    "status": "blocked",
}


def _write(tmp: Path, facts: list[dict], **file_keys) -> Path:
    p = tmp / "t.yaml"
    p.write_text(yaml.safe_dump({"schema": "manual-facts/v1", **file_keys, "facts": facts}))
    return p


GOOD = {
    "variant_id": "tesla-model-3-gen1-lr",
    "field": "ac_kw",
    "value": 11,
    "unit": "kW",
    "source_url": "https://example.org/x",
    "retrieved": "2026-11-01",
    "locator": "p. 2",
    "entered_by": "test",
    "confidence": "low",
}


def test_valid_file_parses_to_schema_facts() -> None:
    facts, issues, fixture = parse_manual_file(
        FIX / "warranty" / "fixture-warranty.yaml", "data/manual/warranty/f.yaml", "warranty", TODAY
    )
    assert issues == [] and not fixture
    assert len(facts) == 2
    f = facts[0].fact
    assert (
        f.source.id.root == "manual" and f.source.url == "https://example.org/fixture/warranty.pdf"
    )
    assert f.retrieved_at == date(2026, 11, 1) and f.unit == "km" and f.claim is True
    assert f.id == "manual:warranty/fixture-warranty:tesla-model-3-gen1-lr:warranty_km"
    assert facts[1].fact.subject_type.value == "generation" and facts[1].fact.claim is None


def test_broken_file_lists_every_rule() -> None:
    _, issues, _ = parse_manual_file(
        FIX / "broken" / "fixture-broken.yaml", "data/manual/broken/b.yaml", "broken", TODAY
    )
    text = "\n".join(i.message for i in issues)
    for needle in (
        "source_url is required",
        "entered_by is required",
        "unit 'mi' does not match wltp_range_km (use 'km')",
        "retrieved date is required",
        "give a quote or a page locator",
        "give exactly one of variant_id or generation_id",
        "unknown field 'colour'",
        "price_new needs a country",
        "is in the future",
        "confidence must be high, medium or low",
    ):
        assert needle in text, needle
    assert {i.index for i in issues} == {0, 1, 2, 3, 4}


@pytest.mark.parametrize(
    ("change", "needle"),
    [
        ({"value": 99}, "out of range"),
        ({"value": "eleven"}, "needs a number"),
        ({"value": True}, "needs a number"),
        ({"source_url": "not a url"}, "source_url"),
        ({"retrieved": "15/11/2026"}, "ISO date"),
        ({"field": "registered_count", "unit": "count"}, "registered_count"),
        ({"field": "heat_pump", "unit": "enum", "value": "maybe"}, "not an allowed value"),
        ({"field": "chemistry_id", "unit": "id", "value": "NMC 811"}, "taxonomy id"),
        ({"country": "XX"}, "country"),
        ({"claim": "yes"}, "claim must be"),
        ({"colour": "red"}, "unknown key 'colour'"),
        ({"variant_id": "Not An Id"}, "schema Fact subject_id"),
    ],
)
def test_single_rule(tmp_path: Path, change: dict, needle: str) -> None:
    p = _write(tmp_path, [{**GOOD, **change}])
    facts, issues, _ = parse_manual_file(p, "data/manual/x/t.yaml", "x", TODAY)
    assert facts == [] and any(needle in i.message for i in issues), [i.message for i in issues]


def test_price_curve_enum_and_file_level_entered_by(tmp_path: Path) -> None:
    rows = [
        {**GOOD, "field": "price_new", "unit": "EUR", "value": 41990, "country": "NL"},
        {
            **GOOD,
            "field": "dc_curve",
            "unit": "kW",
            "value": {"points": [[10, 150], [80, 50]], "status": "measured"},
        },
        {**GOOD, "field": "heat_pump", "unit": "enum", "value": "option"},
    ]
    for r in rows:
        r.pop("entered_by")
    p = _write(tmp_path, rows, entered_by="menno")
    facts, issues, _ = parse_manual_file(p, "data/manual/x/t.yaml", "x", TODAY)
    assert issues == [], [i.message for i in issues]
    assert [m.entered_by for m in facts] == ["menno"] * 3
    assert facts[0].fact.country.value == "NL" and facts[0].record_key.endswith(":NL")


def test_expected_units_cover_every_field_but_price() -> None:
    from ev_pipeline.schema_models import FactField

    missing = [f.value for f in FactField if expected_unit(f.value) is None]
    assert missing == ["price_new"]


def test_duplicates_and_topic_folder(tmp_path: Path) -> None:
    d = tmp_path / "data"
    for name in ("a", "b"):
        (d / "manual" / "t").mkdir(parents=True, exist_ok=True)
        _write(tmp_path, [GOOD]).rename(d / "manual" / "t" / f"{name}.yaml")
    _write(tmp_path, [GOOD]).rename(d / "manual" / "loose.yaml")
    load = load_manual_dir(d, TODAY)
    assert len(load.facts) == 1
    msgs = [i.message for i in load.errors]
    assert any("duplicate of t/a:" in m for m in msgs)
    assert any("topic folder" in m for m in msgs)


def test_example_folder_is_checked_but_never_released(tmp_path: Path) -> None:
    d = tmp_path / "data"
    shutil.copytree(REPO_DATA / "manual" / "_example", d / "manual" / "_example")
    assert load_manual_dir(d, TODAY).facts == []
    full = load_manual_dir(d, TODAY, for_release=False)
    assert len(full.facts) == 1 and full.errors == []
    assert full.fixture_files == {"data/manual/_example/example.yaml"}


def test_repo_example_and_registry_entry() -> None:
    """The committed example passes `ev manual check`; `manual` is blocked (Q-008)."""
    # Real repo data, so check against the real date: a fixed TODAY fails every newer fact.
    code, lines = check(REPO_DATA, date.today())
    assert code == 0, lines
    assert "internal only (status blocked)" in lines[-1]
    reg = load_registry(REPO_DATA / "sources.yaml")
    assert reg.reason_blocked("manual") == "status blocked"


def test_check_command_exit_codes(tmp_path: Path, capsys) -> None:
    from ev_pipeline.cli import main

    d = tmp_path / "data"
    shutil.copytree(FIX / "broken", d / "manual" / "broken")
    assert main(["manual", "check", "--data-dir", str(d)]) == 1
    out = capsys.readouterr().out
    assert "facts[1]: error: unit 'mi'" in out
    shutil.rmtree(d / "manual" / "broken")
    shutil.copytree(FIX / "warranty", d / "manual" / "warranty")
    assert main(["manual", "check", "--data-dir", str(d)]) == 0


def test_release_gate_keeps_manual_facts_internal(data_dir: Path) -> None:
    d = _with_manual(data_dir, "warranty")
    _set_manual_registry(d, BLOCKED)
    res = build_release(d, now=NOW)
    assert not any(f["source"]["id"] == "manual" for f in res.facts)
    assert "manual" not in {s["id"] for s in res.catalogue["sources"]}
    assert res.gated["manual"] == {"reason": "status blocked", "records": 2}
    assert any(i["path"] == "data/manual/warranty/fixture-warranty.yaml" for i in res.inputs)

    _set_manual_registry(d, None)  # not listed at all: blocked as well (fail closed)
    res = build_release(d, now=NOW)
    assert not any(f["source"]["id"] == "manual" for f in res.facts)
    assert res.gated["manual"]["reason"] == "not in data/sources.yaml"


def test_release_uses_manual_facts_once_releasable(data_dir: Path) -> None:
    d = _with_manual(data_dir, "warranty")
    _set_manual_registry(d, {**BLOCKED, "status": "active", "licence": "CC-BY-4.0"})
    res = build_release(d, now=NOW)
    manual = [f for f in res.facts if f["source"]["id"] == "manual"]
    by_field = {f["field"]: f for f in manual}
    assert by_field["warranty_km"]["subject_id"] == "tesla-model-3-gen1-lr"
    # A generation fact lands on every variant of that generation in the release.
    leaf = [f for f in manual if f["field"] == "warranty_years"]
    vids = {
        r["variant_id"] for r in res.catalogue["rows"] if r["generation_id"] == "nissan-leaf-ze0"
    }
    assert {f["subject_id"] for f in leaf} == vids and vids
    assert all(f["id"].endswith("@" + f["subject_id"]) for f in leaf)


def test_release_lists_bad_manual_entries(data_dir: Path) -> None:
    d = _with_manual(data_dir, "broken")
    _set_manual_registry(d, {**BLOCKED, "status": "active", "licence": "CC-BY-4.0"})
    res = build_release(d, now=NOW)
    stages = [p for p in res.problems if p.stage == "manual"]
    assert stages and all(p.source_id == "manual" for p in stages)
    assert not any(f["source"]["id"] == "manual" for f in res.facts)


def test_own_schema_topics_are_left_alone(tmp_path: Path) -> None:
    """data/manual/prices and data/manual/charging have their own loaders (T-081, T-025)."""
    shutil.copytree(REPO_DATA / "manual", tmp_path / "manual")
    shutil.copy(REPO_DATA / "sources.yaml", tmp_path / "sources.yaml")
    (tmp_path / "manual" / "prices").mkdir(exist_ok=True)
    (tmp_path / "manual" / "prices" / "x.yaml").write_text(
        "generation_id: g\ncountry: NL\nrows: []\n"
    )
    # Real date: this copies the repo's manual data, whose facts carry real retrieval dates.
    code, lines = check(tmp_path, date.today())
    assert code == 0, lines
