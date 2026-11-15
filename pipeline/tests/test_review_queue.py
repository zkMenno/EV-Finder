"""P7 review queue: stable review_id + status on data/review/*.csv, durable status.yaml."""

from __future__ import annotations

import csv
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from ev_pipeline.release.build import release_cmd
from ev_pipeline.review_queue import (
    annotate_review_dir,
    load_status,
    review_id,
    snapshot_statuses,
)

TODAY = date(2026, 11, 15)
RELEASE_FIX = Path(__file__).parent / "fixtures" / "release"

UM_HEADER = ["source_id", "record_key", "make", "model", "variant_name", "year", "reason"]


def _write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _unmatched(d: Path, n: int = 4) -> None:
    _write(
        d / "unmatched.csv",
        UM_HEADER,
        [
            ["ademe", "k1", "AUDI", "E-TRON GT", "", "", f"model not in seed ({n}x)"],
            ["rdw", "(summary)", "LYNK", "", "", "", f"make not in seed: {n * 10} records"],
            ["rdw", "(summary)", "XPENG", "", "", "", f"make not in seed: {n} records"],
        ],
    )


def test_ids_are_stable_short_and_ignore_counts(tmp_path: Path) -> None:
    _unmatched(tmp_path, 4)
    annotate_review_dir(tmp_path, today=TODAY)
    first = _read(tmp_path / "unmatched.csv")
    assert list(first[0])[:2] == ["review_id", "status"]
    assert all(r["status"] == "open" for r in first)
    ids = [r["review_id"] for r in first]
    assert len(set(ids)) == 3 and all(i.startswith("um-") and len(i) == 13 for i in ids)
    _unmatched(tmp_path, 7)  # counts changed, same problems
    annotate_review_dir(tmp_path, today=TODAY)
    assert [r["review_id"] for r in _read(tmp_path / "unmatched.csv")] == ids
    annotate_review_dir(tmp_path, today=TODAY)  # idempotent on an annotated file
    again = _read(tmp_path / "unmatched.csv")
    assert [r["review_id"] for r in again] == ids and list(again[0]).count("review_id") == 1


def test_review_id_is_hash_of_source_key_reason() -> None:
    a = review_id("va", "openev", "k", "out of range")
    assert a == review_id("va", "openev", "k", "out of range")
    assert a != review_id("va", "openev", "k", "other reason")
    assert a != review_id("va", "rdw", "k", "out of range")


def test_identical_rows_get_suffixes(tmp_path: Path) -> None:
    row = ["unit", "eea", "k", "v1", "ac_kw", "1", "kW", "bad"]
    header = ["stage", "source_id", "record_key", "subject_id", "field", "value", "unit", "reason"]
    _write(tmp_path / "validation.csv", header, [row, row])
    annotate_review_dir(tmp_path, today=TODAY)
    ids = [r["review_id"] for r in _read(tmp_path / "validation.csv")]
    assert ids[1] == ids[0] + "~2" and ids[0].startswith("va-")


def test_csv_edit_survives_rebuild_via_status_yaml(tmp_path: Path) -> None:
    _unmatched(tmp_path)
    annotate_review_dir(tmp_path, today=TODAY)
    rows = _read(tmp_path / "unmatched.csv")
    rows[0]["status"] = "done"
    rows[1]["status"] = "wont-fix"
    rows[2]["status"] = "nonsense"
    _write(tmp_path / "unmatched.csv", list(rows[0]), [list(r.values()) for r in rows])
    done_id, wont_id = rows[0]["review_id"], rows[1]["review_id"]

    prev = snapshot_statuses(tmp_path)  # what the release does before rewriting
    _unmatched(tmp_path, 9)  # the rebuild writes plain CSVs again
    counts = annotate_review_dir(tmp_path, prev, today=TODAY)
    new = {r["review_id"]: r["status"] for r in _read(tmp_path / "unmatched.csv")}
    assert new[done_id] == "done" and new[wont_id] == "wont-fix"
    assert list(new.values()).count("open") == 1  # the invalid value is ignored
    assert counts["unmatched"] == {"rows": 3, "open": 1, "done": 1, "wont-fix": 1}
    st = load_status(tmp_path)
    assert st[done_id]["status"] == "done" and st[done_id]["file"] == "unmatched"
    assert st[done_id]["updated"] == "2026-11-15" and "AUDI" in st[done_id]["summary"]

    # A rebuild without that row keeps the decision; when it comes back, so does the status.
    _write(tmp_path / "unmatched.csv", UM_HEADER, [])
    counts = annotate_review_dir(tmp_path, snapshot_statuses(tmp_path), today=TODAY)
    assert counts["status_yaml_not_in_csvs"] == 2 and done_id in load_status(tmp_path)
    _unmatched(tmp_path)
    annotate_review_dir(tmp_path, snapshot_statuses(tmp_path), today=TODAY)
    assert {r["review_id"]: r["status"] for r in _read(tmp_path / "unmatched.csv")}[
        done_id
    ] == "done"


def test_status_yaml_edit_is_applied(tmp_path: Path) -> None:
    _unmatched(tmp_path)
    annotate_review_dir(tmp_path, today=TODAY)
    rid = _read(tmp_path / "unmatched.csv")[2]["review_id"]
    (tmp_path / "status.yaml").write_text(
        yaml.safe_dump({"schema": "review-status/v1", "items": {rid: {"status": "done"}}})
    )
    # The CSV still says "open" (the last build wrote that): it must not undo the yaml edit.
    prev = snapshot_statuses(tmp_path)
    annotate_review_dir(tmp_path, prev, today=TODAY)
    assert {r["review_id"]: r["status"] for r in _read(tmp_path / "unmatched.csv")}[rid] == "done"
    assert load_status(tmp_path)[rid]["status"] == "done"
    # Reopening in the CSV works too: it differs from what the build wrote ("done").
    rows = _read(tmp_path / "unmatched.csv")
    for r in rows:
        if r["review_id"] == rid:
            r["status"] = "open"
    _write(tmp_path / "unmatched.csv", list(rows[0]), [list(r.values()) for r in rows])
    annotate_review_dir(tmp_path, snapshot_statuses(tmp_path), today=TODAY)
    assert load_status(tmp_path)[rid]["status"] == "open"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(RELEASE_FIX / "staging", d / "staging")
    shutil.copytree(RELEASE_FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / f"{n}.yaml")
    return d


def test_release_writes_ids_and_keeps_decisions(data_dir: Path) -> None:
    now = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)
    assert release_cmd(False, data_dir=data_dir, now=now) == 0
    review = data_dir / "review"
    for name in ("unmatched", "validation", "conflicts"):
        rows = _read(review / f"{name}.csv")
        assert all(r["review_id"] and r["status"] == "open" for r in rows), name
    conf = _read(review / "conflicts.csv")
    conf[0]["status"] = "wont-fix"
    _write(review / "conflicts.csv", list(conf[0]), [list(r.values()) for r in conf])
    assert release_cmd(False, data_dir=data_dir, now=now) == 0
    again = {r["review_id"]: r["status"] for r in _read(review / "conflicts.csv")}
    assert again[conf[0]["review_id"]] == "wont-fix"
    assert load_status(review)[conf[0]["review_id"]]["status"] == "wont-fix"
