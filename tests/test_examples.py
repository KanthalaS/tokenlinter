"""Guard the bundled example fixtures so the repo always ships working demos."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from tokenlinter.cli import app

runner = CliRunner()
EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_valid_example_passes() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "tokens.json")])
    assert result.exit_code == 0
    assert "valid" in result.stdout


def test_invalid_example_fails_with_eight_violations() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "tokens.invalid.json")])
    assert result.exit_code == 1
    assert "Found 8 problem(s)" in result.stdout


@pytest.mark.parametrize(
    "expected",
    [
        "$.color.brand.primary-hover: empty alias reference {}",
        "$.color.brand.missing-target: dangling alias reference "
        "{color.brand.does-not-exist} (target not found)",
        "$.color.mystery: unknown $type 'banana'",
        "$.color.typed-as-number: unknown $type 77",
        "$.spacing.xs: expected a group or token object, got str",
        "$.radius.pill: unknown $type 'radius'",
        "$.typography.font-size-sm: unknown $type 'fontSize'",
        "$.mode.a: cyclic alias reference: {mode.a} -> {mode.b} -> {mode.a}",
    ],
)
def test_invalid_example_reports_each_violation(expected: str) -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "tokens.invalid.json")])
    assert expected in result.stdout
