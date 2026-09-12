"""HTML style-guide rendering."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from tokenlinter.cli import app
from tokenlinter.render import render_style_guide

DOC = {
    "color": {
        "brand": {"primary": {"$type": "color", "$value": "#0a7d33"}},
        "text": {"$type": "color", "$value": "{color.brand.primary}"},
    },
    "spacing": {"md": {"$type": "dimension", "$value": "16px"}},
    "typography": {
        "font-family": {"$type": "fontFamily", "$value": ["Inter", "system-ui"]},
        "font-weight-bold": {"$type": "fontWeight", "$value": 700},
    },
}

runner = CliRunner()


def test_render_contains_sections_and_resolved_values() -> None:
    page = render_style_guide(DOC, title="My Tokens")
    assert "<!DOCTYPE html>" in page
    assert "My Tokens" in page
    assert "Color" in page
    assert "#0a7d33" in page  # alias resolved to its effective value
    assert "16px" in page
    assert "Inter" in page


def test_render_cli_writes_file(tmp_path: Path) -> None:
    token_file = tmp_path / "tokens.json"
    token_file.write_text('{"color": {"ink": {"$value": "#000000"}}}')
    out = tmp_path / "guide.html"
    result = runner.invoke(app, ["render", str(token_file), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "ink" in out.read_text(encoding="utf-8")
