"""Smoke tests: package imports, CLI works, core deps are installed. No network."""

import importlib

import pytest

import ev_pipeline
from ev_pipeline.cli import build_parser, main


def test_version_is_a_string() -> None:
    assert isinstance(ev_pipeline.__version__, str)
    assert ev_pipeline.__version__


def test_cli_version_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == ev_pipeline.__version__


def test_cli_requires_a_subcommand() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


@pytest.mark.parametrize("module", ["pydantic", "duckdb", "pyarrow", "yaml", "httpx", "jsonschema"])
def test_core_dependency_importable(module: str) -> None:
    importlib.import_module(module)
