"""Smoke tests for the tokenlinter scaffold: package, CLI, schema stub."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from tokenlinter import __version__
from tokenlinter.cli import app

runner = CliRunner()


def test_package_metadata() -> None:
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 1


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_validate_valid_document_via_stdin() -> None:
    doc = json.dumps({"color": {"$type": "color", "$value": "#0a7d33"}})
    result = runner.invoke(app, ["validate"], input=doc)
    assert result.exit_code == 0
    assert "valid" in result.stdout


def test_validate_rejects_unknown_token_type() -> None:
    doc = json.dumps({"color": {"$type": "banana", "$value": "#0a7d33"}})
    result = runner.invoke(app, ["validate"], input=doc)
    assert result.exit_code == 1
    assert "unknown $type" in result.stdout


def test_validate_rejects_bad_root() -> None:
    result = runner.invoke(app, ["validate"], input="[1, 2, 3]")
    assert result.exit_code == 1
    assert "group object" in result.stdout
