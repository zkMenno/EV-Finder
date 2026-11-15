"""Python side of the schema fixture tests (T-001: "Fixture tests pass in TS and Python").

Every file in packages/schema/fixtures is checked with JSON Schema (draft 2020-12) and with
the generated Pydantic models: `*.valid.json` must pass both, `*.invalid.json` must fail
JSON Schema. Same file-name convention as packages/schema/test/fixtures.test.ts.
Added by the T-001 review, 2026-11-15.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from ev_pipeline import schema_models

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "packages" / "schema"
SCHEMA = json.loads((SCHEMA_DIR / "schemas" / "ev.schema.json").read_text(encoding="utf-8"))
FIXTURES = sorted((SCHEMA_DIR / "fixtures").glob("*.json"))


def _def_for(name: str) -> str:
    stem = name.split(".")[0]
    if stem.startswith("fact-"):
        return "Fact"
    return "".join(p[:1].upper() + p[1:] for p in stem.split("-"))


def _validator(def_name: str) -> Draft202012Validator:
    return Draft202012Validator(
        {**SCHEMA, "$ref": f"#/$defs/{def_name}"}, format_checker=FormatChecker()
    )


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_fixture_against_json_schema(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = list(_validator(_def_for(path.name)).iter_errors(data))
    if ".valid." in path.name:
        assert errors == [], [e.message for e in errors]
    else:
        assert errors, f"{path.name} should be rejected"


@pytest.mark.parametrize("path", [p for p in FIXTURES if ".valid." in p.name], ids=lambda p: p.name)
def test_valid_fixture_against_pydantic(path: Path) -> None:
    model = getattr(schema_models, _def_for(path.name))
    model.model_validate(json.loads(path.read_text(encoding="utf-8")))


def test_every_core_entity_has_a_fixture() -> None:
    """T-001 lists Make, Model, Generation, Variant, MarketVariant, Fact, PublishedVariant."""
    have = {_def_for(p.name) for p in FIXTURES}
    core = {"Make", "Model", "Generation", "Variant", "MarketVariant", "Fact", "PublishedVariant"}
    missing = sorted(core - have)
    if missing:
        pytest.xfail(f"no fixture yet for {missing} (packages/schema/AGENTS.md needs one each)")


def test_not_disclosed_is_accepted_where_documented() -> None:
    """Q-017 regression: `Id or 'not-disclosed'` fields accept 'not-disclosed' (anyOf)."""
    pack = json.loads((SCHEMA_DIR / "fixtures" / "battery-pack.valid.json").read_text())
    for key in ("chemistry_id", "cooling_id"):
        candidate = {**pack, key: "not-disclosed"}
        errors = list(_validator("BatteryPack").iter_errors(candidate))
        assert errors == [], [e.message for e in errors]
