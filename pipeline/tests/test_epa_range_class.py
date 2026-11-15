"""A-30 follow-up: EPA "Long Range" / "Standard Range" rows only attach to that pack class."""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import _Candidate, range_class_pool
from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import Confidence, Source

SRC = Source(
    id="fueleconomy", name="fe", url="https://x.example", licence="US-Government-Public-Domain"
)


def _rec(model: str) -> SourceRecord:
    return SourceRecord(source=SRC, record_key="k", make="Kia", model=model,
                        retrieved_at=date(2026, 11, 15), confidence=Confidence.medium)  # fmt: skip


def _c(root: str, *kwh: float) -> _Candidate:
    return _Candidate(root, [root], set(), set(kwh), set(), set())


EV6 = [_c("58", 58.0), _c("77", 77.4), _c("unknown")]


def test_long_range_drops_the_small_pack_only() -> None:
    pool, cls = range_class_pool(_rec("EV6 Long Range RWD"), EV6)
    assert cls == "max" and [c.root for c in pool] == ["77", "unknown"]


def test_standard_range_drops_the_big_pack() -> None:
    pool, cls = range_class_pool(_rec("EV6 RWD (Standard Range)"), EV6)
    assert cls == "min" and [c.root for c in pool] == ["58", "unknown"]


def test_no_class_text_or_no_real_gap_means_no_rule() -> None:
    assert range_class_pool(_rec("EV6 RWD"), EV6) == (EV6, "")
    juniper = [_c("lr-rwd", 75.0), _c("lr-awd", 79.0), _c("perf", 79.0)]
    assert range_class_pool(_rec("Model Y Long Range RWD"), juniper) == (juniper, "")
    both = _rec("Long Range Standard Range")
    assert range_class_pool(both, EV6) == (EV6, "")


def test_split_at_the_biggest_step() -> None:
    ioniq = [_c("58", 58.0), _c("63", 63.0), _c("77", 77.4), _c("84", 84.0)]
    pool, _ = range_class_pool(_rec("Ioniq 5 RWD (Long Range)"), ioniq)
    assert [c.root for c in pool] == ["77", "84"]
