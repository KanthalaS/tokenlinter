"""Alias resolution for DTCG token documents.

Resolves ``{path.to.token}`` references against a flat map of token paths
and reports dangling targets and cyclic chains. The resolved values are
exposed for later consumers — the WCAG contrast engine needs resolved
color values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

ALIAS_RE = re.compile(r"\{([^{}]*)\}")

# Sentinel marking a token whose value could not be resolved.
_UNDEFINED = object()


@dataclass
class AliasReport:
    """Outcome of resolving all aliases in one document."""

    resolved: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def flatten_tokens(payload: Any, *, root: str = "") -> dict[str, dict[str, Any]]:
    """Map every token path to its token dict.

    A node is a token when it carries ``$value``. Returned paths use DTCG
    reference style (``color.brand.primary``, no leading ``$``); the ``$``
    prefix appears only in user-facing messages. Groups are descended into;
    tokens are leaves.
    """
    flat: dict[str, dict[str, Any]] = {}

    def walk(node: Any, path: str) -> None:
        if not isinstance(node, dict):
            return
        if "$value" in node:
            flat[path] = node
            return
        for name, child in node.items():
            if name.startswith("$"):
                continue
            walk(child, f"{path}.{name}" if path else name)

    walk(payload, root)
    return flat


def find_references(value: str) -> list[str]:
    """Return the target paths inside a string value, e.g. ``{a.b}``."""
    return ALIAS_RE.findall(value)


def is_pure_alias(value: str) -> tuple[bool, str]:
    """Return True plus the target when the whole value is one alias."""
    refs = find_references(value)
    if len(refs) == 1 and value.strip() == "{" + refs[0] + "}":
        return True, refs[0]
    return False, ""


def resolve_aliases(flat: dict[str, dict[str, Any]]) -> AliasReport:
    """Resolve aliases in a flattened token map.

    Pure aliases (``{path}`` as the entire value) are followed to their
    concrete leaf. Mixed strings keep their embedded references but are
    flagged for dangling targets. Cycles and dangling references are
    reported once per chain, anchored at the token that fails to resolve.
    """
    report = AliasReport()
    resolved: dict[str, Any] = {}
    errors: list[str] = []
    memo: dict[str, Any] = {}

    def is_concrete(value: Any) -> bool:
        return not isinstance(value, str)

    def label(path: str) -> str:
        return f"$.{path}" if path else "$"

    for path in flat:
        if path in memo:
            continue
        chain = [path]
        visited = {path}
        current = path
        while True:
            value = flat[current].get("$value")
            if is_concrete(value):
                for entry in chain:
                    memo[entry] = value
                    resolved[entry] = value
                break
            pure, ref = is_pure_alias(value)
            if not pure:
                # Mixed string: keep as-is, flag any dangling refs inside.
                for candidate in find_references(value):
                    candidate = candidate.strip()
                    if candidate and candidate not in flat:
                        errors.append(
                            f"{label(current)}: dangling alias reference "
                            f"{{{candidate}}} (target not found)"
                        )
                for entry in chain:
                    memo[entry] = value
                    resolved[entry] = value
                break
            ref = ref.strip()
            if not ref:
                errors.append(f"{label(current)}: empty alias reference {{}}")
                for entry in chain:
                    memo[entry] = _UNDEFINED
                break
            if ref not in flat:
                errors.append(
                    f"{label(current)}: dangling alias reference {{{ref}}} (target not found)"
                )
                for entry in chain:
                    memo[entry] = _UNDEFINED
                break
            if ref in visited:
                cycle = chain[chain.index(ref) :] + [ref]
                dotted = " -> ".join(f"{{{entry}}}" for entry in cycle)
                errors.append(f"{label(path)}: cyclic alias reference: {dotted}")
                for entry in chain:
                    memo[entry] = _UNDEFINED
                break
            chain.append(ref)
            visited.add(ref)
            current = ref

    report.resolved = resolved
    report.errors = errors
    return report


def lint_aliases(payload: Any) -> list[str]:
    """Run alias checks over a whole document; return problems only."""
    return resolve_aliases(flatten_tokens(payload)).errors
