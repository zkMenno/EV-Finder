"""T-111 (QA A-35 B4): plausibility gate. Fixture rows only, no network."""

from __future__ import annotations

import copy
from typing import Any

from ev_pipeline.qa.plausibility import (
    REVIEW,
    WITHHOLD,
    apply_gate,
    check_plausibility,
    find_issues,
    load_config,
)

# Thresholds as in the gate PR's qa_plausibility.yaml (A-35 B4 + release 1 dry run).
CFG: dict[str, Any] = {
    "rules": {
        "wltp_efficiency": {"review_above": 8.0, "withhold_above": {"suv": 8.2, "default": 10.0}},
        "dc_vs_peers": {"field": "dc_km_per_20min", "max_ratio": 1.3, "min_peers": 3},
        "copied_across_generations": {
            "fields": ["wltp_range_km", "consumption_kwh_100km"],
            "min_equal_fields": 1,
            "action": "review",
        },
    },
    "withhold_with": {"dc_km_per_20min": ["dc_km_per_10min"]},
}

WLTP_FACT = "openev:model_y_long_range_awd:wltp_range_km"
NET_FACT = "openev:model_y_long_range_awd:battery_kwh_net"


def _row(vid: str, gid: str, *, wltp: float, net: float, dc20: float, pack: str = "lr-75",
         body: str = "suv") -> dict[str, Any]:  # fmt: skip
    """A catalogue row shaped like release 1 (provenance as build_rows writes it)."""
    wf, nf = f"{WLTP_FACT}:{vid}", f"{NET_FACT}:{vid}"
    return {
        "variant_id": vid,
        "generation_id": gid,
        "model_id": "tesla-model-y",
        "body": body,
        "battery_pack_id": pack,
        "battery_kwh_net": net,
        "wltp_range_km": wltp,
        "consumption_kwh_100km": round(net / wltp * 100, 1),
        "real_range_km": round(wltp * 0.78, 1),
        "dc_km_per_20min": dc20,
        "dc_km_per_10min": round(dc20 / 2, 1),
        "provenance": {
            "battery_kwh_net": {"source_ids": ["openev"], "fact_ids": [nf]},
            "wltp_range_km": {"source_ids": ["openev"], "fact_ids": [wf]},
            "consumption_kwh_100km": {"source_ids": ["openev"], "fact_ids": [nf, wf],
                                      "derived": True},
            "real_range_km": {"source_ids": ["openev"], "fact_ids": [wf], "derived": True},
            "dc_km_per_20min": {"source_ids": ["openev"], "fact_ids": [nf, wf], "derived": True},
            "dc_km_per_10min": {"source_ids": ["openev"], "fact_ids": [nf, wf], "derived": True},
        },
    }  # fmt: skip


def release1_model_y() -> list[dict[str, Any]]:
    """Release 1 values (data/releases/1/catalogue.json): LR AWD 719 km / 79 kWh /
    387.2 km per 20 min in both generations; Performance 252 / 246, LR RWD 197 / 185."""
    return [
        _row("tesla-model-y-gen1-long-range", "gen1", wltp=719, net=79, dc20=387.2),
        _row("tesla-model-y-gen1-performance", "gen1", wltp=507, net=79, dc20=251.7),
        _row("tesla-model-y-gen1-long-range-rwd", "gen1", wltp=600, net=75, dc20=197.2),
        _row("tesla-model-y-juniper-long-range-awd", "juniper", wltp=719, net=79, dc20=387.2),
        _row("tesla-model-y-juniper-performance", "juniper", wltp=514, net=79, dc20=245.9),
        _row("tesla-model-y-juniper-long-range-rwd", "juniper", wltp=600, net=75, dc20=184.8),
    ]


def corrected_model_y() -> list[dict[str, Any]]:
    """T-110's sourced LR AWD figures (RDW TGK, CC0): gen1 533 km, Juniper 586 km WLTP;
    DC rescaled to the corrected range (252 and 288 km per 20 min)."""
    rows = release1_model_y()
    for r, wltp, dc in ((rows[0], 533, 252.0), (rows[3], 586, 288.0)):
        fixed = _row(r["variant_id"], r["generation_id"], wltp=wltp, net=r["battery_kwh_net"],
                     dc20=dc)  # fmt: skip
        r.clear()
        r.update(fixed)
    return rows


def test_release1_model_y_lr_trips_the_gate() -> None:
    issues = find_issues(release1_model_y(), CFG)
    lr = {"tesla-model-y-gen1-long-range", "tesla-model-y-juniper-long-range-awd"}
    got = {(i.variant_id, i.rule, i.action) for i in issues}
    for vid in lr:
        assert (vid, "wltp_efficiency", WITHHOLD) in got  # 9.10 km/kWh, SUV
        assert (vid, "dc_vs_peers", WITHHOLD) in got  # 1.54x / 1.57x the pack peers
    assert {i.variant_id for i in issues} == lr  # Performance and RWD pass


def test_withheld_values_and_their_derived_values_leave_the_row() -> None:
    rows = release1_model_y()
    res = apply_gate(rows, CFG)
    y = rows[0]
    for f in ("wltp_range_km", "real_range_km", "consumption_kwh_100km", "dc_km_per_20min",
              "dc_km_per_10min"):  # fmt: skip
        assert y[f] is None, f
        assert f not in y["provenance"], f
    assert y["battery_kwh_net"] == 79  # the other half of the ratio stays
    assert rows[1]["wltp_range_km"] == 507  # siblings untouched
    fields = sorted(r["field"] for r in res.review_rows if r["variant_id"] == y["variant_id"])
    assert fields == sorted(
        ["wltp_range_km", "real_range_km", "consumption_kwh_100km", "dc_km_per_20min",
         "dc_km_per_10min"]
    )  # fmt: skip
    assert all(r["tolerance"].startswith("plausibility ") for r in res.review_rows)
    assert {r["value"] for r in res.review_rows if r["field"] == "wltp_range_km"} == {719}


def test_corrected_values_pass() -> None:
    rows = corrected_model_y()
    before = copy.deepcopy(rows)
    res = apply_gate(rows, CFG)
    assert res.issues == []
    assert rows == before


def test_dc_against_generation_only_is_review() -> None:
    # Different packs charge differently (Leaf e+ vs 40 kWh): generation-wide outlier = review.
    rows = [
        _row("a", "g", wltp=270, net=39, dc20=50.0, pack="p40", body="hatchback"),
        _row("b", "g", wltp=270, net=39, dc20=54.0, pack="p40", body="hatchback"),
        _row("c", "g", wltp=385, net=59, dc20=93.4, pack="p62", body="hatchback"),
    ]
    issues = find_issues(rows, CFG)
    assert [(i.variant_id, i.rule, i.action) for i in issues] == [("c", "dc_vs_peers", REVIEW)]
    apply_gate(rows, CFG)
    assert rows[2]["dc_km_per_20min"] == 93.4


def test_dc_needs_min_peers() -> None:
    rows = [
        _row("a", "g", wltp=500, net=75, dc20=380.0),
        _row("b", "g", wltp=500, net=75, dc20=200.0),
    ]
    assert find_issues(rows, CFG) == []


def test_wltp_review_band_for_efficient_non_suv() -> None:
    # Model 3 Highland LR in release 1: 629 km / 75 kWh = 8.39 -> listed, not withheld.
    rows = [_row("m3", "g", wltp=629, net=75, dc20=300.0, body="sedan")]
    issues = find_issues(rows, CFG)
    assert [(i.rule, i.action) for i in issues] == [("wltp_efficiency", REVIEW)]
    apply_gate(rows, CFG)
    assert rows[0]["wltp_range_km"] == 629


def test_wltp_above_default_withhold_for_any_body() -> None:
    rows = [_row("x", "g", wltp=820, net=80, dc20=200.0, body="sedan")]
    assert find_issues(rows, CFG)[0].action == WITHHOLD


def test_copied_across_generations_with_different_packs() -> None:
    # Kona OS 64 kWh vs Kona SX2 LR in release 1: same WLTP 484 km, other pack -> both review.
    rows = [
        _row("os-64", "os", wltp=484, net=64, dc20=150.0, pack="hk-64"),
        _row("sx2-lr", "sx2", wltp=484, net=58, dc20=150.0, pack=""),
    ]
    issues = [i for i in find_issues(rows, CFG) if i.rule == "copied_across_generations"]
    assert {(i.variant_id, i.action) for i in issues} == {("os-64", REVIEW), ("sx2-lr", REVIEW)}


def test_same_pack_across_generations_is_not_a_copy() -> None:
    # The criterion says "different packs": a pack carried over may keep its figure.
    rows = [
        _row("g1", "gen1", wltp=533, net=75, dc20=250.0),
        _row("g2", "gen2", wltp=533, net=75, dc20=250.0),
    ]
    assert [i for i in find_issues(rows, CFG) if i.rule == "copied_across_generations"] == []


def test_derived_equal_values_are_not_copies() -> None:
    rows = [
        _row("a", "g1", wltp=500, net=60, dc20=150.0, pack="p1"),
        _row("b", "g2", wltp=501, net=61, dc20=150.0, pack="p2"),
    ]
    rows[1]["consumption_kwh_100km"] = rows[0]["consumption_kwh_100km"] = 12.0
    assert [i for i in find_issues(rows, CFG) if i.rule == "copied_across_generations"] == []


def test_no_config_means_gate_off_and_check_skipped(tmp_path) -> None:  # noqa: ANN001
    assert load_config(tmp_path / "missing.yaml") is None
    rows = release1_model_y()
    res = apply_gate(rows, None)
    assert res.issues == [] and res.review_rows == [] and rows[0]["wltp_range_km"] == 719
    assert check_plausibility(rows, None).status == "skipped"


def test_check_reports_withheld_and_review() -> None:
    rows = release1_model_y()
    res = apply_gate(rows, CFG)
    held = [i.to_dict() for i in res.issues if i.action == WITHHOLD]
    c = check_plausibility(rows, CFG, held)
    assert c.status == "flag" and not c.blocking
    assert c.details["withheld_count"] == 4
    assert c.details["review_count"] == 0  # withheld values are gone from the rows
    clean = corrected_model_y()
    assert check_plausibility(clean, CFG, []).status == "pass"


def test_shipped_config_when_present_trips_model_y() -> None:
    """The gate PR's qa_plausibility.yaml (when on this branch) must trip release 1's Model Y."""
    cfg = load_config()
    if cfg is None:  # thresholds land in their own gate PR (G-06)
        assert apply_gate(release1_model_y(), cfg).issues == []
        return
    ids = {i.variant_id for i in find_issues(release1_model_y(), cfg) if i.action == WITHHOLD}
    assert ids == {"tesla-model-y-gen1-long-range", "tesla-model-y-juniper-long-range-awd"}
    assert find_issues(corrected_model_y(), cfg) == []


def test_release_build_withholds_and_reports(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """End to end on the release fixture: withheld values leave catalogue.json, land in
    data/review/conflicts.csv and in qa.json `plausibility`; derived files never see them."""
    import json
    import shutil
    from datetime import UTC, datetime
    from pathlib import Path

    import yaml

    from ev_pipeline.qa import plausibility
    from ev_pipeline.release.build import build_release, write_release

    fix = Path(__file__).parent / "fixtures" / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")
    cfg = {"rules": {"wltp_efficiency": {"review_above": 0.1, "withhold_above": {"default": 0.1}}}}
    path = tmp_path / "qa_plausibility.yaml"
    path.write_text(yaml.safe_dump(cfg))
    monkeypatch.setattr(plausibility, "CONFIG_FILE", path)

    res = build_release(d, now=datetime(2026, 11, 15, 1, 0, tzinfo=UTC))
    held = {i["variant_id"] for i in res.plausibility_withheld}
    assert held  # the fixture has WLTP + usable kWh rows
    for r in res.catalogue["rows"]:
        if r["variant_id"] in held:
            assert r["wltp_range_km"] is None and "wltp_range_km" not in r["provenance"]
    out = write_release(res, d)
    qa = json.loads((out / "qa.json").read_text())["checks"]["plausibility"]
    assert qa["status"] == "flag" and qa["details"]["withheld_count"] == len(held)
    conflicts = (d / "review" / "conflicts.csv").read_text()
    assert "plausibility wltp_efficiency" in conflicts
    assert res.sections["plausibility"]["withheld_values"] >= len(held)


# --- PR #91 fresh review: withheld inputs take every value built on them -------------------


def _release2_atto3() -> dict[str, Any]:
    """Release 2 shape: WLTP 510 km on 60.5 kWh (8.43 km/kWh, SUV) is withheld, but the
    WLTP consumption is its own (RDW TGK) fact, so the share-a-fact rule kept it."""
    return {
        "variant_id": "byd-atto-3-gen1-60kwh",
        "generation_id": "byd-atto-3-gen1",
        "model_id": "byd-atto-3",
        "body": "suv",
        "battery_kwh_net": 60.5,
        "wltp_range_km": 510.0,
        "consumption_kwh_100km": 16.4,
        "real_range_km": 397.8,
        "real_range_rung": "body-ratio",
        "provenance": {
            "battery_kwh_net": {"source_ids": ["openev"], "fact_ids": ["o:net"]},
            "wltp_range_km": {"source_ids": ["openev"], "fact_ids": ["o:wltp"]},
            "consumption_kwh_100km": {"source_ids": ["rdw-tgk"], "fact_ids": ["r:cons"]},
            "real_range_km": {"source_ids": ["openev"], "fact_ids": ["o:wltp"],
                              "derived": True, "estimate": True},
        },
    }  # fmt: skip


def test_withheld_real_range_takes_its_rung() -> None:
    """A rung names the basis of real_range_km; with no real range it must go too."""
    row = _release2_atto3()
    apply_gate([row], CFG)
    assert row["wltp_range_km"] is None and row["real_range_km"] is None
    assert row["real_range_rung"] is None


def test_range_basis_withheld_lists_the_variant() -> None:
    """WLTP or usable kWh withheld -> no range estimate (matrix, winter range, scores input)
    may be built on the row; a withheld DC figure alone does not block range estimates."""
    rows = release1_model_y()
    res = apply_gate(rows, CFG)
    assert res.range_withheld == {
        "tesla-model-y-gen1-long-range",
        "tesla-model-y-juniper-long-range-awd",
    }
    atto = [_release2_atto3()]
    assert apply_gate(atto, CFG).range_withheld == {"byd-atto-3-gen1-60kwh"}
    dc_only = {"rules": {"dc_vs_peers": CFG["rules"]["dc_vs_peers"]}}
    assert apply_gate(release1_model_y(), dc_only).range_withheld == set()


def test_release_build_withholds_winter_range_and_scores_input(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    """End to end: a row whose WLTP is withheld gets no real-range rung, no winter range,
    no consumption-matrix entry and no derived shortlist values."""
    import shutil
    from datetime import UTC, datetime
    from pathlib import Path

    import yaml

    from ev_pipeline.qa import plausibility
    from ev_pipeline.release.build import build_release

    fix = Path(__file__).parent / "fixtures" / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")

    base = build_release(d, now=datetime(2026, 11, 15, 1, 0, tzinfo=UTC))
    winter_before = {r["variant_id"] for r in base.catalogue["rows"]
                     if r.get("real_range_winter_km") is not None}  # fmt: skip
    assert winter_before  # the fixture models winter range without the gate

    cfg = {"rules": {"wltp_efficiency": {"review_above": 0.1, "withhold_above": {"default": 0.1}}}}
    path = tmp_path / "qa_plausibility.yaml"
    path.write_text(yaml.safe_dump(cfg))
    monkeypatch.setattr(plausibility, "CONFIG_FILE", path)
    res = build_release(d, now=datetime(2026, 11, 15, 1, 0, tzinfo=UTC))
    held = {i["variant_id"] for i in res.plausibility_withheld}
    assert held & winter_before  # the test exercises a row that had a winter range
    for r in res.catalogue["rows"]:
        if r["variant_id"] in held:
            vid = r["variant_id"]
            assert r.get("real_range_km") is None and r.get("real_range_rung") is None, vid
            assert r.get("real_range_winter_km") is None, vid
            assert "real_range_winter_km" not in r["provenance"], vid
    matrix_ids = {m["variant_id"] for m in (res.consumption or {}).get("variants", [])}
    assert not held & matrix_ids
    for v in (res.shortlist or {}).get("variants", []):
        if v["variant_id"] in held:
            assert not v.get("derived"), v["variant_id"]
