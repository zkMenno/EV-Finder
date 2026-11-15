"""T-060: battery pack / platform links for rows the seed file does not cover.

Rule links (same generation; usable kWh fits exactly one pack), release variant ids in
variant_links.yaml, cited platform-only generation defaults, and the coverage report.
Inline data only; no network.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from ev_pipeline.derive.links import (
    RULE_TOLERANCE,
    Links,
    apply_rule_links,
    inherited_for,
    link_coverage,
    pack_fit,
)
from ev_pipeline.release.build import pack_links_md

REPO = Path(__file__).resolve().parents[2]

PACKS = {
    "meb-58": {"id": "meb-58", "usable_kwh": 58, "gross_kwh": 62},
    "meb-77": {"id": "meb-77", "usable_kwh": 77, "gross_kwh": 82},
    "cma-78": {"id": "cma-78", "usable_kwh": 75, "gross_kwh": 78},
    "cma-82": {"id": "cma-82", "usable_kwh": 79, "gross_kwh": 82},
    "egmp-77-4": {"id": "egmp-77-4", "usable_kwh": "not-disclosed", "gross_kwh": 77.4},
}
PLATFORMS = {"vw-meb": {"id": "vw-meb", "name": "MEB"}, "volvo-cma": {"id": "volvo-cma"}}


def _links() -> Links:
    links = Links(platforms=dict(PLATFORMS), packs=dict(PACKS))
    links.by_variant = {
        "vw-id3-gen1-pro": {"variant_id": "vw-id3-gen1-pro", "platform_id": "vw-meb",
                            "battery_pack_id": "meb-58"},
        "vw-id3-gen1-pro-s": {"variant_id": "vw-id3-gen1-pro-s", "platform_id": "vw-meb",
                              "battery_pack_id": "meb-77"},
        "hy-i5-gen1-77": {"variant_id": "hy-i5-gen1-77", "platform_id": "e-gmp",
                          "battery_pack_id": "egmp-77-4"},
        # A release-id link from the file: it always beats the rule.
        "vw-id3-gen1-gtx": {"variant_id": "vw-id3-gen1-gtx", "battery_pack_id": "meb-58"},
    }  # fmt: skip
    links.by_generation = {
        "volvo-p2-gen1": {"generation_id": "volvo-p2-gen1", "platform_id": "volvo-cma",
                          "battery_pack_options": ["cma-78", "cma-82"]},
    }  # fmt: skip
    return links


GEN = {
    "vw-id3-gen1-pro": "vw-id3-gen1",
    "vw-id3-gen1-pro-s": "vw-id3-gen1",
    "vw-id3-gen1-base": "vw-id3-gen1",  # OpenEV variant, 58 kWh
    "vw-id3-gen1-77-2023": "vw-id3-gen1",  # OpenEV variant, 77 kWh
    "vw-id3-gen1-odd": "vw-id3-gen1",  # 48 kWh: fits no pack of the generation
    "vw-id3-gen1-gtx": "vw-id3-gen1",
    "hy-i5-gen1-77": "hy-i5-gen1",
    "hy-i5-gen1-n": "hy-i5-gen1",  # 78 kWh usable > 77.4 gross: cannot be that pack
    "volvo-p2-gen1-lr": "volvo-p2-gen1",  # 75 kWh fits cma-78 and cma-82 (5 %): ambiguous
    "volvo-p2-gen1-sr": "volvo-p2-gen1",  # no kWh at all
    "audi-a6-gen1-avant": "audi-a6-gen1",  # nothing linked in the generation
}
NET = {
    "vw-id3-gen1-base": 58.0,
    "vw-id3-gen1-77-2023": 77.0,
    "vw-id3-gen1-odd": 48.0,
    "vw-id3-gen1-gtx": 77.0,
    "hy-i5-gen1-n": 78.0,
    "volvo-p2-gen1-lr": 75.0,
    "audi-a6-gen1-avant": 94.9,
}


def _run() -> tuple[Links, dict[str, dict]]:
    links = _links()
    report = apply_rule_links(links, GEN, NET)
    return links, {r["variant_id"]: r for r in report}


def test_pack_fit_tolerance_and_gross_cap() -> None:
    assert pack_fit(PACKS["meb-77"], 77.0) == 0
    assert pack_fit(PACKS["meb-77"], 73.0) == pytest.approx(4 / 77)  # Q4 50: 5.2 % off
    assert pack_fit(PACKS["meb-77"], 77 * (1 - RULE_TOLERANCE) - 0.1) is None
    assert pack_fit(PACKS["egmp-77-4"], 75.0) is not None  # gross used: usable not disclosed
    assert pack_fit(PACKS["egmp-77-4"], 72.6) is None  # 6.2 % below gross: outside tolerance
    assert pack_fit(PACKS["egmp-77-4"], 78.0) is None  # above gross: never this pack
    assert pack_fit({"id": "x", "usable_kwh": "not-disclosed"}, 50.0) is None


def test_rule_links_pack_and_platform_from_same_generation() -> None:
    links, rep = _run()
    assert rep["vw-id3-gen1-base"]["battery_pack_id"] == "meb-58"
    assert rep["vw-id3-gen1-base"]["pack_via"] == "rule"
    assert rep["vw-id3-gen1-base"]["platform_id"] == "vw-meb"
    assert rep["vw-id3-gen1-base"]["platform_via"] == "rule"
    assert rep["vw-id3-gen1-77-2023"]["battery_pack_id"] == "meb-77"
    link = links.link_for("vw-id3-gen1-base", "vw-id3-gen1")
    assert link["battery_pack_id"] == "meb-58" and link["platform_id"] == "vw-meb"
    # Seed-linked rows are untouched and counted as `file`.
    assert rep["vw-id3-gen1-pro"]["pack_via"] == "file"
    assert "vw-id3-gen1-pro" not in links.by_rule


def test_release_id_link_in_file_beats_rule() -> None:
    links, rep = _run()
    # The file says meb-58 for the GTX even though 77 kWh fits meb-77: the file wins.
    assert rep["vw-id3-gen1-gtx"]["battery_pack_id"] == "meb-58"
    assert rep["vw-id3-gen1-gtx"]["pack_via"] == "file"
    # Its platform is still filled by rule (the file link names none).
    assert rep["vw-id3-gen1-gtx"]["platform_via"] == "rule"
    assert links.link_for("vw-id3-gen1-gtx", "vw-id3-gen1")["battery_pack_id"] == "meb-58"


def test_ambiguous_or_unfit_rows_stay_unlinked_with_reason() -> None:
    links, rep = _run()
    assert rep["vw-id3-gen1-odd"]["battery_pack_id"] is None
    assert "fits none of meb-58/meb-77" in rep["vw-id3-gen1-odd"]["reason"]
    assert rep["hy-i5-gen1-n"]["battery_pack_id"] is None  # 78 > 77.4 gross
    lr = rep["volvo-p2-gen1-lr"]
    assert lr["battery_pack_id"] is None and "fits 2 packs cma-78/cma-82" in lr["reason"]
    assert lr["platform_id"] == "volvo-cma" and lr["platform_via"] == "file"
    assert "no usable kWh" in rep["volvo-p2-gen1-sr"]["reason"]
    a6 = rep["audi-a6-gen1-avant"]
    assert a6["battery_pack_id"] is None and a6["platform_id"] is None
    assert "no link in this generation" in a6["reason"]
    assert "audi-a6-gen1-avant" not in links.by_rule


def test_rule_is_idempotent() -> None:
    links = _links()
    first = apply_rule_links(links, GEN, NET)
    assert apply_rule_links(links, GEN, NET) == first


def test_rule_links_carry_provenance_notes() -> None:
    links, _ = _run()
    inh = inherited_for(links, "vw-id3-gen1-base", "vw-id3-gen1", {"battery_kwh_net": 58.0})
    note = inh["label_provenance"]["battery_pack_id"]["note"]
    assert note.startswith("rule T-060: generation vw-id3-gen1; usable 58 kWh fits pack meb-58")
    assert inh["label_provenance"]["platform_id"]["note"].startswith("rule T-060")
    assert inh["label_provenance"]["battery_pack_id"]["source_ids"] == ["seed-manual"]
    # Pack facts flow to the row; the row's own usable kWh still wins.
    assert inh["numbers"]["battery_kwh_gross"][0] == 62.0
    assert "battery_kwh_net" not in inh["numbers"]
    # File links keep their old provenance note and no platform note.
    seed = inherited_for(links, "vw-id3-gen1-pro", "vw-id3-gen1", {})
    assert seed["label_provenance"]["battery_pack_id"]["note"] == (
        "from data/seed/variant_links.yaml"
    )
    assert "platform_id" not in seed["label_provenance"]


def test_cited_platform_provenance() -> None:
    links = Links(platforms=dict(PLATFORMS), packs=dict(PACKS))
    links.by_generation["vw-id7-gen1"] = {
        "generation_id": "vw-id7-gen1",
        "platform_id": "vw-meb",
        "cited": {
            "platform_id": {
                "value": "vw-meb",
                "source_url": "https://example.org/id7",
                "source_name": "Maker press release",
                "retrieved": date(2026, 11, 15),
                "quote": "based on MEB",
                "confidence": "high",
            }
        },
    }
    rep = {
        r["variant_id"]: r for r in apply_rule_links(links, {"vw-id7-gen1-pro": "vw-id7-gen1"}, {})
    }
    assert rep["vw-id7-gen1-pro"]["platform_via"] == "file"
    assert "no pack linked" in rep["vw-id7-gen1-pro"]["reason"]
    inh = inherited_for(links, "vw-id7-gen1-pro", "vw-id7-gen1", {})
    note = inh["label_provenance"]["platform_id"]["note"]
    assert "https://example.org/id7" in note and "retrieved 2026-11-15" in note


def test_coverage_counts_and_markdown() -> None:
    _, rep = _run()
    cov = link_coverage(list(rep.values()))
    assert cov["rows"] == len(GEN)
    assert cov["battery_pack_id"] == {"file": 4, "rule": 2, "missing": 5}
    assert sum(cov["platform_id"].values()) == len(GEN)
    assert {u["variant_id"] for u in cov["unlinked"]} == {
        "vw-id3-gen1-odd", "hy-i5-gen1-n", "volvo-p2-gen1-lr", "volvo-p2-gen1-sr",
        "audi-a6-gen1-avant",
    }  # fmt: skip
    md = "\n".join(pack_links_md(cov))
    assert "## Battery pack and platform links" in md
    assert "| battery_pack_id | 36% (4) | 18% (2) | 45% (5) |" in md
    assert "`audi-a6-gen1-avant`" in md
    assert pack_links_md(None) == []


# --- data/taxonomy/validate_taxonomy.py: release ids and cited links ------------------------


def _validator() -> ModuleType:
    path = REPO / "data" / "taxonomy" / "validate_taxonomy.py"
    spec = importlib.util.spec_from_file_location("validate_taxonomy_t060", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_release_generation_longest_prefix() -> None:
    v = _validator()
    gens = {"kia-ev6-gen1", "kia-ev6", "volvo-ex30-gen1"}
    assert v.release_generation("kia-ev6-gen1-gt-line", gens) == "kia-ev6-gen1"
    assert v.release_generation("volvo-ex30-gen1-base", gens) == "volvo-ex30-gen1"
    assert v.release_generation("volvo-ex30-gen1", gens) is None  # the generation itself
    assert v.release_generation("tesla-model-3-x", gens) is None


def test_check_link_cited_rules() -> None:
    v = _validator()
    errs: list[str] = []
    good = {
        "value": "vw-meb",
        "source_url": "https://example.org/",
        "source_name": "Maker",
        "retrieved": date(2026, 11, 15),
        "quote": "q",
        "confidence": "high",
    }
    v.check_link_cited("t", {"platform_id": "vw-meb"}, {"platform_id": good}, errs.append)
    assert errs == []
    bad = {**good, "value": "x", "source_url": "http://x", "retrieved": "soon", "quote": None}
    v.check_link_cited(
        "t", {"platform_id": "vw-meb"}, {"platform_id": bad, "ac_kw": {}}, errs.append
    )
    text = " | ".join(errs)
    for expect in ("differs from the link", "https", "retrieved", "quote", "can be cited"):
        assert expect in text
