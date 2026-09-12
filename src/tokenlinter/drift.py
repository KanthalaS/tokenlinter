"""Token-drift reports: diff two DTCG documents after alias resolution.

Comparing resolved values means an alias reference and its literal target
are treated as the same token — the classic false positive in drift checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tokenlinter.aliases import flatten_tokens, resolve_aliases


@dataclass
class DriftReport:
    """Structural differences between two token documents."""

    added: dict[str, Any] = field(default_factory=dict)
    removed: dict[str, Any] = field(default_factory=dict)
    changed: dict[str, tuple[Any, Any]] = field(default_factory=dict)
    unchanged: int = 0

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def compare_documents(base: Any, changed: Any) -> DriftReport:
    """Diff two documents on their alias-resolved effective values."""
    before = resolve_aliases(flatten_tokens(base)).resolved
    after = resolve_aliases(flatten_tokens(changed)).resolved
    report = DriftReport()
    for path, value in after.items():
        if path not in before:
            report.added[path] = value
    for path, value in before.items():
        if path not in after:
            report.removed[path] = value
    for path in before.keys() & after.keys():
        if before[path] != after[path]:
            report.changed[path] = (before[path], after[path])
        else:
            report.unchanged += 1
    return report


def format_drift(report: DriftReport) -> list[str]:
    """Human-readable lines for the drift report."""
    lines: list[str] = []
    for path, value in sorted(report.added.items()):
        lines.append(f"+ $.{path}: {value!r}")
    for path, value in sorted(report.removed.items()):
        lines.append(f"- $.{path}: {value!r}")
    for path, (before, after) in sorted(report.changed.items()):
        lines.append(f"~ $.{path}: {before!r} -> {after!r}")
    return lines
