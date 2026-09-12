# tokenlinter

Python-native design-token QA. Validates design tokens in the
[W3C DTCG format](https://tr.designtokens.org/format/) and enforces WCAG
contrast, so design systems catch drift and accessibility regressions before
they ship.

**Status:** pre-alpha. DTCG structural checks (groups, token types) and
alias resolution are implemented; the WCAG contrast engine, token-drift
reports, and pre-commit hook are on the roadmap.

## What it checks

- DTCG structure: group nesting vs tokens, unknown `$type` values
- Alias references: `{path.to.token}` resolution against the token map,
  dangling targets, and cyclic chains
- (Roadmap) WCAG contrast ratios for color-token pairs

## Quick start

```console
uv sync --extra dev
uv run tokenlinter --version
uv run tokenlinter validate path/to/tokens.json
```

Pipe a document in instead of a file:

```console
cat path/to/tokens.json | uv run tokenlinter validate
```

Try the bundled examples:

```console
uv run tokenlinter validate examples/tokens.json           # valid → exit 0
uv run tokenlinter validate examples/tokens.invalid.json  # 8 violations → exit 1
```

## Development

```console
uv run pytest
uv run ruff check .
```

## License

MIT