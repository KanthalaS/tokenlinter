"""Repo tooling: pre-commit hook and bundled HTML example stay consistent."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pre_commit_config_validates_token_files() -> None:
    config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "repos:" in config
    assert "id: tokenlinter-validate" in config
    assert "entry: tokenlinter validate" in config


def test_bundled_style_guide_html_exists() -> None:
    page = (ROOT / "examples" / "style-guide.html").read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in page
    assert "Design Tokens" in page
