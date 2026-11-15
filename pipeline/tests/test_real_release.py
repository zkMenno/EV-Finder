"""Reviewer checks on the real, committed release (data/releases/latest).

These read the published files only (no network, no pipeline run). They are skipped when no
release is committed. Added by the T-005/006/007 review, 2026-11-15.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import pytest
import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[2]
RELEASES = REPO / "data" / "releases"
SCHEMA = REPO / "packages" / "schema" / "schemas" / "ev.schema.json"
SOURCES = REPO / "data" / "sources.yaml"

# Row keys that are numbers but are not data values (ids, years, release number).
NON_DATA_NUMBERS = {"release", "year_start", "year_end"}
NO_LICENCE = {"", "none", "unknown", "n/a"}


def _release_dir() -> Path:
    latest = RELEASES / "latest"
    if not latest.exists():
        pytest.skip("no committed release")
    return RELEASES / latest.read_text().strip()


@pytest.fixture(scope="module")
def release_dir() -> Path:
    return _release_dir()


@pytest.fixture(scope="module")
def catalogue(release_dir: Path) -> dict[str, Any]:
    return json.loads((release_dir / "catalogue.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rows(catalogue: dict[str, Any]) -> list[dict[str, Any]]:
    return catalogue["rows"]


@pytest.fixture(scope="module")
def facts(release_dir: Path) -> dict[str, dict[str, Any]]:
    return {f["id"]: f for f in pq.read_table(release_dir / "facts.parquet").to_pylist()}


def _is_number(v: object) -> bool:
    return isinstance(v, int | float) and not isinstance(v, bool)


def test_release_matches_schema(catalogue: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    schema = {**schema, "$ref": "#/$defs/Catalogue"}
    errors = [
        f"{'/'.join(map(str, e.path))}: {e.message}"
        for e in Draft202012Validator(schema).iter_errors(catalogue)
    ]
    assert errors == []


def test_every_number_has_provenance(rows: list[dict[str, Any]]) -> None:
    """Every non-null number in every row (any key, not only a fixed list) is traced."""
    missing: list[str] = []
    for row in rows:
        prov = row.get("provenance") or {}
        for k, v in row.items():
            if k in NON_DATA_NUMBERS or not _is_number(v):
                continue
            if k not in prov:
                missing.append(f"{row['variant_id']}.{k}")
        for cc, money in (row.get("price_new") or {}).items():
            if _is_number(money.get("amount")) and f"price_new.{cc}" not in prov:
                missing.append(f"{row['variant_id']}.price_new.{cc}")
        # Nested registration counts: one provenance entry per country naming every source.
        for cc, entries in (row.get("registrations") or {}).items():
            p = prov.get(f"registrations.{cc}")
            if p is None:
                missing.append(f"{row['variant_id']}.registrations.{cc}")
                continue
            for e in entries:
                if _is_number(e.get("count")) and e.get("source_id") not in p["source_ids"]:
                    missing.append(f"{row['variant_id']}.registrations.{cc}.{e.get('source_id')}")
    assert missing == []


def test_every_provenance_entry_names_a_source_and_confidence(
    catalogue: dict[str, Any], rows: list[dict[str, Any]]
) -> None:
    listed = {s["id"] for s in catalogue["sources"]}
    bad: list[str] = []
    for row in rows:
        for k, p in (row.get("provenance") or {}).items():
            if not p.get("source_ids") or p.get("confidence") not in {"high", "medium", "low"}:
                bad.append(f"{row['variant_id']}.{k}: empty source or confidence")
            for sid in p.get("source_ids", []):
                if sid not in listed:
                    bad.append(f"{row['variant_id']}.{k}: source {sid} not in catalogue.sources")
    assert bad == []


def test_fact_ids_resolve_to_published_facts(
    rows: list[dict[str, Any]], facts: dict[str, dict[str, Any]]
) -> None:
    unresolved = sorted(
        {
            fid
            for row in rows
            for p in (row.get("provenance") or {}).values()
            for fid in p.get("fact_ids", []) or []
            if fid not in facts
        }
    )
    assert unresolved == [], f"{len(unresolved)} fact ids not in facts.parquet: {unresolved[:10]}"


def test_every_released_source_is_active_with_a_named_licence(
    catalogue: dict[str, Any], facts: dict[str, dict[str, Any]]
) -> None:
    reg = {s["id"]: s for s in yaml.safe_load(SOURCES.read_text(encoding="utf-8"))["sources"]}
    used = {s["id"] for s in catalogue["sources"]} | {f["source_id"] for f in facts.values()}
    bad: list[str] = []
    for sid in sorted(used):
        entry = reg.get(sid)
        if entry is None:
            bad.append(f"{sid}: not in data/sources.yaml")
            continue
        lic = str(entry.get("licence") or "").strip()
        if entry.get("status") != "active":
            bad.append(f"{sid}: status {entry.get('status')}")
        if lic.lower() in NO_LICENCE or "to confirm" in lic.lower():
            bad.append(f"{sid}: licence not named/confirmed ({lic})")
    for s in catalogue["sources"]:
        if not s.get("licence"):
            bad.append(f"{s['id']}: no licence in catalogue.sources")
    assert bad == []


def test_no_nyland_anywhere_in_the_release(release_dir: Path) -> None:
    for path in sorted(release_dir.iterdir()):
        blob = path.read_bytes().lower()
        for needle in (b"nyland", b"bj\xc3\xb8rn", b"bjorn"):
            assert needle not in blob, f"{needle!r} found in {path.name}"


def test_real_range_always_names_its_rung(rows: list[dict[str, Any]]) -> None:
    rungs = {"owner-data", "exact-test", "sibling-variant", "brand-body-drivetrain-ratio",
             "body-ratio"}  # fmt: skip
    bad = [
        r["variant_id"]
        for r in rows
        if (r.get("real_range_km") is None) != (r.get("real_range_rung") is None)
        or (r.get("real_range_rung") is not None and r["real_range_rung"] not in rungs)
    ]
    assert bad == []
    # Estimated rungs must be labelled as estimates.
    for r in rows:
        if r.get("real_range_rung") in {"sibling-variant", "brand-body-drivetrain-ratio",
                                        "body-ratio"}:  # fmt: skip
            assert r["provenance"]["real_range_km"].get("estimate") is True, r["variant_id"]


def _close(a: float, b: float, rel: float = 0.02, abs_: float = 0.15) -> bool:
    return abs(a - b) <= max(abs_, rel * abs(b))


def test_ac_km_per_h_formula(rows: list[dict[str, Any]]) -> None:
    """AC km/h = AC kW / consumption x 100 (brief)."""
    bad = []
    for r in rows:
        if r.get("ac_km_per_h") is None:
            continue
        expect = r["ac_kw"] / r["consumption_kwh_100km"] * 100
        if not _close(r["ac_km_per_h"], expect):
            bad.append((r["variant_id"], r["ac_km_per_h"], round(expect, 1)))
    assert bad == []


def test_dc_km_in_n_minutes_uses_motorway_consumption(rows: list[dict[str, Any]]) -> None:
    """km in N min = dc_avg x N/60 / motorway consumption x 100, capped at 10-80 % (Dec. 009)."""
    bad = []
    for r in rows:
        mway = r.get("consumption_motorway_kwh_100km")
        for minutes, key in ((10, "dc_km_per_10min"), (20, "dc_km_per_20min")):
            if r.get(key) is None:
                continue
            assert mway, f"{r['variant_id']}: {key} without motorway consumption"
            kwh = r["dc_avg_10_80_kw"] * minutes / 60
            if r.get("battery_kwh_net"):
                kwh = min(kwh, r["battery_kwh_net"] * 0.7)
            expect = kwh / mway * 100
            if not _close(r[key], expect, rel=0.03):
                bad.append((r["variant_id"], key, r[key], round(expect, 1)))
    assert bad == []


def test_estimated_motorway_consumption_is_wltp_times_1_30(rows: list[dict[str, Any]]) -> None:
    bad = []
    for r in rows:
        p = (r.get("provenance") or {}).get("consumption_motorway_kwh_100km") or {}
        cons = r.get("consumption_kwh_100km")
        if (
            p.get("estimate")
            and cons
            and not _close(r["consumption_motorway_kwh_100km"], cons * 1.3)
        ):
            bad.append(r["variant_id"])
    assert bad == []


def test_merged_values_are_never_averages(
    rows: list[dict[str, Any]], facts: dict[str, dict[str, Any]]
) -> None:
    """A non-derived number must equal one of the source facts it cites (Decision 009)."""
    bad = []
    for r in rows:
        for k, p in (r.get("provenance") or {}).items():
            if p.get("derived") or p.get("estimate") or k.startswith("price_new."):
                continue
            v = r.get(k)
            if not _is_number(v) or k == "registered_count_nl":
                continue
            cited = [facts[f]["value_num"] for f in p.get("fact_ids", []) if f in facts]
            cited = [c for c in cited if c is not None]
            if cited and not any(abs(round(c, 1) - v) < 0.051 for c in cited):
                bad.append((r["variant_id"], k, v, cited))
    assert bad == [], bad[:10]


# --- added by the T-004/005/006 fixes after review, 2026-11-15 ------------------------------


def test_run_log_has_no_host_paths(release_dir: Path) -> None:
    log = json.loads((release_dir / "run_log.json").read_text(encoding="utf-8"))
    for inp in log["inputs"]:
        assert not Path(inp["path"]).is_absolute(), inp["path"]
        assert inp["path"].startswith("data/"), inp["path"]
    text = (release_dir / "run_log.json").read_text(encoding="utf-8")
    for needle in ("/home/", "/root/", "/tmp/", "/Users/", "C:\\\\"):
        assert needle not in text


def test_no_eea_spec_facts(facts: dict[str, dict[str, Any]]) -> None:
    # EEA type-approval averages blend different cars (and M includes a 75 kg driver): counts only.
    eea = {f["field"] for f in facts.values() if f["source_id"] == "eea"}
    assert eea <= {"registered_count"}


def test_no_e_tron_gt_counted_as_e_tron(release_dir: Path) -> None:
    facts_tbl = pq.read_table(release_dir / "facts.parquet").to_pylist()
    for f in facts_tbl:
        if f["subject_id"].startswith("audi-e-tron"):
            assert " GT" not in (f["source_record"] or "").upper(), f["source_record"]


# --- added with KBA / DfT / ADEME / KilowattApp, 2026-11-15 ---------------------------------

COUNT_KIND = {"rdw": "fleet", "dft-veh": "fleet", "kba-fz10": "new_registrations",
              "eea": "new_registrations"}  # fmt: skip


def test_registrations_are_never_summed_across_sources_or_periods(
    rows: list[dict[str, Any]], facts: dict[str, dict[str, Any]]
) -> None:
    bad = []
    for r in rows:
        for cc, entries in (r.get("registrations") or {}).items():
            keys = [(e["source_id"], e["period"]) for e in entries]
            if len(keys) != len(set(keys)):
                bad.append((r["variant_id"], cc, "duplicate source/period"))
            for e in entries:
                if COUNT_KIND.get(e["source_id"]) != e["kind"]:
                    bad.append((r["variant_id"], cc, e["source_id"], e["kind"]))
            # The cited facts of one country come from the sources listed there, and each
            # entry's count equals the sum of its own source's cited facts for that period.
            p = r["provenance"][f"registrations.{cc}"]
            cited = [facts[f] for f in p.get("fact_ids", [])]
            for e in entries:
                own = [f for f in cited if f["source_id"] == e["source_id"]]
                if e["source_id"] != "rdw":  # RDW: summed per first-admission year (below)
                    own = [f for f in own if (e["period"] or "") in (f["source_record"] or "")
                           or e["source_id"] == "eea"]  # fmt: skip
                if own and sum(f["value_num"] for f in own) != e["count"]:
                    bad.append((r["variant_id"], cc, e["source_id"], e["count"]))
        nl = [e for e in (r.get("registrations") or {}).get("NL", []) if e["source_id"] == "rdw"]
        nl_counts = [(e["count"], e["kind"]) for e in nl]
        if r.get("registered_count_nl") is not None and nl_counts != [
            (r["registered_count_nl"], "fleet")
        ]:
            bad.append((r["variant_id"], "NL", "rdw != registered_count_nl"))
    assert bad == [], bad[:10]


def test_dft_counts_are_fleet_at_model_level_on_multi_generation_models(
    catalogue: dict[str, Any], rows: list[dict[str, Any]]
) -> None:
    gens_per_model: dict[str, int] = {}
    for g in catalogue["generations"]:
        gens_per_model[g["model_id"]] = gens_per_model.get(g["model_id"], 0) + 1
    for r in rows:
        for e in (r.get("registrations") or {}).get("UK", []):
            if e["source_id"] == "dft-veh":
                expect = "model" if gens_per_model[r["model_id"]] > 1 else "generation"
                assert (e["kind"], e["level"]) == ("fleet", expect), r["variant_id"]


def test_charge_curve_status_is_honest(
    rows: list[dict[str, Any]], facts: dict[str, dict[str, Any]]
) -> None:
    """Only a measured curve may give non-estimate curve figures; KilowattApp curves are
    'estimated' upstream, so every curve-derived figure is flagged estimate."""
    for r in rows:
        status = r.get("dc_curve_status")
        for f in ("dc_minutes_10_80", "dc_peak_held_min"):
            p = r["provenance"].get(f) or {}
            if (
                status in ("estimated", "default")
                and p.get("derived")
                and "curve" in p.get("note", "")
            ):
                assert p.get("estimate") is True, (r["variant_id"], f)
        if status == "measured":
            pytest.fail(f"{r['variant_id']}: no source publishes measured curves tonight")


def test_attach_only_sources_add_no_rows_of_their_own(
    rows: list[dict[str, Any]], facts: dict[str, dict[str, Any]]
) -> None:
    attach_only = {"ademe", "kilowatt-openev"}
    by_subject: dict[str, set[str]] = {}
    for f in facts.values():
        if f["subject_type"] == "variant":
            by_subject.setdefault(f["subject_id"], set()).add(f["source_id"])
    for r in rows:
        srcs = by_subject.get(r["variant_id"], set())
        assert not srcs or not srcs <= attach_only, (r["variant_id"], srcs)


def test_kilowatt_consumption_is_never_published(facts: dict[str, dict[str, Any]]) -> None:
    assert not [
        f
        for f in facts.values()
        if f["source_id"] == "kilowatt-openev" and f["field"] == "consumption_kwh_100km"
    ]
