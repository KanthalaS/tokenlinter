"""Command-line entrypoint for tokenlinter."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from tokenlinter import __version__
from tokenlinter.contrast import lint_contrast
from tokenlinter.drift import compare_documents, format_drift
from tokenlinter.linter import lint
from tokenlinter.render import render_style_guide

app = typer.Typer(
    name="tokenlinter",
    help="Validate design tokens (W3C DTCG), enforce WCAG contrast, spot drift.",
    no_args_is_help=True,
)
console = Console(soft_wrap=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"tokenlinter {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: B008
        False,
        "--version",
        "-V",
        help="Show the tokenlinter version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """tokenlinter — design-token QA for design systems."""


def _load_document(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        console.print(f"[red]Cannot read {path}: {exc}[/red]")
        raise typer.Exit(1) from exc
    if not isinstance(payload, dict):
        console.print("[red]Root of a DTCG document must be a group object.[/red]")
        raise typer.Exit(1)
    return payload


@app.command()
def validate(
    token_file: Path | None = typer.Argument(  # noqa: B008
        None,
        help="Path to a DTCG design-token JSON file. Reads stdin when omitted.",
    ),
) -> None:
    """Validate a design-token document: structure, types, aliases."""
    if token_file is None:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            console.print(f"[red]Invalid JSON on stdin: {exc}[/red]")
            raise typer.Exit(1) from exc
    else:
        payload = _load_document(token_file)

    errors = lint(payload)
    if errors:
        console.print(f"[red]Found {len(errors)} problem(s):[/red]")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(1)
    console.print("[green]✓[/green] DTCG document is valid.")


@app.command()
def contrast(
    token_file: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to a DTCG design-token JSON file.",
    ),
    background: str = typer.Option(  # noqa: B008
        "#ffffff",
        "--background",
        "-b",
        help="Background color tokens are checked against.",
    ),
    level: str = typer.Option(  # noqa: B008
        "aa",
        "--level",
        "-l",
        help="WCAG checkpoint: aa, aa-large, aaa, aaa-large.",
    ),
) -> None:
    """Check color-token contrast against a background (WCAG 2.x)."""
    payload = _load_document(token_file)
    problems = lint_contrast(payload, background=background, level=level)
    if problems:
        console.print(f"[red]{len(problems)} contrast failure(s):[/red]")
        for problem in problems:
            console.print(f"  [red]✗[/red] {problem}")
        raise typer.Exit(1)
    console.print("[green]✓[/green] All color tokens pass contrast.")


@app.command()
def drift(
    base: Path = typer.Argument(..., help="Base design-token file."),  # noqa: B008
    changed: Path = typer.Argument(  # noqa: B008
        ..., help="Changed design-token file to compare against base."
    ),
) -> None:
    """Report token drift between two documents (alias-aware)."""
    report = compare_documents(_load_document(base), _load_document(changed))
    if not report.has_drift:
        console.print(
            f"[green]✓[/green] No drift: {report.unchanged} token(s) unchanged."
        )
        return
    console.print(
        f"[yellow]{len(report.added)} added, {len(report.removed)} removed, "
        f"{len(report.changed)} changed[/yellow]"
    )
    for line in format_drift(report):
        console.print(f"  {line}")
    raise typer.Exit(1)


@app.command()
def render(
    token_file: Path = typer.Argument(  # noqa: B008
        ..., help="Path to a DTCG design-token JSON file."
    ),
    output: Path = typer.Option(  # noqa: B008
        Path("style-guide.html"),
        "--output",
        "-o",
        help="Output HTML file path.",
    ),
    title: str = typer.Option(  # noqa: B008
        "Design Tokens",
        "--title",
        "-t",
        help="Page title for the generated style guide.",
    ),
) -> None:
    """Render a standalone HTML style guide from a token document."""
    payload = _load_document(token_file)
    output.write_text(render_style_guide(payload, title=title), encoding="utf-8")
    console.print(f"[green]✓[/green] Wrote {output}")
