"""Decision 036/037 housekeeping: data/sources.yaml rows and the pending-confirmation status."""

from __future__ import annotations

from pathlib import Path

import pytest

from ev_pipeline.release.gate import RELEASABLE_STATUSES, load_registry, parse_registry

REGISTRY = Path(__file__).resolve().parents[2] / "data" / "sources.yaml"


def _reg(status: str, licence: str = "CC-BY-4.0"):
    return parse_registry({"sources": [{"id": "x", "licence": licence, "status": status}]})


@pytest.mark.parametrize("status", sorted(RELEASABLE_STATUSES))
def test_releasable_statuses_pass_the_gate(status: str) -> None:
    assert _reg(status).releasable("x")


@pytest.mark.parametrize("status", ["blocked", "waiting_permission", "", "pending"])
def test_other_statuses_stay_blocked(status: str) -> None:
    assert not _reg(status).releasable("x")


def test_pending_confirmation_still_needs_a_named_licence() -> None:
    assert not _reg("active_pending_confirmation", "unknown (to confirm)").releasable("x")


def test_repo_registry_reflects_decisions_036_037() -> None:
    reg = load_registry(REGISTRY)
    s = reg.sources
    assert s["eafo"].status == "active_pending_confirmation" and reg.releasable("eafo")
    assert "Decision 037" in s["eafo"].terms
    for sid in ("era5-land", "meteostat", "geonames", "ecb-mir", "ndw", "afdc-stations"):
        assert reg.releasable(sid), sid
    for sid in ("wa-dol-ev", "eobs", "gisco-lau", "boe-iumhptl", "rvo"):
        assert not reg.releasable(sid), sid
    assert "ODbL" in s["wa-dol-ev"].licence
    import yaml

    raw = {e["id"]: e for e in yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["sources"]}
    assert raw["ecb-mir"]["series"]["DE"] == "MIR.M.DE.B.A2B.A.C.A.2250.EUR.N"
    assert "NL" not in raw["ecb-mir"]["series"]  # series stops 2010-05 (R-20)
    for sid in ("rdw", "rdw-defects", "rdw-tgk"):
        assert s[sid].name.startswith("Dutch open vehicle register (opendata.rdw.nl)"), sid


def test_rdw_attribution_follows_decision_037() -> None:
    root = Path(__file__).resolve().parents[1] / "ev_pipeline" / "sources"
    for name in ("rdw", "rdw_defects", "rdw_tgk"):
        text = (root / name / "adapter.py").read_text(encoding="utf-8")
        assert "Bron: RDW" not in text, name
        assert "Dutch open vehicle register (opendata.rdw.nl), CC0." in text, name
