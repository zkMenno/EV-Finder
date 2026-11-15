"""Q-019 option (a): EEA generation averages corroborate merged values, never set them."""

from __future__ import annotations

from datetime import date

import pytest

from ev_pipeline.derive.metrics import quality_tier
from ev_pipeline.match.matcher import (
    EEA_CORROBORATION_ENV,
    eea_corroboration_enabled,
    match_records,
)
from ev_pipeline.match.seed import parse_seed
from ev_pipeline.merge.corroborate import apply_corroboration, variant_covers
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.merge.policy import parse_policies
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Source

OPENEV = {"id": "openev", "name": "OpenEV Data", "licence": "CDLA-Permissive-2.0"}
KWA = {"id": "kilowatt-openev", "name": "KilowattApp", "licence": "MIT"}
EEA = {"id": "eea", "name": "EEA", "licence": "CC-BY-4.0"}
RDW = {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"}

SEED = parse_seed(
    {
        "makes": [
            {
                "id": "cupra",
                "name": "Cupra",
                "models": [
                    {
                        "id": "cupra-born",
                        "name": "Born",
                        "generations": [{"id": "cupra-born-gen1", "years": [2021, None]}],
                    }
                ],
            }
        ]
    }
)
POLICIES = parse_policies(
    {
        "fields": {
            "wltp_range_km": {"primary": ["openev"], "tolerance": {"pct": 2}},
            "battery_kwh_net": {"primary": ["openev"], "tolerance": {"pct": 2}, "merge": "median"},
        }
    }
)


def _spec(source, variant, year, **specs):
    units = {"wltp_range_km": "km", "battery_kwh_net": "kWh"}
    return SourceRecord(
        source=source,
        record_key=f"{source['id']}:{variant}:{year}",
        make="Cupra",
        model="Born",
        variant_name=variant,
        year=year,
        specs={k: SpecValue(value=v, unit=units[k]) for k, v in specs.items()},
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
    )


def _eea(country, zr, count, year=2025, wh_km=None):
    specs = {"wltp_range_km": SpecValue(value=zr, unit="km")}
    if wh_km is not None:
        specs["consumption_kwh_100km"] = SpecValue(value=wh_km, unit="Wh/km")
    specs["registered_count"] = SpecValue(value=count, unit="count")
    return SourceRecord(
        source=EEA,
        record_key=f"eea:{country}|CUPRA|BORN|{year}#corroboration",
        kind="corroboration",
        make="CUPRA",
        model="BORN",
        year=year,
        country=country,
        specs=specs,
        retrieved_at=date(2026, 11, 14),
        confidence="low",
    )


def _records():
    return [
        _spec(OPENEV, "58 kWh", 2021, wltp_range_km=420, battery_kwh_net=58),
        _spec(OPENEV, "58 kWh", 2025, wltp_range_km=420, battery_kwh_net=58),  # still sold
        _spec(KWA, "58 kWh", 2021, battery_kwh_net=58),
        _spec(OPENEV, "77 kWh", 2022, wltp_range_km=548, battery_kwh_net=77),
        _eea("DE", 423.0, 9000, wh_km=165.0),  # biggest sample: the one offered
        _eea("NL", 548.0, 50),  # small sample: never a second chance to agree
    ]


def _run(records, corroborate=True):
    res = match_records(records, SEED, eea_corroboration=corroborate)
    by_v: dict[str, list] = {}
    for mf in res.spec_facts:
        by_v.setdefault(mf.fact.subject_id.root, []).append(mf)
    merged = {v: merge_variant_facts(fs, POLICIES) for v, fs in by_v.items()}
    used, log = apply_corroboration(merged, res.variants, res.corroboration_facts, POLICIES)
    return res, merged, used, log


def test_flag(monkeypatch) -> None:
    monkeypatch.delenv(EEA_CORROBORATION_ENV, raising=False)
    assert eea_corroboration_enabled() is False  # default off: Q-019 is open
    monkeypatch.setenv(EEA_CORROBORATION_ENV, "1")
    assert eea_corroboration_enabled() is True
    assert eea_corroboration_enabled(False) is False


def test_flag_off_ignores_corroboration_records() -> None:
    res, merged, used, _ = _run(_records(), corroborate=False)
    assert res.corroboration_facts == [] and used == []
    assert res.corroboration_skipped["flag off"] == 2
    assert res.unmatched == [] and res.other_makes == {}  # never unmatched.csv
    assert merged["cupra-born-gen1-58-kwh"]["wltp_range_km"].agreeing_sources == 1


def test_generation_fact_one_per_field_heaviest_average() -> None:
    res, *_ = _run(_records())
    facts = {mf.fact.field.value: mf for mf in res.corroboration_facts}
    assert set(facts) == {"wltp_range_km", "consumption_kwh_100km"}
    w = facts["wltp_range_km"]
    assert w.fact.subject_type.value == "generation"
    assert w.fact.subject_id.root == "cupra-born-gen1"
    assert w.fact.value == 423.0 and w.weight == 9000  # DE, not NL's 548
    assert facts["consumption_kwh_100km"].fact.value == pytest.approx(16.5)  # Wh/km -> kWh/100km
    # Never a variant, never a spec fact.
    assert all(mf.source_id != "eea" for mf in res.spec_facts)


def test_agreement_counts_but_never_sets_the_value() -> None:
    _, merged, used, log = _run(_records())
    m58 = merged["cupra-born-gen1-58-kwh"]["wltp_range_km"]
    assert m58.value == 420 and m58.winner.source_id == "openev"  # value unchanged
    assert m58.agreeing_sources == 2 and m58.independent_agreeing == 2
    assert "eea" in m58.source_ids and used[0].fact.id in m58.fact_ids
    assert m58.confidence == "medium"  # corroboration does not raise confidence
    assert "corroboration" in (m58.note() or "")
    # 77 kWh (548 km) is 23% away from the DE average: not used, and not a conflict.
    m77 = merged["cupra-born-gen1-77-kwh"]["wltp_range_km"]
    assert m77.agreeing_sources == 1 and m77.conflicts == [] and "eea" not in m77.source_ids
    # No merged consumption anywhere: the consumption average sets nothing.
    assert all("consumption_kwh_100km" not in f for f in merged.values())
    assert log["outcomes"]["agrees"] == 1


def test_sourced_tier_needs_battery_too() -> None:
    _, merged, *_ = _run(_records())
    m = merged["cupra-born-gen1-58-kwh"]
    tier = quality_tier(
        m["battery_kwh_net"].independent_agreeing, m["wltp_range_km"].independent_agreeing
    )
    assert tier == "sourced"  # battery: openev + KilowattApp; range: openev + EEA average
    m77 = merged["cupra-born-gen1-77-kwh"]
    assert quality_tier(m77["battery_kwh_net"].independent_agreeing, 1) == "single-source"


def test_not_counted_twice_and_only_for_variants_on_sale() -> None:
    recs = _records()
    recs[0] = _spec(OPENEV, "58 kWh", 2021, wltp_range_km=420, battery_kwh_net=58)
    res = match_records(recs, SEED, eea_corroboration=True)
    info = res.variants["cupra-born-gen1-58-kwh"]
    info.explicit_end = 2023  # pretend it left the market before the 2025 average
    assert not variant_covers(info, 2025) and variant_covers(info, 2022)
    by_v: dict[str, list] = {}
    for mf in res.spec_facts:
        by_v.setdefault(mf.fact.subject_id.root, []).append(mf)
    merged = {v: merge_variant_facts(fs, POLICIES) for v, fs in by_v.items()}
    used, log = apply_corroboration(merged, res.variants, res.corroboration_facts, POLICIES)
    assert used == [] and log["outcomes"]["variant not on sale that year"] >= 1
    # A second pass never adds EEA again.
    info.explicit_end = None
    apply_corroboration(merged, res.variants, res.corroboration_facts, POLICIES)
    apply_corroboration(merged, res.variants, res.corroboration_facts, POLICIES)
    assert merged["cupra-born-gen1-58-kwh"]["wltp_range_km"].agreeing_sources == 2


def test_only_corroboration_sources() -> None:
    rogue = _eea("NL", 420.0, 10).model_copy(update={"source": Source(**RDW)})
    res = match_records([*_records()[:4], rogue], SEED, eea_corroboration=True)
    assert res.corroboration_facts == []
    assert res.corroboration_skipped["rdw: not a corroboration source"] == 1
    assert res.spec_facts and all(mf.source_id != "rdw" for mf in res.spec_facts)


# --- release integration ------------------------------------------------------------------


def _release_dir(tmp_path):
    import json
    import shutil
    from pathlib import Path

    fix = Path(__file__).parent / "fixtures" / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")
    rec = {
        "source": {"id": "eea", "name": "EEA CO2 emissions from new cars", "licence": "CC-BY-4.0"},
        "record_key": "eea:2022:DE:FORD|MUSTANG MACH-E#corroboration",
        "kind": "corroboration",
        "make": "FORD",
        "model": "MUSTANG MACH-E",
        "year": 2022,
        "country": "DE",
        "specs": {
            "wltp_range_km": {"value": 545.0, "unit": "km"},
            "registered_count": {"value": 1200, "unit": "count"},
        },
        "retrieved_at": "2026-11-14",
        "confidence": "low",
    }
    with (d / "staging" / "eea.records.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return d


@pytest.mark.parametrize("flag", ["0", "1"])
def test_release_corroboration(tmp_path, monkeypatch, flag) -> None:
    from datetime import UTC, datetime

    from ev_pipeline.release.build import build_release, summary

    monkeypatch.setenv(EEA_CORROBORATION_ENV, flag)
    res = build_release(_release_dir(tmp_path), now=datetime(2026, 11, 15, tzinfo=UTC))
    row = next(r for r in res.catalogue["rows"] if r["model_id"] == "ford-mustang-mach-e")
    p = row["provenance"]["wltp_range_km"]
    assert row["wltp_range_km"] == 540  # the value never moves
    fact_ids = {f["id"] for f in res.facts}
    assert all(fid in fact_ids for fid in p["fact_ids"])  # QA: every fact id resolves
    eea_facts = [f for f in res.facts if f["id"].endswith("#corroboration:wltp_range_km")]
    s = summary(res)
    if flag == "1":
        assert p["agreeing_sources"] == 2 and "eea" in p["source_ids"]
        assert "corroboration" in p.get("note", "")
        assert [f["subject_type"] for f in eea_facts] == ["generation"]
        assert s["match_flags"]["eea_corroboration"] is True
        assert s["corroboration"]["facts_used"] == 1
    else:
        assert p.get("agreeing_sources", 1) == 1 and "eea" not in p["source_ids"]
        assert eea_facts == []
        assert s["corroboration"]["skipped"] == {"flag off": 1}
