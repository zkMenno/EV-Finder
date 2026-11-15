"""Release edge cases (overnight coverage pass): staging parse errors, path logging, folder
safety, diff with changed/removed variants, licence gate wording, optional taxonomy and
schema/provenance guards.

Uses the shared synthetic release fixture (fixtures/release/) copied into a tmp data folder,
plus tiny SYNTHETIC dicts built in this file. No network.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from ev_pipeline.release import build as rb
from ev_pipeline.release.build import (
    build_release,
    compute_diff,
    default_data_dir,
    load_staging,
    log_path,
    release_cmd,
    write_release,
)
from ev_pipeline.release.gate import licence_problem, load_registry, parse_registry
from ev_pipeline.release.taxonomy import load_optional_taxonomy, optional_taxonomy_errors
from ev_pipeline.release.validate import ReleaseError, provenance_errors, schema_errors

FIX = Path(__file__).parent / "fixtures" / "release"
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
    return d


# --- loading and paths -------------------------------------------------------------------


def test_default_data_dir_follows_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert default_data_dir() == tmp_path
    monkeypatch.delenv("EV_DATA_DIR")
    assert default_data_dir() == rb.REPO_ROOT / "data"


def test_load_staging_without_folder(tmp_path: Path) -> None:
    assert load_staging(tmp_path / "nope") == ([], [], [])


def test_load_staging_skips_blank_lines_and_reports_bad_ones(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    staging.mkdir()
    good = (FIX / "staging" / "eea.records.jsonl").read_text().splitlines()[0]
    (staging / "eea.records.jsonl").write_text(
        good + "\n\n   \n{not json}\n" + '{"source": {"id": "eea"}}\n', encoding="utf-8"
    )
    (staging / "nyland.records.jsonl").write_text(good + "\n", encoding="utf-8")
    records, inputs, problems = load_staging(staging)
    assert len(records) == 1
    assert [p.record_key for p in problems] == ["eea.records.jsonl:4", "eea.records.jsonl:5"]
    assert all(p.stage == "parse" and p.source_id == "eea" for p in problems)
    by_path = {Path(i["path"]).name: i for i in inputs}
    assert by_path["eea.records.jsonl"]["records"] == 1
    assert "permission pending" in by_path["nyland.records.jsonl"]["skipped"]


def test_log_path_never_logs_an_absolute_host_path(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "releases").mkdir(parents=True)
    assert log_path(data / "releases" / "3", data) == "data/releases/3"
    elsewhere = tmp_path / "other" / "file.json"
    assert log_path(elsewhere, data) == "file.json"
    inside_repo = rb.REPO_ROOT / "pipeline" / "README.md"
    assert log_path(inside_repo, data) == "pipeline/README.md"


def test_missing_seed_fails(tmp_path: Path) -> None:
    with pytest.raises(ReleaseError, match="seed not found"):
        build_release(tmp_path, now=NOW)
    assert release_cmd(True, data_dir=tmp_path, now=NOW) == 1


# --- writing -----------------------------------------------------------------------------


def test_existing_release_folder_is_never_overwritten(data_dir: Path) -> None:
    write_release(build_release(data_dir, now=NOW, release=1), data_dir)
    before = (data_dir / "releases" / "1" / "catalogue.json").read_bytes()
    with pytest.raises(ReleaseError, match="already exists"):
        write_release(build_release(data_dir, now=NOW, release=1), data_dir)
    assert (data_dir / "releases" / "1" / "catalogue.json").read_bytes() == before


def test_stale_tmp_folder_is_replaced(data_dir: Path) -> None:
    tmp = data_dir / "releases" / ".tmp-1"
    tmp.mkdir(parents=True)
    (tmp / "leftover.txt").write_text("from a crashed run", encoding="utf-8")
    out = write_release(build_release(data_dir, now=NOW, release=1), data_dir)
    assert not tmp.exists()
    assert not (out / "leftover.txt").exists()
    assert (out / "catalogue.json").exists()


def test_release_cmd_today_sets_the_release_date(data_dir: Path, capsys) -> None:
    assert release_cmd(True, data_dir=data_dir, today=date(2026, 1, 2)) == 0
    log = json.loads(capsys.readouterr().out)
    assert log["at"].startswith("2026-01-02")


def test_release_cmd_reports_write_failure(data_dir: Path, monkeypatch, capsys) -> None:
    def boom(res, d):
        raise ReleaseError("disk says no")

    monkeypatch.setattr(rb, "write_release", boom)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    assert "disk says no" in capsys.readouterr().err


# --- diff --------------------------------------------------------------------------------


def test_diff_first_release_lists_everything_as_added() -> None:
    cur = {"release": 1, "rows": [{"variant_id": "b"}, {"variant_id": "a"}]}
    d = compute_diff(None, cur)
    assert d["previous_release"] is None
    assert d["added"] == ["a", "b"] and d["removed"] == [] and d["changed"] == {}
    assert d["counts"]["rows_previous"] == 0


def test_diff_changed_removed_and_ignored_keys() -> None:
    prev = {
        "release": 4,
        "rows": [
            {"variant_id": "a", "release": 4, "x": 1, "provenance": {"x": 1}, "gone": 5},
            {"variant_id": "b", "release": 4, "x": 1},
            {"variant_id": "c", "release": 4, "x": None},
        ],
    }
    cur = {
        "release": 5,
        "rows": [
            # Only release + provenance changed for "a" besides a dropped field.
            {"variant_id": "a", "release": 5, "x": 1, "provenance": {"x": 2}},
            {"variant_id": "b", "release": 5, "x": 1},
            # A field that appears from nothing counts as changed (None -> value).
            {"variant_id": "c", "release": 5, "x": None, "new_field": [1]},
        ],
    }
    d = compute_diff(prev, cur)
    assert d["removed"] == [] and d["added"] == []
    assert d["changed"] == {
        "a": {"gone": {"old": 5, "new": None}},
        "c": {"new_field": {"old": None, "new": [1]}},
    }
    assert d["counts"]["changed"] == 2


def test_diff_all_removed() -> None:
    prev = {"release": 1, "rows": [{"variant_id": "a"}, {"variant_id": "b"}]}
    d = compute_diff(prev, {"release": 2, "rows": []})
    assert d["removed"] == ["a", "b"]
    assert d["counts"] == {"rows_previous": 2, "rows": 0, "added": 0, "removed": 2, "changed": 0}


# --- licence gate ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("licence", "problem"),
    [
        ("CC-BY-4.0", None),
        ("CC0-1.0 (checked 2026-11)", None),
        ("", "no named licence"),
        ("  N/A  ", "no named licence"),
        ("None given", "no named licence"),
        ("unknown-ish", "no named licence"),
        ("CC-BY-4.0 (unconfirmed)", "licence not confirmed"),
        ("OGL-UK-3.0 (To Confirm)", "licence not confirmed"),
    ],
)
def test_licence_problem(licence: str, problem: str | None) -> None:
    got = licence_problem(licence)
    assert (got is None) if problem is None else got.startswith(problem)


def test_registry_source_object_and_loading(tmp_path: Path) -> None:
    reg = parse_registry(
        {"sources": [{"id": "s", "name": "S", "licence": "CC-BY-4.0 (to confirm)"}]}
    )
    assert reg.source_object("s") == {"id": "s", "name": "S", "licence": "CC-BY-4.0"}
    assert reg.source_object("missing") is None
    assert reg.reason_blocked("s") == "status "  # no status = not active
    assert load_registry(tmp_path / "none.yaml").loaded is False
    empty = tmp_path / "sources.yaml"
    empty.write_text("", encoding="utf-8")
    reg2 = load_registry(empty)
    assert reg2.loaded is True and reg2.sources == {}
    assert reg2.reason_blocked("openev") == "not in data/sources.yaml"


# --- optional taxonomy -------------------------------------------------------------------


def _blocked(sid: str) -> str | None:
    return None if sid == "ok" else "status blocked"


def test_optional_table_shapes_and_gating(tmp_path: Path) -> None:
    tax = tmp_path / "taxonomy"
    tax.mkdir()
    # SYNTHETIC tables: a bare list, a dict with a non-list value, and gated rows.
    (tax / "bidi_modes.yaml").write_text("- {id: v2l}\n- not-a-dict\n", encoding="utf-8")
    (tax / "bidi_routes.yaml").write_text("bidi_routes: oops\n", encoding="utf-8")
    (tax / "bidi_equipment.yaml").write_text(
        "bidi_equipment:\n"
        "  - {id: e1, source_ids: [ok]}\n"
        "  - {id: e2, source_ids: [ok, bad]}\n"
        "  - {id: e3}\n",
        encoding="utf-8",
    )
    out = load_optional_taxonomy(tmp_path, _blocked)
    assert out.tables["bidi_modes"] == [{"id": "v2l"}]
    assert out.tables["bidi_routes"] == []
    assert [r["id"] for r in out.tables["bidi_equipment"]] == ["e1"]
    assert out.held_back["bidi_equipment"] == {
        "e2": "bad: status blocked",
        "e3": "(none): no source",
    }
    assert out.counts() == {"bidi_modes": 1, "bidi_routes": 0, "bidi_equipment": 1}


def test_optional_taxonomy_duplicate_ids_and_missing_tables() -> None:
    tables = {
        "bidi_modes": [{"id": "v2l"}, {"id": "v2l"}],
        "bidi_equipment": [
            {"id": "e1", "mode_ids": "v2l", "route_id": "ac", "compatible_platform_ids": ["x"]}
        ],
        "charging_definitions": [{"id": "d1", "replaced_by": None}],
    }
    errs = optional_taxonomy_errors(tables, {"y"})
    assert "taxonomy bidi_modes: duplicate id v2l" in errs
    assert "taxonomy bidi_equipment e1: route_id needs bidi_routes.yaml" in errs
    assert "taxonomy bidi_equipment e1: unknown platform 'x'" in errs
    assert not any("mode_ids" in e for e in errs)  # a string mode id is accepted


# --- schema and provenance guards --------------------------------------------------------


def test_schema_errors_on_bad_facts_and_cap(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    assert schema_errors(res.catalogue, res.facts) == []
    bad = {"id": "x:1:battery_kwh_net", "field": "battery_kwh_net"}  # no source, value, ...
    errs = schema_errors(res.catalogue, [bad])
    assert any(e.startswith("fact x:1:battery_kwh_net:") for e in errs)
    assert any(e.startswith("pydantic Fact x:1:battery_kwh_net") for e in errs)
    many = schema_errors(res.catalogue, [dict(bad, id=f"x:{i}") for i in range(100)])
    assert 50 < len(many) < 100  # stops collecting after 50 errors


def test_provenance_errors_on_prices_and_empty_sources() -> None:
    row = {
        "variant_id": "v",
        "battery_kwh_net": 60.0,
        "price_new": {"NL": {"amount": 40000, "currency": "EUR"}},
        "provenance": {"battery_kwh_net": {"source_ids": [], "confidence": "low"}},
    }
    assert provenance_errors([row]) == [
        "v: price_new.NL has no provenance",
        "v: provenance battery_kwh_net has no source",
    ]
