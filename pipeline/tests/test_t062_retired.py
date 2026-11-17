"""T-062 pipeline part: retired variant ids never 404 and the map never shrinks."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ev_pipeline.release.retired import compute_retired, has_catalogue_field, load_hand_kept


def _prev(*ids: str) -> dict:
    return {"rows": [{"variant_id": i} for i in ids]}


def test_vanished_ids_map_to_null_or_hand_kept_successor() -> None:
    r = compute_retired(_prev("a", "b", "c"), {}, {"b", "c", "d"}, {})
    assert r.ids == {"a": None} and r.log["new_this_release"] == ["a"]
    r = compute_retired(_prev("a", "b"), {}, {"b", "d"}, {"a": "d"})
    assert r.ids == {"a": "d"} and r.log["with_successor"] == 1


def test_map_never_shrinks_and_chains_resolve() -> None:
    prev_map = {"old1": "a", "old0": None}
    r = compute_retired(_prev("a", "b"), prev_map, {"b", "c"}, {"a": "c"})
    assert r.ids == {"old0": None, "old1": "c", "a": "c"}  # old1 -> a -> c


def test_live_again_leaves_the_map() -> None:
    r = compute_retired(_prev("b"), {"a": "b"}, {"a", "b"}, {})
    assert r.ids == {} and r.log["live_again"] == ["a"]


def test_successor_that_is_not_live_becomes_null() -> None:
    r = compute_retired(_prev("a"), {}, {"z"}, {"a": "ghost"})
    assert r.ids == {"a": None} and r.log["successor_not_live"] == ["a"]
    loop = compute_retired(None, {"x": "y", "y": "x"}, {"z"}, {})
    assert loop.ids == {"x": None, "y": None}


def test_hand_kept_file(tmp_path: Path) -> None:
    assert load_hand_kept(tmp_path) == {}
    (tmp_path / "retired_ids.yaml").write_text("schema: retired-ids/v1\nids:\n  a: b\n  c: null\n")
    assert load_hand_kept(tmp_path) == {"a": "b", "c": None}
    (tmp_path / "retired_ids.yaml").write_text("ids: {a: b}\n")
    with pytest.raises(ValueError, match="schema"):
        load_hand_kept(tmp_path)


def test_schema_switch() -> None:
    assert not has_catalogue_field({"$defs": {"Catalogue": {"properties": {"rows": {}}}}})
    assert has_catalogue_field({"$defs": {"Catalogue": {"properties": {"retired_ids": {}}}}})


def test_release_writes_retired_ids_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from ev_pipeline.release.build import release_cmd

    fix = Path(__file__).parent / "fixtures" / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    now = datetime(2026, 11, 15, 1, tzinfo=UTC)
    assert release_cmd(False, data_dir=d, now=now) == 0
    assert not (d / "releases" / "1" / "retired_ids.json").exists()  # nothing retired yet
    cat1 = json.loads((d / "releases" / "1" / "catalogue.json").read_text())
    gone = cat1["rows"][0]["variant_id"]
    # Pretend release 1 had one more variant that release 2 no longer has.
    cat1["rows"].append({**cat1["rows"][0], "variant_id": "zz-retired-variant"})
    (d / "releases" / "1" / "catalogue.json").write_text(json.dumps(cat1))
    # Re-package so the manifest's sha256 matches (the T-123 release diff checks N-1 by it).
    from ev_pipeline.release.publish import load_config, package

    package(d / "releases" / "1", load_config(d))
    (d / "seed" / "retired_ids.yaml").write_text(
        f"schema: retired-ids/v1\nids:\n  zz-retired-variant: {gone}\n"
    )
    assert release_cmd(False, data_dir=d, now=now) == 0
    doc = json.loads((d / "releases" / "2" / "retired_ids.json").read_text())
    assert doc["retired_ids"] == {"zz-retired-variant": gone} and doc["release"] == 2
