"""WCAG contrast engine: parsing, luminance, ratios, checkpoints."""

from __future__ import annotations

import pytest

from tokenlinter.contrast import (
    contrast_ratio,
    lint_contrast,
    parse_color,
    relative_luminance,
)


def test_parse_hex_variants() -> None:
    assert parse_color("#fff") == (255, 255, 255)
    assert parse_color("#0a7d33") == (10, 125, 51)
    assert parse_color("#0A7D33") == (10, 125, 51)


def test_parse_rgb_and_rgba() -> None:
    assert parse_color("rgb(255, 0, 0)") == (255, 0, 0)
    assert parse_color("rgba(0, 0, 0, 0.5)") == (128, 128, 128)


def test_parse_named_and_invalid() -> None:
    assert parse_color("black") == (0, 0, 0)
    assert parse_color("white") == (255, 255, 255)
    assert parse_color("16px") is None
    assert parse_color(42) is None
    assert parse_color("not-a-color") is None


def test_relative_luminance_endpoints() -> None:
    assert relative_luminance((0, 0, 0)) == pytest.approx(0.0, abs=1e-4)
    assert relative_luminance((255, 255, 255)) == pytest.approx(1.0, abs=1e-4)


def test_black_on_white_is_max_contrast() -> None:
    assert contrast_ratio((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0, abs=0.1)


def test_red_fails_aa_but_passes_aa_large_on_white() -> None:
    ratio = contrast_ratio((255, 0, 0), (255, 255, 255))
    assert ratio == pytest.approx(4.0, abs=0.1)
    assert ratio < 4.5
    assert ratio >= 3.0


def test_mid_gray_fails_aa_on_white() -> None:
    # #777777 is the folk-standard near-failure: ratio ~4.48 < 4.5.
    doc = {"gray": {"$type": "color", "$value": "#777777"}}
    assert lint_contrast(doc) != []


def test_black_passes_all_levels_on_white() -> None:
    doc = {"ink": {"$type": "color", "$value": "#000000"}}
    assert lint_contrast(doc) == []
    assert lint_contrast(doc, level="aaa") == []


def test_white_token_fails_on_white() -> None:
    doc = {"paper": {"$type": "color", "$value": "#ffffff"}}
    problems = lint_contrast(doc)
    assert problems and "fails aa" in problems[0]


def test_aliased_color_checked_at_resolved_value() -> None:
    doc = {
        "ink": {"$type": "color", "$value": "#000000"},
        "text": {"$type": "color", "$value": "{ink}"},
    }
    assert lint_contrast(doc) == []


def test_unknown_level_and_background_errors() -> None:
    doc = {"a": {"$type": "color", "$value": "#000000"}}
    assert "unknown level" in lint_contrast(doc, level="nope")[0]
    assert "cannot parse background" in lint_contrast(doc, background="pinkish")[0]
