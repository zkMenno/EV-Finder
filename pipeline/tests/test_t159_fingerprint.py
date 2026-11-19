"""T-159 (T-153 follow-up 6): a fingerprint group whose versions sit on 2+ seed variants that
each carry split evidence (match/tgk_split.yaml) splits into one `have` group per variant."""

from __future__ import annotations

from types import SimpleNamespace

from ev_pipeline.variants import propose as vp


def _v(placed: str | None) -> SimpleNamespace:
    return SimpleNamespace(placed=placed)


def _result(split: dict, bands: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(tgk_split=split, year_bands=bands or [])


SPLIT = {"y-lr": {"top_speed_kmh": {"217"}}, "y-perf": {"top_speed_kmh": {"250"}}}


def test_split_evidence_splits_the_group_per_variant():
    part = [_v("y-lr"), _v("y-perf"), _v("y-lr"), _v(None)]
    out = vp.split_by_evidence(part, _result(SPLIT))  # type: ignore[arg-type]
    assert [(len(g), by) for g, by in out] == [(2, "y-lr"), (1, "y-perf"), (1, "unplaced")]


def test_group_stays_whole_without_split_evidence_for_every_variant():
    part = [_v("y-lr"), _v("other")]
    assert vp.split_by_evidence(part, _result(SPLIT)) == [(part, "")]  # type: ignore[arg-type]
    one = [_v("y-lr"), _v(None)]
    assert vp.split_by_evidence(one, _result(SPLIT)) == [(one, "")]  # type: ignore[arg-type]


def test_year_bands_use_their_root_variants_evidence():
    bands = [{"variant_id": "y-lr", "new_ids": ["y-lr-2023"]}]
    part = [_v("y-lr-2023"), _v("y-perf")]
    out = vp.split_by_evidence(part, _result(SPLIT, bands))  # type: ignore[arg-type]
    assert [by for _, by in out] == ["y-lr-2023", "y-perf"]


def test_split_groups_get_their_own_keys_and_verdicts():
    rec = SimpleNamespace(year=2022, record_key="k", variant_name="Y", model="Y")
    mk = lambda placed: vp.Version(  # noqa: E731
        rec, "y", placed, "", "wltp", None, 90.0, 500.0, frozenset(), 0, 0.0
    )
    g_lr = vp.Group("y", "wltp", "multi", True, [mk("y-lr")], "y-lr")
    g_whole = vp.Group("y", "wltp", "multi", True, [mk("y-lr"), mk("y-perf")])
    assert g_lr.verdict == "have" and g_whole.verdict == "several"
    assert g_lr.key.endswith("|v=y-lr") and "|v=" not in g_whole.key
