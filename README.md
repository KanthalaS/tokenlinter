# tokenlinter

Python-native design-token QA. Validates design tokens in the
[W3C DTCG format](https://tr.designtokens.org/format/), enforces WCAG
contrast, spots token drift, and renders token docs as a style guide —
so design systems catch drift and accessibility regressions before they
ship.

**Status:** pre-alpha (v0.3.0). DTCG structure checks, alias resolution,
WCAG 2.x contrast checks, alias-aware drift reports, HTML style-guide
rendering, and a pre-commit hook are implemented.

## What it checks

- DTCG structure: group nesting vs tokens, unknown `$type` values
- Alias references: `{path.to.token}` resolution, dangling targets, cyclic chains
- WCAG 2.x contrast: every color token (resolved through aliases) against a
  background, at aa / aa-large / aaa / aaa-large checkpoints
- Token drift: added, removed, and changed tokens between two documents,
  compared on resolved values so alias-versus-literal is not a false positive

## Quick start

```console
uv sync --extra dev
uv run tokenlinter --version
```

Try the bundled examples:

```console
uv run tokenlinter validate examples/tokens.json           # valid → exit 0
uv run tokenlinter validate examples/tokens.invalid.json  # 8 violations → exit 1
```

Read the rendered style guide of the example tokens (`examples/style-guide.html`),
or render your own:

```console
uv run tokenlinter render examples/tokens.json -o style-guide.html
```

## Commands

```console
# validate a design-token document (structure, types, aliases); stdin works too
tokenlinter validate path/to/tokens.json
cat path/to/tokens.json | tokenlinter validate

# WCAG contrast of every color token against a background
tokenlinter contrast path/to/tokens.json --background "#ffffff" --level aa

# alias-aware drift between two token documents
tokenlinter drift base-tokens.json changed-tokens.json

# regenerate the HTML style guide from a token document
tokenlinter render path/to/tokens.json -o style-guide.html --title "My Tokens"
```

Exit codes: `0` = clean, `1` = problems found — CI and hooks rely on that.

## Pre-commit

```console
uv run pre-commit install
```

Every commit then validates any `tokens.json` / `token.json` file in the repo.
The same check runs in CI (`uv run pre-commit run --all-files`).

## Development

```console
uv run pytest
uv run ruff check .
```

## License

MIT