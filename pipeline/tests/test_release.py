"""T-006 release: range checks, numbering, diff, schema validation, licence gate, nyland."""

from __future__ import annotations

import csv
import gzip
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest
import yaml

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.release.build import (
    build_release,
    compute_diff,
    coverage,
    next_release_number,
    release_cmd,
)
from ev_pipeline.release.gate import parse_registry
from ev_pipeline.release.validate import (
    ReleaseError,
    check_fact_ranges,
    excluded_source_errors,
    in_range,
    provenance_errors,
)
from ev_pipeline.schema_models import Fact

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


def _catalogue(d: Path, n: int) -> dict:
    return json.loads((d / "releases" / str(n) / "catalogue.json").read_text())


def _rows(cat: dict) -> dict[str, dict]:
    return {r["variant_id"]: r for r in cat["rows"]}


# --- range checks ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "ok"),
    [
        ("battery_kwh_net", 10, True),
        ("battery_kwh_net", 9.9, False),
        ("battery_kwh_net", 150, True),
        ("battery_kwh_net", 151, False),
        ("wltp_range_km", 79, False),
        ("wltp_range_km", 900, True),
        ("consumption_kwh_100km", 36, False),
        ("ac_kw", 43, True),  # Zoe Q90/R240 charge at 43 kW AC
        ("ac_kw", 44, False),
        ("ac_kw", 1.9, False),
        ("dc_peak_kw", 401, False),
        ("dc_avg_10_80_kw", 9, False),
        ("price_new.NL", 4999, False),
        ("price_new.UK", 250_000, True),
        ("boot_l", 2001, False),
        ("length_mm", 2499, False),
        ("towing_kg", 3501, False),
        ("power_kw", 99999, True),  # no range for this field
    ],
)
def test_range_checks(field: str, value: float, ok: bool) -> None:
    assert in_range(field, value) is ok


def test_out_of_range_fact_is_dropped_and_listed() -> None:
    def mk(field: str, value: float) -> MatchedFact:
        f = Fact(
            id=f"openev:k:{field}",
            subject_type="variant",
            subject_id="x-base",
            field=field,
            value=value,
            unit="kW",
            source={"id": "openev", "name": "o", "licence": "CDLA-Permissive-2.0"},
            source_record="k",
            retrieved_at=date(2026, 11, 14),
            confidence="medium",
        )
        return MatchedFact(f, "openev", 30, 2022)

    keep, dropped = check_fact_ranges([mk("ac_kw", 11), mk("ac_kw", 250)])
    assert [k.fact.value for k in keep] == [11]
    assert dropped[0].field == "ac_kw" and "out of range 2-43" in dropped[0].reason


# --- end to end ----------------------------------------------------------------------------


def test_release_end_to_end(data_dir: Path) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    out = data_dir / "releases" / "1"
    assert sorted(p.name for p in out.iterdir()) == [
        "README.md",
        "catalogue",  # per-generation split (T-064)
        "catalogue.json",
        "catalogue.parquet",
        "consumption_matrix.json",  # Trip fit model (T-033)
        "coverage.md",
        "diff.json",
        "facts.parquet",
        "manifest.json",  # sizes + sha256 of every file (T-064, Decision 035)
        "open",  # open data bundle (Decision 016)
        "qa.json",  # release QA (R-05 §1)
        "qa.md",
        "run_log.json",
        "sources.json",  # source health per source (addendum 6 P3)
        "used_prices.json",  # used price bands per build year (T-081)
    ]
    assert (data_dir / "releases" / "latest").read_text().strip() == "1"
    raw = (out / "catalogue.json").read_bytes()
    cat = json.loads(raw)
    assert raw == json.dumps(cat, separators=(",", ":"), ensure_ascii=False).encode()  # compact
    assert cat["release"] == 1 and cat["generated_at"].startswith("2026-11-15T01:00")
    rows = _rows(cat)
    assert set(rows) == {
        "citroen-e-c4-c41-50-kwh",
        "ford-mustang-mach-e-gen1-extended-range-awd",
        "nissan-leaf-ze0-24kwh",
        "nissan-leaf-ze1-40-kwh",
        "renault-zoe-ph1-q90",
        "tesla-model-3-gen1-lr",
        "tesla-model-3-gen1-performance",
    }
    lr = rows["tesla-model-3-gen1-lr"]
    # WLTP: the earliest model year wins within one source (2022: 602, not 2023: 629; T-005
    # review) and the 4% difference stays one variant (below the 5% year-band split).
    assert lr["battery_kwh_net"] == 75.0 and lr["wltp_range_km"] == 602.0
    assert lr["quality_tier"] == "sourced"
    assert lr["registered_count_nl"] == 3000
    assert lr["price_new"] == {"NL": {"amount": 56990.0, "currency": "EUR"}}
    assert lr["voltage_class_id"] == "400v" and lr["charge_100_daily"] is True
    assert rows["citroen-e-c4-c41-50-kwh"]["consumption_kwh_100km"] == 15.5  # from Wh/km
    assert rows["citroen-e-c4-c41-50-kwh"]["quality_tier"] == "single-source"
    assert rows["renault-zoe-ph1-q90"]["ac_kw"] == 43.0
    assert rows["ford-mustang-mach-e-gen1-extended-range-awd"]["ac_kw"] is None  # 250 dropped
    assert rows["nissan-leaf-ze0-24kwh"]["battery_kwh_net"] == 21.0  # from the pack
    # Numbers rounded to 1 decimal.
    for r in cat["rows"]:
        for k, v in r.items():
            if isinstance(v, float):
                assert round(v, 1) == v, (r["variant_id"], k, v)
    assert provenance_errors(cat["rows"]) == []
    assert {"taxonomy", "platforms", "battery_packs"} <= set(cat)

    # Parquet files.
    t = pq.read_table(out / "catalogue.parquet")
    assert t.num_rows == 7 and "price_new_nl" in t.column_names
    f = pq.read_table(out / "facts.parquet").to_pylist()
    assert {x["source_id"] for x in f} >= {"openev", "eea", "rdw", "seed-manual", "wikidata"}
    # EEA is count-only (Q-039): its spec records in staging never become facts.
    assert {x["field"] for x in f if x["source_id"] == "eea"} == {"registered_count"}
    run_log = json.loads((out / "run_log.json").read_text())
    assert run_log["outputs"]["count_only_spec_records_skipped"] == {"eea": 2}
    # No absolute host paths in the run log (T-006 review): data/... relative paths only.
    assert str(data_dir) not in (out / "run_log.json").read_text()
    assert all(i["path"].startswith("data/") for i in run_log["inputs"]), run_log["inputs"]
    assert any(x["subject_type"] == "battery_pack" for x in f)

    # Review files.
    review = data_dir / "review"
    val = list(csv.DictReader((review / "validation.csv").open()))
    assert any(v["field"] == "ac_kw" and v["value"] == "250.0" for v in val)
    conf = list(csv.DictReader((review / "conflicts.csv").open()))
    assert {(c["variant_id"], c["field"], c["source_id"]) for c in conf} >= {
        ("citroen-e-c4-c41-50-kwh", "battery_kwh_net", "wikidata"),
        ("tesla-model-3-gen1-lr", "wltp_range_km", "openev"),  # 2023's 629 vs 2022's 602
    }
    assert all(c["winning_value"] != c["value"] for c in conf)
    um = list(csv.DictReader((review / "unmatched.csv").open()))
    assert {u["reason"] for u in um} >= {"model not in seed"}

    readme = (out / "README.md").read_text()
    assert "CDLA-Permissive-2.0" in readme and "Contains data from" in readme
    cov = (out / "coverage.md").read_text()
    assert "| battery_kwh_net |" in cov and "2+ agreeing sources" in cov


def test_catalogue_stays_small(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    assert res.catalogue_gzip_bytes == len(
        gzip.compress(
            json.dumps(res.catalogue, separators=(",", ":"), ensure_ascii=False).encode(), mtime=0
        )
    )
    assert res.catalogue_gzip_bytes < 300_000


def test_dry_run_writes_nothing(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert release_cmd(True, data_dir=data_dir, now=NOW) == 0
    assert not (data_dir / "releases").exists()
    assert not (data_dir / "review").exists()
    assert '"rows": 7' in capsys.readouterr().out


def test_release_numbering_and_diff(data_dir: Path) -> None:
    assert next_release_number(data_dir / "releases") == 1
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    d1 = json.loads((data_dir / "releases" / "1" / "diff.json").read_text())
    assert d1["previous_release"] is None and d1["counts"]["added"] == 7

    # Change one input: e-C4 battery 46.3 -> 48 (openev), drop the Zoe variant.
    path = data_dir / "staging" / "openev.records.jsonl"
    lines = path.read_text().splitlines()
    lines = [x.replace('"value": 46.3', '"value": 48.0') for x in lines]
    path.write_text("\n".join(lines) + "\n")
    v = yaml.safe_load((data_dir / "seed" / "variants.yaml").read_text())
    v["variants"] = [x for x in v["variants"] if x["id"] != "renault-zoe-ph1-q90"]
    (data_dir / "seed" / "variants.yaml").write_text(yaml.safe_dump(v))

    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    assert (data_dir / "releases" / "latest").read_text().strip() == "2"
    d2 = json.loads((data_dir / "releases" / "2" / "diff.json").read_text())
    assert d2["previous_release"] == 1
    assert d2["removed"] == ["renault-zoe-ph1-q90"] and d2["added"] == []
    ch = d2["changed"]["citroen-e-c4-c41-50-kwh"]
    assert ch["battery_kwh_net"] == {"old": 46.3, "new": 48.0}
    assert "release" not in ch and "provenance" not in ch
    assert _catalogue(data_dir, 2)["rows"][0]["release"] == 2
    # Rerun numbers onwards and never overwrites.
    assert next_release_number(data_dir / "releases") == 3


def test_compute_diff_counts() -> None:
    prev = {"release": 1, "rows": [{"variant_id": "a", "x": 1}, {"variant_id": "b", "x": 1}]}
    cur = {"release": 2, "rows": [{"variant_id": "b", "x": 2}, {"variant_id": "c", "x": 1}]}
    d = compute_diff(prev, cur)
    assert d["added"] == ["c"] and d["removed"] == ["a"]
    assert d["changed"] == {"b": {"x": {"old": 1, "new": 2}}}
    assert d["counts"] == {"rows_previous": 2, "rows": 2, "added": 1, "removed": 1, "changed": 1}


# --- exclusion and licence gate ----------------------------------------------------------


def _all_text(d: Path, n: int = 1) -> str:
    out = d / "releases" / str(n)
    text = (out / "catalogue.json").read_text() + (out / "README.md").read_text()
    text += json.dumps(pq.read_table(out / "facts.parquet").to_pylist(), default=str)
    text += json.dumps(pq.read_table(out / "catalogue.parquet").to_pylist(), default=str)
    return text


TESTCAR_OPENEV = (
    '{"source": {"id": "openev", "name": "OpenEV Data", "licence": "CDLA-Permissive-2.0"}, '
    '"record_key": "synthetic/testcar-alpha/2024-lr", "kind": "spec", "make": "Testmake", '
    '"model": "Testcar Alpha", "variant_name": "Long Range", "year": 2024, "country": null, '
    '"drivetrain": null, "specs": {"battery_kwh_net": {"value": 70.0, "unit": "kWh"}}, '
    '"retrieved_at": "2026-11-14", "confidence": "medium"}\n'
)
TESTCAR_VID = "testmake-testcar-alpha-gen1-long-range"


def test_nyland_fixture_is_synthetic() -> None:
    # Hard rule: nyland fixtures hold invented "Testcar" rows only, never a real car.
    for line in (FIX / "staging" / "nyland.records.jsonl").read_text().splitlines():
        rec = json.loads(line)
        assert rec["source"]["id"] == "nyland"
        assert rec["make"] == "Testmake" and rec["model"].startswith("Testcar")


def test_nyland_never_reaches_a_release(data_dir: Path) -> None:
    # The nyland record WOULD match: the fixture seed has Testcar Alpha, and an openev record
    # for the same variant makes the row exist. Also smuggle the nyland record into openev's file.
    nyl = (data_dir / "staging" / "nyland.records.jsonl").read_text()
    with (data_dir / "staging" / "openev.records.jsonl").open("a") as fh:
        fh.write(TESTCAR_OPENEV)
        fh.write(nyl)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    text = _all_text(data_dir)
    assert "nyland" not in text.lower()
    row = _rows(_catalogue(data_dir, 1))[TESTCAR_VID]
    assert row["battery_kwh_net"] == 70.0  # openev, not nyland's 72.1
    assert row["real_range_km"] != 412  # nyland's measured value never lands
    assert row.get("real_range_rung") != "measured"
    assert all("nyland" not in p["source_ids"] for p in row["provenance"].values())
    assert "72.1" not in json.dumps(row) and "testcar-alpha-lr-2024" not in text


def test_nyland_record_would_match_without_the_exclusion(data_dir: Path) -> None:
    # Control for the test above: the same record under an allowed source id does match.
    from ev_pipeline.match.matcher import match_records
    from ev_pipeline.match.seed import load_seed
    from ev_pipeline.records import SourceRecord

    rec = json.loads((data_dir / "staging" / "nyland.records.jsonl").read_text())
    rec["source"] = {"id": "openev", "name": "o", "licence": "CDLA-Permissive-2.0"}
    res = match_records([SourceRecord.model_validate(rec)], load_seed(FIX / "models.yaml"))
    assert TESTCAR_VID in res.variants


def test_missing_registry_fails_the_release(data_dir: Path) -> None:
    # Fail closed (T-006 review): no data/sources.yaml means no release at all.
    (data_dir / "sources.yaml").unlink()
    with (data_dir / "staging" / "openev.records.jsonl").open("a") as fh:
        fh.write((data_dir / "staging" / "nyland.records.jsonl").read_text())
    with pytest.raises(ReleaseError, match="no data/sources.yaml"):
        build_release(data_dir, now=NOW)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    assert not (data_dir / "releases").exists()
    reg = parse_registry({"sources": []})
    reg.loaded = False
    assert not reg.releasable("openev") and not reg.releasable("nyland")


def test_guard_rejects_injected_excluded_source() -> None:
    cat = {
        "sources": [{"id": "nyland", "name": "n", "licence": "none"}],
        "rows": [
            {
                "variant_id": "x",
                "provenance": {"real_range_km": {"source_ids": ["nyland"], "confidence": "high"}},
            }
        ],
    }
    errs = excluded_source_errors(cat, [{"id": "nyland:k:f", "source": {"id": "nyland"}}])
    assert len(errs) == 3


def test_registry_gate_rules() -> None:
    reg = parse_registry(
        {
            "sources": [
                {"id": "openev", "licence": "CDLA-Permissive-2.0", "status": "active"},
                {"id": "eea", "licence": "CC-BY-4.0 (to confirm)", "status": "active"},
                {"id": "fastned", "licence": "none", "status": "waiting_permission"},
                {"id": "kba", "licence": "unknown (to confirm)", "status": "blocked"},
                {"id": "nolicence", "licence": "none", "status": "active"},
                {"id": "unknownlic", "licence": "unknown", "status": "active"},
                {"id": "permitted", "licence": "none", "status": "active", "permission": "written"},
                {
                    "id": "pending",
                    "licence": "none",
                    "status": "waiting_permission",
                    "permission": "written",
                },
                {"id": "nyland", "licence": "CC0-1.0", "status": "active", "permission": "written"},
            ]
        }
    )
    assert reg.releasable("openev")
    # "(to confirm)" no longer passes on an active source (matches data/sources.yaml's rule).
    assert reg.reason_blocked("eea").startswith("licence not confirmed")
    assert reg.reason_blocked("fastned") == "status waiting_permission"
    assert reg.reason_blocked("kba") == "status blocked"
    assert reg.reason_blocked("nolicence").startswith("no named licence")
    assert reg.reason_blocked("unknownlic").startswith("no named licence")
    assert reg.releasable("permitted")  # explicit written permission is the only override
    assert reg.reason_blocked("pending") == "status waiting_permission"  # status still applies
    assert reg.reason_blocked("unlisted") == "not in data/sources.yaml"
    assert not reg.releasable("nyland")  # hard exclusion beats the registry


def test_real_registry_has_no_written_permission_tonight() -> None:
    real = yaml.safe_load((FIX.parents[2].parent / "data" / "sources.yaml").read_text())
    assert all(s.get("permission") is None for s in real["sources"])
    reg = parse_registry(real)
    for s in real["sources"]:
        lic = str(s.get("licence", "")).lower()
        if "to confirm" in lic or lic.startswith(("none", "unknown")):
            assert not reg.releasable(s["id"]), s["id"]


def test_non_active_source_is_gated(data_dir: Path) -> None:
    reg = yaml.safe_load((data_dir / "sources.yaml").read_text())
    for s in reg["sources"]:
        if s["id"] in ("eea", "wikidata"):
            s["status"] = "waiting_permission"
    (data_dir / "sources.yaml").write_text(yaml.safe_dump(reg))
    res = build_release(data_dir, now=NOW)
    assert res.gated["eea"]["reason"] == "status waiting_permission"
    assert res.gated["eea"]["records"] == 3
    assert res.gated["wikidata"]["records"] == 2
    for sid in ("eea", "wikidata"):
        assert sid not in json.dumps(res.catalogue)
        assert all(f["source"]["id"] != sid for f in res.facts)
    # Without wikidata nothing confirms the Model 3 battery: tier falls back.
    rows = _rows(res.catalogue)
    assert rows["tesla-model-3-gen1-lr"]["quality_tier"] == "single-source"


# --- validation failures -----------------------------------------------------------------


def test_unknown_taxonomy_id_fails_release(data_dir: Path) -> None:
    p = data_dir / "seed" / "battery_packs.yaml"
    p.write_text(p.read_text().replace("chemistry_id: nmc", "chemistry_id: unobtainium"))
    with pytest.raises(ReleaseError, match="unknown chemistry id 'unobtainium'"):
        build_release(data_dir, now=NOW)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    assert not (data_dir / "releases").exists()


def test_not_disclosed_is_allowed(data_dir: Path) -> None:
    p = data_dir / "seed" / "battery_packs.yaml"
    p.write_text(p.read_text().replace("chemistry_id: nmc", "chemistry_id: not-disclosed"))
    res = build_release(data_dir, now=NOW)
    assert _rows(res.catalogue)["nissan-leaf-ze0-24kwh"]["chemistry_id"] == "not-disclosed"
    # Schema workaround (Q-017): the shipped pack leaves the oneOf-ambiguous key out.
    pack = next(p for p in res.catalogue["battery_packs"] if p["id"] == "nissan-24-air")
    assert pack["chemistry_id"] == "not-disclosed"  # Q-017 fixed: ships as-is


def test_missing_taxonomy_is_skipped_and_ids_not_published(data_dir: Path) -> None:
    shutil.rmtree(data_dir / "taxonomy")
    for n in ("platforms", "battery_packs", "variant_links"):
        (data_dir / "seed" / f"{n}.yaml").unlink()
    res = build_release(data_dir, now=NOW)
    assert "taxonomy" not in res.catalogue
    assert all("chemistry_id" not in r for r in res.catalogue["rows"])


def test_schema_violation_fails_release(data_dir: Path, monkeypatch) -> None:
    import ev_pipeline.release.build as build

    real = build.build_rows

    def broken(*a, **kw):
        rows, problems = real(*a, **kw)
        rows[0]["era"] = "stone-age"
        return rows, problems

    monkeypatch.setattr(build, "build_rows", broken)
    with pytest.raises(ReleaseError, match="era"):
        build_release(data_dir, now=NOW)


def test_missing_provenance_fails_release(data_dir: Path, monkeypatch) -> None:
    import ev_pipeline.release.build as build

    real = build.build_rows

    def broken(*a, **kw):
        rows, problems = real(*a, **kw)
        for r in rows:
            r["provenance"].pop("battery_kwh_net", None)
        return rows, problems

    monkeypatch.setattr(build, "build_rows", broken)
    with pytest.raises(ReleaseError, match="battery_kwh_net has no provenance"):
        build_release(data_dir, now=NOW)


def test_every_number_has_provenance_on_real_fixture(data_dir: Path) -> None:
    res = build_release(data_dir, now=NOW)
    for r in res.catalogue["rows"]:
        for k, v in r.items():
            if k in ("release", "year_start", "year_end"):
                continue  # identity fields: from the seed, not facts
            if isinstance(v, int | float) and not isinstance(v, bool):
                assert k in r["provenance"], (r["variant_id"], k)
        for p in r["provenance"].values():
            assert p["source_ids"] and p["confidence"] in ("high", "medium", "low")


def test_coverage_buckets() -> None:
    rows = [
        {"battery_kwh_net": 1, "provenance": {"battery_kwh_net": {"agreeing_sources": 2}}},
        {"battery_kwh_net": 1, "provenance": {"battery_kwh_net": {"agreeing_sources": 1}}},
        {"battery_kwh_net": 1, "provenance": {"battery_kwh_net": {"estimate": True}}},
        {"battery_kwh_net": None, "provenance": {}},
    ]
    c = coverage(rows)["battery_kwh_net"]
    assert c == {"2+ agreeing sources": 1, "1 source": 1, "estimate only": 1, "missing": 1}
