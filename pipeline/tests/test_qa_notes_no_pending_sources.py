"""Published QA text never names a permission-pending source (pipeline/AGENTS.md rule 5).

Release 2's qa.json carried "Nyland" in the EPA back-test note and the profile-fields
proxy_note (PR #91 fresh review). test_real_release only catches that after a release is
built; these build the two sections from small inputs and check them directly.
"""

from __future__ import annotations

import json
from pathlib import Path

from ev_pipeline.backtest import epa
from ev_pipeline.qa import profile_fields as pf
from ev_pipeline.refresh.plan import PERMISSION_PENDING

NEEDLES = {s.lower() for s in PERMISSION_PENDING} | {"nyland", "bjørn", "bjorn"}


def _clean(obj: object) -> list[str]:
    blob = json.dumps(obj, ensure_ascii=False).lower()
    return [n for n in sorted(NEEDLES) if n in blob]


def _row(vid: str) -> dict:
    return {
        "variant_id": vid,
        "model_id": vid.rsplit("-", 1)[0],
        "body": "sedan",
        "wltp_range_km": 500,
        "real_range_km": 400.0,
        "real_range_rung": "body-ratio",
        "consumption_kwh_100km": 15.0,
        "battery_kwh_net": 60,
        "provenance": {
            "wltp_range_km": {"source_ids": ["eea"]},
            "consumption_kwh_100km": {"source_ids": ["eea"]},
        },
    }


def test_epa_backtest_notes_name_no_pending_source(tmp_path: Path) -> None:
    (tmp_path / "seed").mkdir()
    (tmp_path / "seed" / "top40.yaml").write_text("models:\n- model_id: a-m\n")
    facts = [{"subject_type": "variant", "subject_id": "a-m-1", "field": "epa_range_km",
              "value": 380, "source": {"id": "fueleconomy"}, "source_record": "r1"}]  # fmt: skip
    bt = epa.epa_backtest({"rows": [_row("a-m-1")]}, facts, tmp_path, lambda s: True)
    assert _clean(bt) == []
    assert _clean(epa.audit_md(bt, 1, "t")) == []


def test_profile_fields_section_names_no_pending_source() -> None:
    sec = pf.profile_fields_section({"rows": [_row("a-m-1")]}, None, None, pf.load_config())
    assert _clean(sec) == []
