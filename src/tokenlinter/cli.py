"""Command-line entrypoint for tokenlinter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from tokenlinter import __version__
from tokenlinter.schema import validate_tokens

app = typer.Typer(
    name="tokenlinter",
    help="Validate design tokens (W3C DTCG) and enforce WCAG contrast.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"tokenlinter {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the tokenlinter version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """tokenlinter — design-token QA for design systems."""


@app.command()
def validate(
    token_file: Path | None = typer.Argument(  # noqa: B008
        None,
        help="Path to a DTCG design-token JSON file. Reads stdin when omitted.",
    ),
) -> None:
    """Validate a design-token document against the DTCG rules."""
    if token_file is None:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            console.print(f"[red]Invalid JSON on stdin: {exc}[/red]")
            raise typer.Exit(1) from exc
    else:
        try:
            payload = json.loads(token_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            console.print(f"[red]Cannot read {token_file}: {exc}[/red]")
            raise typer.Exit(1) from exc

    errors = validate_tokens(payload)
    if errors:
        console.print(f"[red]Found {len(errors)} problem(s):[/red]")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
        raise typer.Exit(1)
    console.print("[green]✓[/green] DTCG document is valid.")
