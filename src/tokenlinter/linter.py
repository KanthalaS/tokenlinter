"""One-pass linting: compose the structural and alias checks."""

from __future__ import annotations

from typing import Any

from tokenlinter import aliases
from tokenlinter.schema import validate_tokens


def lint(payload: Any) -> list[str]:
    """Return every problem found in a DTCG document, schema then aliases.

    New check families (e.g. the WCAG contrast engine) join here.
    """
    errors = validate_tokens(payload)
    errors.extend(aliases.lint_aliases(payload))
    return errors
