"""T-123: release diff N vs N-1 with approved changes (fixtures: tests/fixtures/release_diff)."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

from ev_pipeline.release.differ import (
    CONFIG_FILE,
    DiffConfigError,
    diff_releases,
    flatten,
    load_config,
    parse_config,
    release_diff_check,
    summary,
    summary_md,
    write_csv,
)

FIX = Path(__file__).parent / "fixtures" / "release_diff"
APPROVE_A = {
    "release": 2,
    "file": "catalogue.json",
    "id": "a",
    "field": "wltp_range_km",
    "change": "changed",
    "reason": "test: new WLTP homologation",
    "approved_by": "Decision 061",
}


def cfg(approved: list[dict[str, Any]] | None = None, **over: Any) -> Any:
    doc = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    doc["approved"] = approved or []
    doc.update(over)
    return parse_config(doc, "test")


def by_key(res: Any) -> dict[tuple[str, str, str], Any]:
    return {(c.file, c.id, c.field or c.kind): c for c in res.changes}


def test_repo_config_loads() -> None:
    c = load_config()
    assert c.path == "config/approved_changes.yaml" and len(c.sha256) == 64
    assert c.threshold("catalogue.json", "wltp_range_km") is not None
    assert c.threshold("catalogue.json", "registered_count_nl") is None  # review only


def test_fixture_releases_one_approved_one_unapproved_one_removal() -> None:
    res = diff_releases(FIX / "1", FIX / "2", cfg([APPROVE_A]))
    k = by_key(res)
    a = k[("catalogue.json", "a", "wltp_range_km")]
    assert (a.old, a.new, a.status, a.approval) == (400, 430, "approved", "#0 Decision 061")
    b = k[("catalogue.json", "b", "wltp_range_km")]
    assert (b.old, b.new, b.status) == (300, 330, "blocking")
    assert "rel 0.05" in b.rule
    assert k[("catalogue.json", "c", "removed")].status == "blocking"
    assert k[("catalogue.json", "d", "added")].status == "review"
    assert {(c.file, c.id) for c in res.blocking} == {
        ("catalogue.json", "b"),
        ("catalogue.json", "c"),
    }


def test_noise_is_ignored() -> None:
    res = diff_releases(FIX / "1", FIX / "2", cfg([APPROVE_A]))
    fields = {(c.file, c.field) for c in res.changes}
    # 60 -> 60.0001 and 200 -> 200.0004 are below the precision; key order, generated_at,
    # release, provenance order and plain-list order (list_source_ids) are not changes.
    assert ("catalogue.json", "battery_kwh_net") not in fields
    assert not any(f.startswith("consumption_matrix.json") for f, _ in fields)
    assert not any(c.records == "generations" for c in res.changes)
    assert not any("list_source_ids" in c.field for c in res.changes)
    assert not any(c.field in ("release", "generated_at") for c in res.changes)


def test_review_changes_under_threshold_and_unthresholded() -> None:
    k = by_key(diff_releases(FIX / "1", FIX / "2", cfg([APPROVE_A])))
    s = k[("shortlist_scores.json", "a", "scores.commuter/home/town.score")]
    assert (s.old, s.new, s.status) == (70, 72, "review")  # 2 points < abs 10
    p = k[("used_prices.json", "a", "bands.NL[2021].median")]
    assert p.status == "review"  # +2.5 % < 15 %
    t = k[("towns/NL.json", "s1", "jan_mean_c")]
    assert t.status == "review"  # 0.5 °C < 1.0


def test_charging_goes_through_same_report_review_only() -> None:
    k = by_key(diff_releases(FIX / "1", FIX / "2", cfg()))
    ch = [c for (f, _, _), c in k.items() if f == "charging_stats.json"]
    assert len(ch) == 1 and ch[0].kind == "charging" and ch[0].status == "review"
    assert ch[0].reason.startswith("revised")


def test_threshold_beyond_both_abs_and_rel() -> None:
    c = cfg()
    t = c.threshold("catalogue.json", "battery_kwh_net")  # rel 0.03, abs 1.0
    from ev_pipeline.release.differ import _beyond

    assert not _beyond(t, 20.0, 20.9)  # 4.5 % but under 1 kWh
    assert not _beyond(t, 80.0, 81.5)  # 1.5 kWh but under 3 %
    assert _beyond(t, 60.0, 62.0)
    assert not _beyond(t, "a", "b")  # text under a rel/abs rule: review


def test_cleared_thresholded_value_blocks_filled_does_not(tmp_path: Path) -> None:
    old, new = tmp_path / "1", tmp_path / "2"
    shutil.copytree(FIX / "1", old)
    shutil.copytree(FIX / "1", new)
    cat = json.loads((new / "catalogue.json").read_text())
    cat["rows"][0]["wltp_range_km"] = None
    cat["rows"][0]["provenance"].pop("wltp_range_km")
    cat["rows"][1]["epa_range_km"] = 280.0
    (new / "catalogue.json").write_text(json.dumps(cat))
    k = by_key(diff_releases(old, new, cfg()))
    assert k[("catalogue.json", "a", "wltp_range_km")].kind == "cleared"
    assert k[("catalogue.json", "a", "wltp_range_km")].status == "blocking"
    assert k[("catalogue.json", "b", "epa_range_km")].status == "review"


def test_number_losing_its_source_blocks(tmp_path: Path) -> None:
    old, new = tmp_path / "1", tmp_path / "2"
    shutil.copytree(FIX / "1", old)
    shutil.copytree(FIX / "1", new)
    cat = json.loads((new / "catalogue.json").read_text())
    cat["rows"][0]["provenance"]["battery_kwh_net"]["source_ids"] = []
    (new / "catalogue.json").write_text(json.dumps(cat))
    up = json.loads((new / "used_prices.json").read_text())
    up["variants"][0]["bands"]["NL"][0].pop("list_source_ids")
    (new / "used_prices.json").write_text(json.dumps(up))
    res = diff_releases(old, new, cfg())
    lost = {(c.file, c.field) for c in res.changes if c.kind == "source_lost"}
    assert lost == {("catalogue.json", "battery_kwh_net"), ("used_prices.json", "bands.NL[2021]")}
    assert all(c.status == "blocking" for c in res.changes if c.kind == "source_lost")


def test_source_switch_is_not_source_lost(tmp_path: Path) -> None:
    """samples band -> model band: `source` goes, `list_source_ids` comes (same parent)."""
    old, new = tmp_path / "1", tmp_path / "2"
    shutil.copytree(FIX / "1", old)
    shutil.copytree(FIX / "1", new)
    for d, band in ((old, {"source": "marktplaats"}), (new, {"list_source_ids": ["rdw"]})):
        up = json.loads((d / "used_prices.json").read_text())
        b = up["variants"][0]["bands"]["NL"][0]
        b.pop("list_source_ids")
        b.update(band)
        (d / "used_prices.json").write_text(json.dumps(up))
    assert not [c for c in diff_releases(old, new, cfg()).changes if c.kind == "source_lost"]


def test_retired_ids_make_removal_non_blocking(tmp_path: Path) -> None:
    new = tmp_path / "2"
    shutil.copytree(FIX / "2", new)
    (new / "retired_ids.json").write_text(json.dumps({"retired_ids": {"c": "d"}}))
    k = by_key(diff_releases(FIX / "1", new, cfg([APPROVE_A])))
    c = k[("catalogue.json", "c", "removed")]
    assert c.status == "retired" and c.reason == "retired_ids -> d"


def test_file_removed_blocks(tmp_path: Path) -> None:
    new = tmp_path / "2"
    shutil.copytree(FIX / "2", new)
    (new / "shortlist_scores.json").unlink()
    k = by_key(diff_releases(FIX / "1", new, cfg([APPROVE_A])))
    assert k[("shortlist_scores.json", "", "file_removed")].status == "blocking"


def test_new_file_is_skipped_not_blocking(tmp_path: Path) -> None:
    old = tmp_path / "1"
    shutil.copytree(FIX / "1", old)
    (old / "used_prices.json").unlink()
    res = diff_releases(old, FIX / "2", cfg([APPROVE_A]))
    assert {"file": "used_prices.json", "reason": "new in this release"} in res.skipped
    assert not [c for c in res.changes if c.file == "used_prices.json"]


def test_approval_scope_release_kind_and_stale() -> None:
    other_release = {**APPROVE_A, "release": 3}
    res = diff_releases(FIX / "1", FIX / "2", cfg([other_release]))
    assert by_key(res)[("catalogue.json", "a", "wltp_range_km")].status == "blocking"
    assert res.stale_approvals == []  # not live for release 2
    wrong_kind = {**APPROVE_A, "change": "removed"}
    res = diff_releases(FIX / "1", FIX / "2", cfg([wrong_kind]))
    assert by_key(res)[("catalogue.json", "a", "wltp_range_km")].status == "blocking"
    assert [s["index"] for s in res.stale_approvals] == [0]
    bulk = {"release": [2], "id": "*", "reason": "test: re-match", "approved_by": "PR #77"}
    res = diff_releases(FIX / "1", FIX / "2", cfg([bulk]))
    assert res.blocking == []


@pytest.mark.parametrize(
    "entry, msg",
    [
        ({"approved_by": "PR #1"}, "reason is required"),
        ({"reason": "x", "approved_by": "Menno said so"}, "approved_by"),
        ({"reason": "x", "approved_by": "PR #1", "change": "moved"}, "change must be"),
        ({"reason": "x", "approved_by": "PR #1", "release": "2"}, "release must be"),
    ],
)
def test_bad_approval_entries_are_rejected(entry: dict[str, Any], msg: str) -> None:
    with pytest.raises(DiffConfigError, match=msg):
        cfg([entry])


def test_bad_threshold_and_schema_rejected() -> None:
    with pytest.raises(DiffConfigError, match="rel, abs or any"):
        cfg(thresholds=[{"file": "x", "field": "y"}])
    with pytest.raises(DiffConfigError, match="schema"):
        parse_config({"schema": "nope"})


def test_flatten_keys_lists_and_sorts_plain_lists() -> None:
    flat = flatten(
        {"b": [{"build_year": 2021, "x": 1.23456}], "s": ["z", "a"], "provenance": {"q": 1}},
        frozenset({"provenance"}),
        3,
    )
    assert flat == {"b[2021].build_year": 2021, "b[2021].x": 1.235, "s": '["a", "z"]'}


def test_csv_and_summary(tmp_path: Path) -> None:
    res = diff_releases(FIX / "1", FIX / "2", cfg([APPROVE_A]))
    path = tmp_path / "release_diff.csv"
    write_csv(res, path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows[0]["status"] == "blocking"  # blocking first
    s = summary(res)
    assert s["status"] == "fail" and s["counts"]["blocking"] == 2
    assert s["files"]["catalogue.json:rows"]["removed"] == 1
    assert s["biggest_moves"][0]["field"] == "jan_mean_c"  # 3.0 -> 3.5 °C = +16.7 %
    md = "\n".join(summary_md(s))
    assert "Release diff 1 -> 2" in md and "Blocking" in md


def _data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    for n in ("1", "2"):
        shutil.copytree(FIX / n, d / "releases" / n)
    return d


def test_qa_check_blocks_then_passes_with_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = _data_dir(tmp_path)
    check, res = release_diff_check(d, d / "releases" / "2", 2)
    assert check.blocking and check.status == "fail" and res is not None
    assert (d / "review" / "release_diff.csv").exists()
    doc = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    doc["approved"] = [
        APPROVE_A,
        {"release": 2, "id": "b", "reason": "test: b re-tested", "approved_by": "PR #5"},
        {"release": 2, "id": "c", "change": "removed", "reason": "test", "approved_by": "PR #5"},
    ]
    p = tmp_path / "approved.yaml"
    p.write_text(yaml.safe_dump(doc))
    monkeypatch.setenv("EV_RELEASE_DIFF_CONFIG", str(p))
    check, _ = release_diff_check(d, d / "releases" / "2", 2)
    assert check.status == "pass", check.details["blocking"]


def test_qa_check_first_release_skipped_and_bad_config_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = _data_dir(tmp_path)
    check, _ = release_diff_check(d, d / "releases" / "1", 1)
    assert check.status == "skipped"
    p = tmp_path / "bad.yaml"
    p.write_text("schema: approved-changes/v1\napproved: [{approved_by: nobody}]\n")
    monkeypatch.setenv("EV_RELEASE_DIFF_CONFIG", str(p))
    check, _ = release_diff_check(d, d / "releases" / "2", 2)
    assert check.status == "fail" and "cannot diff" in check.summary  # fail closed


def test_cli_diff_from_to_writes_csv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ev_pipeline.cli import main

    d = _data_dir(tmp_path)
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    assert main(["release", "diff", "--from", "1", "--to", "2"]) == 0
    out = capsys.readouterr().out
    assert "Release 1 -> 2" in out and "Release diff 1 -> 2 (T-123)" in out
    assert (d / "review" / "release_diff.csv").exists()
    assert main(["release", "diff", "1", "2", "--check"]) == 2  # unapproved changes
    assert main(["release", "diff", "1"]) == 1
