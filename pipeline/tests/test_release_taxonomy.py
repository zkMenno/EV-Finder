"""Optional taxonomy tables in the release (T-024, T-019) and allowed-value fact checks.

Uses the release fixture plus the real data/taxonomy tables (our own, licence-clean text).
"""

from __future__ import annotations

import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.release.build import build_release, summary
from ev_pipeline.release.taxonomy import OPTIONAL_TABLES, optional_taxonomy_errors
from ev_pipeline.release.validate import (
    ReleaseError,
    check_fact_ranges,
    enum_fact_errors,
    value_reason,
)
from ev_pipeline.schema_models import Fact

FIX = Path(__file__).parent / "fixtures" / "release"
REPO_TAXONOMY = Path(__file__).resolve().parents[2] / "data" / "taxonomy"
NOW = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    for name in OPTIONAL_TABLES:
        shutil.copy(REPO_TAXONOMY / f"{name}.yaml", d / "taxonomy" / f"{name}.yaml")
    return d


def _equipment(d: Path) -> list[dict]:
    return yaml.safe_load((d / "taxonomy" / "bidi_equipment.yaml").read_text())["bidi_equipment"]


def test_optional_tables_ship_in_taxonomy(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)  # passes schema validation of the whole catalogue
    tax = res.catalogue["taxonomy"]
    for name in OPTIONAL_TABLES:
        assert name in tax
    assert {r["id"] for r in tax["bidi_modes"]} == {"v2l", "v2h", "v2g", "v2b"}
    assert any(b["id"] == "dc-150-349" and b["ours"] for b in tax["power_bands"])
    assert res.catalogue_gzip_bytes < 300_000


def test_equipment_held_back_until_sources_are_releasable(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    assert res.catalogue["taxonomy"]["bidi_equipment"] == []
    held = res.taxonomy_held_back["bidi_equipment"]
    assert len(held) == len(_equipment(data_dir))
    assert "not in data/sources.yaml" in held["dcbel-ara"]
    assert summary(res)["taxonomy_rows_held_back"] == res.taxonomy_held_back


def test_equipment_row_ships_once_its_sources_are_active(data_dir: Path) -> None:
    row = next(r for r in _equipment(data_dir) if r["id"] == "dcbel-ara")
    eq_path = data_dir / "taxonomy" / "bidi_equipment.yaml"
    eq_path.write_text(yaml.safe_dump({"bidi_equipment": [row, _equipment(data_dir)[0]]}))
    reg_path = data_dir / "sources.yaml"
    reg = yaml.safe_load(reg_path.read_text())
    for sid in row["source_ids"]:
        reg["sources"].append({"id": sid, "name": sid, "licence": "CC-BY-4.0", "status": "active"})
    reg_path.write_text(yaml.safe_dump(reg))
    res = build_release(data_dir, now=NOW)
    shipped = [r["id"] for r in res.catalogue["taxonomy"]["bidi_equipment"]]
    assert shipped == ["dcbel-ara"]
    assert list(res.taxonomy_held_back["bidi_equipment"]) == ["mobilize-powerbox-verso"]


def test_missing_optional_files_are_skipped(data_dir: Path) -> None:
    for name in OPTIONAL_TABLES:
        (data_dir / "taxonomy" / f"{name}.yaml").unlink()
    res = build_release(data_dir, now=NOW)
    assert set(res.catalogue["taxonomy"]) == {
        "voltage_classes",
        "chemistries",
        "cooling_types",
        "glossary_terms",
    }


def test_no_optional_tables_without_base_taxonomy(data_dir: Path) -> None:
    for name in ("voltage_classes", "chemistries", "cooling_types", "glossary_terms"):
        (data_dir / "taxonomy" / f"{name}.yaml").unlink()
    for n in ("platforms", "battery_packs", "variant_links"):
        (data_dir / "seed" / f"{n}.yaml").unlink()
    res = build_release(data_dir, now=NOW)
    assert "taxonomy" not in res.catalogue
    assert res.taxonomy_held_back["(all)"]


def test_dangling_power_band_fails_release(data_dir: Path) -> None:
    p = data_dir / "taxonomy" / "power_bands.yaml"
    p.write_text(p.read_text().replace("maps_to: [dc-50-149]", "maps_to: [dc-9000]", 1))
    with pytest.raises(ReleaseError, match="maps_to 'dc-9000'"):
        build_release(data_dir, now=NOW)


def test_schema_violation_in_optional_table_fails_release(data_dir: Path) -> None:
    p = data_dir / "taxonomy" / "bidi_status.yaml"
    p.write_text(p.read_text().replace("    filter_group: live", "    filter_group: maybe", 1))
    with pytest.raises(ReleaseError, match="maybe"):
        build_release(data_dir, now=NOW)


def test_cross_reference_errors() -> None:
    tables = {
        "bidi_routes": [{"id": "ac-onboard"}],
        "bidi_modes": [{"id": "v2g"}],
        "bidi_equipment": [
            {
                "id": "box",
                "route_id": "teleport",
                "mode_ids": ["v2g", "v2x"],
                "protocol_ids": ["iso15118-20"],
                "compatible_platform_ids": ["vw-meb", "nope"],
            }
        ],
        "charging_definitions": [{"id": "a", "replaced_by": "b"}],
    }
    errs = optional_taxonomy_errors(tables, {"vw-meb"})
    assert any("unknown route_id 'teleport'" in e for e in errs)
    assert any("unknown mode_ids 'v2x'" in e for e in errs)
    assert any("protocol_ids needs bidi_protocols.yaml" in e for e in errs)
    assert any("unknown platform 'nope'" in e for e in errs)
    assert any("unknown replaced_by 'b'" in e for e in errs)


# --- allowed values for enum-valued facts (Decision 020) -------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "ok"),
    [
        ("iso15118_20_support", "yes", True),
        ("iso15118_20_support", "not-disclosed", True),
        ("iso15118_20_support", "maybe", False),
        ("iso15118_20_support", True, False),
        ("heat_pump", "option", True),
        ("heat_pump", "yes", False),
        ("drag_coefficient", 0.23, True),
        ("drag_coefficient", "not-disclosed", True),
        ("drag_coefficient", 1.2, False),
        ("drag_coefficient", 0, False),
        ("drag_coefficient", "0.23", False),
        ("ac_kw", "anything", True),
    ],
)
def test_value_reason(field: str, value: object, ok: bool) -> None:
    assert (value_reason(field, value) is None) is ok


def _fact(field: str, value: object) -> MatchedFact:
    f = Fact(
        id=f"openev:k:{field}:{value}",
        subject_type="variant",
        subject_id="x-base",
        field=field,
        value=value,
        unit="id" if isinstance(value, str) else "",
        source={"id": "openev", "name": "o", "licence": "CDLA-Permissive-2.0"},
        source_record="k",
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
    )
    return MatchedFact(f, "openev", 30, 2022)


def test_bad_enum_fact_is_dropped_and_listed() -> None:
    keep, dropped = check_fact_ranges(
        [_fact("iso15118_20_support", "yes"), _fact("iso15118_20_support", "probably")]
    )
    assert [k.fact.value for k in keep] == ["yes"]
    assert dropped[0].field == "iso15118_20_support"
    assert "not an allowed value" in dropped[0].reason


def test_enum_fact_guard_on_published_facts() -> None:
    facts = [
        {"id": "a", "field": "heat_pump", "value": "standard"},
        {"id": "b", "field": "heat_pump", "value": "sometimes"},
        {"id": "c", "field": "drag_coefficient", "value": 2},
    ]
    errs = enum_fact_errors(facts)
    assert len(errs) == 2 and "fact b" in errs[0] and "fact c" in errs[1]
