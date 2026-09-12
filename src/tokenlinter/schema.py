"""DTCG (Design Tokens Community Group) structural validation.

Holds the structural slice: group nesting and token types. Alias rules live
in :mod:`tokenlinter.aliases`, and the WCAG contrast engine will join the
lint pipeline in a later milestone.

Spec reference: https://tr.designtokens.org/format/
"""

from __future__ import annotations

from typing import Any

# Keys reserved by the DTCG format at the token level.
RESERVED_KEYS = frozenset(
    {"$value", "$type", "$description", "$extensions", "$deprecated"}
)

# Token types recognised by the DTCG draft format.
KNOWN_TYPES = frozenset(
    {
        "border",
        "color",
        "cubicBezier",
        "dimension",
        "duration",
        "fontFamily",
        "fontWeight",
        "gradient",
        "number",
        "shadow",
        "string",
        "strokeStyle",
        "transition",
        "typography",
    }
)


def validate_tokens(payload: Any) -> list[str]:
    """Return human-readable problems in a DTCG token document.

    A document is a tree of groups; a node is a token when it carries a
    ``$value`` key. Returns an empty list when the document is clean.
    """
    if not isinstance(payload, dict):
        return ["root of a DTCG document must be a group object"]
    errors: list[str] = []
    _validate_group(payload, path="$", errors=errors)
    return errors


def _validate_group(group: dict[str, Any], *, path: str, errors: list[str]) -> None:
    for name, value in group.items():
        child_path = f"{path}.{name}"
        if name in RESERVED_KEYS:
            continue
        if not isinstance(value, dict):
            errors.append(
                f"{child_path}: expected a group or token object, "
                f"got {type(value).__name__}"
            )
            continue
        if "$value" in value:
            _validate_token(value, path=child_path, errors=errors)
        else:
            _validate_group(value, path=child_path, errors=errors)


def _validate_token(token: dict[str, Any], *, path: str, errors: list[str]) -> None:
    token_type = token.get("$type")
    if token_type is not None and token_type not in KNOWN_TYPES:
        known = ", ".join(sorted(KNOWN_TYPES))
        errors.append(f"{path}: unknown $type {token_type!r} (known types: {known})")
