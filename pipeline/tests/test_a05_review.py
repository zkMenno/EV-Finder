"""A-05 overnight review: regression tests for findings (audits/A-05-overnight-review.md).

Tests marked xfail(strict=True) document a confirmed bug: they fail today (so the suite stays
green) and turn into an XPASS error the moment the fix lands, so the marker must be removed
together with the fix.
"""

from __future__ import annotations

from datetime import date

import pytest

from ev_pipeline.match.matcher import VariantInfo, match_records
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

RDW = {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"}

SEED = {
    "makes": [
        {
            "id": "volvo",
            "name": "Volvo",
            "models": [
                {
                    "id": "volvo-ex30",
                    "name": "EX30",
                    "generations": [{"id": "volvo-ex30-gen1", "years": [2023, None]}],
                }
            ],
        }
    ]
}
GEN = "volvo-ex30-gen1"


def _v(vid: str, name: str, kw: float, wltp: float) -> dict:
    return {
        "generation_id": GEN,
        "id": f"{GEN}-{vid}",
        "name": name,
        "years": [2023, None],
        "specs": {"power_kw": kw, "wltp_range_km": wltp},
    }


ROWS = [
    _v("base", "base", 200, 344),  # OpenEV names the entry trim "base"
    _v("69-kwh", "69 kWh", 200, 476),
    _v("twin-motor", "Twin Motor", 315, 449),
]


def _coarse_rdw(wltp: float) -> SourceRecord:
    """An RDW make|model|year group record: no variant name, no power evidence (its WLTP is
    the median of a plate sample over all trims of that year)."""
    return SourceRecord(
        source=RDW,
        record_key="8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:VOLVO|EX30|2024#wltp_range_km",
        make="VOLVO",
        model="EX30",
        variant_name=None,
        year=2024,
        specs={"wltp_range_km": SpecValue(value=wltp, unit="km")},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )


def _placed(res) -> set[str]:
    return {mf.fact.subject_id.root for mf in res.spec_facts if mf.source_id == "rdw"}


def test_named_treats_missing_name_as_base() -> None:
    """Root cause (documents current behaviour): a record without a variant name is an
    exact name match for any variant called "base"."""
    info = VariantInfo(id=f"{GEN}-base", generation_id=GEN, name="base")
    assert info.named("rdw", None) is True


@pytest.mark.xfail(strict=True, reason="A-05 F1: nameless RDW group lands on 'base'")
def test_nameless_rdw_group_does_not_land_on_base_by_name() -> None:
    """475 km is the Extended Range figure (69 kWh variant, 476 km); it must never become
    the 51 kWh base car's WLTP. Either 69 kWh (WLTP evidence) or review is acceptable."""
    seed = parse_seed(SEED)
    manual = parse_manual_variants({"variants": ROWS}, date(2026, 11, 14))[0]
    res = match_records([_coarse_rdw(475)], seed, manual)
    assert f"{GEN}-base" not in _placed(res)


# --- F (merge): a SPREAD_SOURCES source whose own vote conflicts still lifts confidence -----

from ev_pipeline.match.matcher import MatchedFact, priority_of  # noqa: E402
from ev_pipeline.merge.merge import merge_facts  # noqa: E402
from ev_pipeline.schema_models import Fact  # noqa: E402

_LIC = {"rdw-tgk": "CC0-1.0", "openev": "CDLA-Permissive-2.0"}


def _mf(source: str, value: float, key: str, year: int) -> MatchedFact:
    fact = Fact(
        id=f"{source}:{key}:wltp_range_km",
        subject_type="variant",
        subject_id="x-gen1-base",
        field="wltp_range_km",
        value=value,
        unit="km",
        source={"id": source, "name": source, "licence": _LIC[source]},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    return MatchedFact(fact, source, priority_of(source), year)


@pytest.mark.xfail(strict=True, reason="A-05 F6: conflicting TGK vote still counts as agreeing")
def test_tgk_whose_vote_conflicts_does_not_confirm_the_value() -> None:
    """openev 400 wins; TGK's own vote (earliest version) says 340, a later TGK version says
    400. TGK disagrees as a source, so the value must not reach `high` on TGK's account."""
    facts = [_mf("openev", 400, "o", 2021), _mf("rdw-tgk", 340, "a", 2020)]
    facts.append(_mf("rdw-tgk", 400, "b", 2022))
    mg = merge_facts(facts)
    assert mg.value == 400
    assert any(f.source_id == "rdw-tgk" for f in mg.conflicts)  # the vote is a conflict...
    assert mg.confidence != "high"  # ...so TGK must not also confirm the value
