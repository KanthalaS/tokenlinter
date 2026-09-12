# tokenlinter

Python-native design-token QA. Validates design tokens in the
[W3C DTCG format](https://tr.designtokens.org/format/) and enforces WCAG
contrast, so design systems catch drift and accessibility regressions before
they ship.

**Status:** scaffold (pre-alpha). Roadmap: full DTCG schema validation, alias
resolution, WCAG contrast engine, token-drift reports, pre-commit hook and
GitHub Action.

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

Try the bundled example:

```console
uv run tokenlinter validate examples/tokens.json
```

## Development

```console
uv run pytest
uv run ruff check .
```

## License

MIT