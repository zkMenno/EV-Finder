"""Shared charging-stats helper: taxonomy ids, definition windows, schema validation."""

from datetime import date

import jsonschema
import pytest

from ev_pipeline.sources.eafo import charging_stats as cs


def builder() -> cs.StatBuilder:
    return cs.StatBuilder(
        source_id="fixture",
        taxonomy=cs.load_taxonomy(),
        retrieved_at=date(2026, 11, 15),
        confidence="high",
    )


def test_definition_validity_window() -> None:
    tax = cs.load_taxonomy()
    assert not tax.in_validity("uk-dft-evse-2026", date(2025, 12, 31))
    assert tax.in_validity("uk-dft-evse-2026", date(2026, 1, 1))
    assert tax.in_validity("uk-dft-device-pre2026", date(2025, 12, 31))
    assert not tax.in_validity("uk-dft-device-pre2026", date(2026, 1, 1))


def test_unknown_ids_are_refused() -> None:
    b = builder()
    kw = dict(
        country="DE",
        period_end=date(2026, 7, 1),
        value=1,
        unit="count",
        definition_id="de-bnetza-ladepunkt",
    )
    with pytest.raises(ValueError, match="metric"):
        b.add(metric_id="chargers", **kw)
    with pytest.raises(ValueError, match="power band"):
        b.add(metric_id="public-points", power_band_id="dc-999", **kw)
    with pytest.raises(ValueError, match="definition"):
        b.add(metric_id="public-points", **{**kw, "definition_id": "nope"})


def test_row_matches_schema_fixture_shape_and_rejects_negative() -> None:
    row = builder().add(
        country="DE",
        period_end=date(2026, 7, 1),
        metric_id="public-points-dc",
        power_band_id="dc-150-349",
        value=12345,
        unit="count",
        definition_id="de-bnetza-ladepunkt",
    )
    assert row is not None and row["entered_by"] == "pipeline"
    with pytest.raises(jsonschema.ValidationError):
        cs.validate({**row, "value": -1})
    with pytest.raises(jsonschema.ValidationError):
        cs.validate({**row, "latitude": 52.1})  # no point-level fields allowed


def test_out_of_window_rows_are_counted_not_written() -> None:
    b = builder()
    assert (
        b.add(
            country="UK",
            period_end=date(2025, 7, 1),
            metric_id="public-points",
            value=1,
            unit="count",
            definition_id="uk-dft-evse-2026",
        )
        is None
    )
    assert b.dropped_out_of_validity == 1 and not b.rows
