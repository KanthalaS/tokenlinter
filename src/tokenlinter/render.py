"""Static HTML style-guide renderer for DTCG token documents.

Turns a token document into one self-contained HTML page with color
swatches, spacing bars, typography previews — using alias-resolved values
so every card shows the effective token value.
"""

from __future__ import annotations

import html
import re
from typing import Any

from tokenlinter.aliases import flatten_tokens, resolve_aliases
from tokenlinter.contrast import parse_color, relative_luminance

_PX_RE = re.compile(r"^([\d.]+)\s*px$")

_CSS = """
:root { color-scheme: light; }
body { font-family: "Inter", system-ui, -apple-system, sans-serif; margin: 0;
       background: #f6f7f9; color: #1f2933; }
header { padding: 2.5rem 2rem; background: #1f2933; color: #fff; }
header h1 { margin: 0; font-size: 1.5rem; }
header p { margin: 0.5rem 0 0; opacity: 0.7; font-size: 0.85rem; }
main { padding: 2rem; max-width: 64rem; margin: 0 auto; }
section { margin-bottom: 2.5rem; }
h2 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
     color: #616e7c; margin: 0 0 0.75rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
        gap: 1rem; }
.swatch { border-radius: 8px; padding: 1rem 1rem 0.8rem;
          box-shadow: 0 1px 2px rgb(0 0 0 / 12%); min-height: 4.5rem; }
.swatch .name { font-weight: 600; font-size: 0.9rem; }
.swatch .value { font-size: 0.75rem; opacity: 0.75; }
.bar { height: 1.5rem; background: #0a7d33; border-radius: 4px;
       margin: 0.5rem 0 0.25rem; min-width: 2px; }
.space { display: flex; align-items: baseline; justify-content: space-between;
         font-size: 0.85rem; }
.row { display: flex; justify-content: space-between; padding: 0.5rem 0;
       border-bottom: 1px solid #e4e7eb; font-size: 0.9rem; }
.row .name { color: #616e7c; }
.mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
.type-sample { margin: 0.75rem 0; }
""".strip()


def _swatch_text_color(color: tuple[int, int, int]) -> str:
    return "#1a1a1a" if relative_luminance(color) > 0.45 else "#ffffff"


def _color_section(tokens: list[tuple[str, Any]]) -> str:
    cards: list[str] = []
    for name, value in tokens:
        color = parse_color(value)
        if color is None:
            continue
        text = _swatch_text_color(color)
        cards.append(
            f'<div class="swatch" style="background:{html.escape(value)};'
            f'color:{text}">'
            f'<div class="name">{html.escape(name)}</div>'
            f'<div class="value mono">{html.escape(str(value))}</div>'
            f"</div>"
        )
    if not cards:
        return ""
    return (
        "<section><h2>Color</h2><div class=\"grid\">"
        + "".join(cards)
        + "</div></section>"
    )


def _spacing_section(tokens: list[tuple[str, Any]]) -> str:
    rows: list[str] = []
    for name, value in tokens:
        match = _PX_RE.match(str(value))
        if not match:
            continue
        px = float(match.group(1))
        width = min(px * 4, 240)
        rows.append(
            f'<div class="bar" style="width:{max(width, 2):.0f}px"></div>'
            f'<div class="space"><span>{html.escape(name)}</span>'
            f'<span class="mono">{html.escape(str(value))}</span></div>'
        )
    if not rows:
        return ""
    return "<section><h2>Spacing</h2>" + "".join(rows) + "</section>"


def _typography_section(tokens: list[tuple[str, Any]]) -> str:
    font_stack = "system-ui, sans-serif"
    weight = 400
    for name, value in tokens:
        if name.endswith("font-family") or "family" in name:
            if isinstance(value, list):
                font_stack = ", ".join(str(part) for part in value)
            elif isinstance(value, str):
                font_stack = value
        elif name.endswith("weight") or "weight" in name:
            try:
                weight = int(value)
            except (TypeError, ValueError):
                continue
    style = f"font-family:{font_stack};font-weight:{weight};"
    return (
        "<section><h2>Typography</h2>"
        f'<div class="type-sample" style="{style}">'
        "The quick brown fox jumps over the lazy dog"
        "</div>"
        f'<div class="mono" style="font-size:0.8rem;color:#616e7c">'
        f"{html.escape(font_stack)}, weight {weight}</div>"
        "</section>"
    )


def _table_section(group: str, tokens: list[tuple[str, Any]]) -> str:
    rows = "".join(
        f'<div class="row"><span class="name">{html.escape(name)}</span>'
        f'<span class="mono">{html.escape(str(value))}</span></div>'
        for name, value in tokens
    )
    return f"<section><h2>{html.escape(group)}</h2>{rows}</section>"


def render_style_guide(payload: Any, *, title: str = "Design Tokens") -> str:
    """Return a standalone HTML style guide for a token document."""
    resolved = resolve_aliases(flatten_tokens(payload)).resolved
    groups: dict[str, list[tuple[str, Any]]] = {}
    for path, value in resolved.items():
        group, _, name = path.partition(".")
        groups.setdefault(group, []).append((name or path, value))

    sections: list[str] = []
    for group, tokens in sorted(groups.items()):
        if group == "color":
            section = _color_section(tokens)
        elif group == "spacing":
            section = _spacing_section(tokens)
        elif group in {"typography", "type"}:
            section = _typography_section(tokens)
        else:
            section = _table_section(group, tokens)
        if section:
            sections.append(section)

    count = len(resolved)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        f"<header><h1>{html.escape(title)}</h1>"
        f"<p>{count} resolved tokens</p></header>\n"
        f"<main>\n{''.join(sections)}\n</main>\n</body>\n</html>\n"
    )
