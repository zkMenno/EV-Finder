"""T-153: a power figure the seed cites from a maker document wins over a record's power.

OpenEV Elroq "Base" is the Elroq 85 (77 kWh net) with the Elroq 60's 150 kW; the seed Elroq
85 cites Škoda's 210 kW. The aliased record joins the seed row (its battery agrees), and its
150 kW is withheld (validation.csv), never a Fact. Without battery agreement, or when the
seed's power is a plain spec, the seed power gate still sends the record to review.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from ev_pipeline.match.matcher import (
    CITED_POWER_WINS,
    NO_SEED_POWER_MATCH,
    MatchResult,
    match_records,
)
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

GEN = "skoda-elroq-gen1"
V85 = f"{GEN}-85"
OPENEV = {"id": "openev", "name": "Open EV Data", "licence": "CDLA-Permissive-2.0"}
SEED = {
    "makes": [
        {
            "id": "skoda",
            "name": "Skoda",
            "models": [
                {"id": "skoda-elroq", "name": "Elroq",
                 "generations": [{"id": GEN, "years": [2024, None]}]},
            ],
        }
    ]
}  # fmt: skip


def _cited(value: float) -> dict[str, Any]:
    return {
        "value": value,
        "source_url": "https://cdn.skoda-storyboard.com/x.pdf",
        "retrieved": date(2026, 11, 18),
        "quote": "Max. system engine performance [kW] 125* 150* 210* 250*",
        "confidence": "high",
    }


def _variant(power: dict[str, Any] | None = None, **specs: float) -> dict[str, Any]:
    v: dict[str, Any] = {
        "generation_id": GEN, "id": V85, "name": "Elroq 85 (77 kWh)", "years": [2025, None],
        "drivetrain": "rwd", "specs": specs, "source_names": {"openev": ["Base"]},
        "cited": {"battery_kwh_net": _cited(77)},
    }  # fmt: skip
    if power is not None:
        v["cited"]["power_kw"] = power
    return v


def _base(**specs: float) -> SourceRecord:
    return SourceRecord(
        source=OPENEV,
        record_key="openev:elroq/base",
        kind="spec",
        make="Skoda",
        model="Elroq",
        variant_name="Base",
        year=2025,
        specs={
            k: SpecValue(value=v, unit="kWh" if "kwh" in k else ("km" if "km" in k else "kW"))
            for k, v in specs.items()
        },
        retrieved_at=date(2026, 11, 18),
        confidence="medium",
    )


def _run(variant: dict[str, Any], rec: SourceRecord) -> MatchResult:
    mv, problems = parse_manual_variants({"variants": [variant]}, date(2026, 11, 18))
    assert problems == []
    return match_records([rec], parse_seed(SEED), mv, scoped_aliases=True)


def _openev_fields(res: MatchResult) -> set[str]:
    return {
        mf.fact.field.value
        for mf in res.spec_facts
        if mf.source_id == "openev" and mf.fact.subject_id.root == V85
    }


def test_cited_power_wins_and_the_record_power_is_withheld() -> None:
    rec = _base(battery_kwh_net=77, power_kw=150, wltp_range_km=581, dc_peak_kw=175)
    res = _run(_variant(_cited(210)), rec)
    assert res.unmatched == []
    assert _openev_fields(res) == {"battery_kwh_net", "wltp_range_km", "dc_peak_kw"}
    [p] = [p for p in res.problems if p.reason.startswith(CITED_POWER_WINS)]
    assert (p.subject_id, p.field, p.value) == (V85, "power_kw", "150")
    assert "150 vs 210 kW cited" in p.reason


def test_no_battery_evidence_keeps_the_seed_power_gate() -> None:
    res = _run(_variant(_cited(210)), _base(power_kw=150, wltp_range_km=581))
    assert [u.reason.split(" (")[0] for u in res.unmatched] == [f"{NO_SEED_POWER_MATCH} {V85}"]


def test_contradicting_battery_keeps_the_record_out() -> None:
    res = _run(_variant(_cited(210)), _base(battery_kwh_net=59, power_kw=150))
    assert len(res.unmatched) == 1 and _openev_fields(res) == set()


def test_spec_power_is_not_cited_power() -> None:
    """A seed `specs:` power is model knowledge, not a maker document: gate unchanged."""
    res = _run(_variant(None, power_kw=210), _base(battery_kwh_net=77, power_kw=150))
    assert res.unmatched and res.unmatched[0].reason.startswith(NO_SEED_POWER_MATCH)
    assert not any(p.reason.startswith(CITED_POWER_WINS) for p in res.problems)


def test_agreeing_power_joins_without_a_problem() -> None:
    res = _run(_variant(_cited(210)), _base(battery_kwh_net=77, power_kw=208))
    assert res.unmatched == [] and "power_kw" in _openev_fields(res)
    assert not any(p.reason.startswith(CITED_POWER_WINS) for p in res.problems)
