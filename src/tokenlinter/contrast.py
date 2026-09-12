"""WCAG 2.x contrast engine for resolved design tokens.

Computes relative luminance and contrast ratios and flags color tokens that
fail the requested AA/AAA checkpoint against a background color. Works on
alias-resolved values, so aliased colors are checked at their effective
value.
"""

from __future__ import annotations

import re
from typing import Any

from tokenlinter.aliases import flatten_tokens, resolve_aliases

# WCAG 2.x minimum contrast ratios.
AA_NORMAL = 4.5
AA_LARGE = 3.0
AAA_NORMAL = 7.0
AAA_LARGE = 4.5

THRESHOLDS = {
    "aa": AA_NORMAL,
    "aa-large": AA_LARGE,
    "aaa": AAA_NORMAL,
    "aaa-large": AAA_LARGE,
}

_HEX_RE = re.compile(r"^#([0-9a-f]{3}|[0-9a-f]{6})$")
_RGB_RE = re.compile(
    r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})"
    r"(?:\s*,\s*([0-9.]+))?\s*\)$"
)

# A small subset of CSS named colors actually used in token files.
NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "silver": (192, 192, 192),
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
}


def parse_color(value: Any) -> tuple[int, int, int] | None:
    """Parse a CSS-ish color string into sRGB ints, or None when unsupported."""
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    match = _HEX_RE.match(text)
    if match:
        digits = match.group(1)
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        red = int(digits[0:2], 16)
        green = int(digits[2:4], 16)
        blue = int(digits[4:6], 16)
        return (red, green, blue)
    match = _RGB_RE.match(text)
    if match:
        red = int(match.group(1))
        green = int(match.group(2))
        blue = int(match.group(3))
        alpha = float(match.group(4) or 1.0)
        if alpha < 1.0:
            # Simplification: composite the translucent color over white.
            red = round(alpha * red + (1 - alpha) * 255)
            green = round(alpha * green + (1 - alpha) * 255)
            blue = round(alpha * blue + (1 - alpha) * 255)
        return (red, green, blue)
    return None


def srgb_to_linear(channel: int) -> float:
    """Convert one sRGB channel (0-255) to linear light."""
    value = channel / 255.0
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(color: tuple[int, int, int]) -> float:
    """WCAG 2.x relative luminance in [0, 1]."""
    red, green, blue = (srgb_to_linear(channel) for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG contrast ratio between two colors, 1:1 to 21:1."""
    light, dark = sorted(
        (relative_luminance(fg), relative_luminance(bg)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def lint_contrast(
    payload: Any, *, background: str = "#ffffff", level: str = "aa"
) -> list[str]:
    """Check every color token against one background; return problems."""
    if level not in THRESHOLDS:
        return [
            f"unknown level {level!r} "
            f"(choose from {', '.join(sorted(THRESHOLDS))})"
        ]
    bg = parse_color(background)
    if bg is None:
        return [f"cannot parse background color {background!r}"]
    minimum = THRESHOLDS[level]
    resolved = resolve_aliases(flatten_tokens(payload)).resolved
    problems: list[str] = []
    for path, value in resolved.items():
        color = parse_color(value)
        if color is None:
            continue  # not a color token
        ratio = contrast_ratio(color, bg)
        if ratio < minimum:
            problems.append(
                f"$.{path}: contrast {ratio:.2f}:1 on {background} fails {level} "
                f"(minimum {minimum:.1f}:1)"
            )
    return problems
