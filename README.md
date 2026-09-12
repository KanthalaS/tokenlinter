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

## Install

```console
pip install tokenlinter
```

or from source with uv:

```console
uv sync --extra dev
uv run tokenlinter --version
```

## Quick start

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

## Publishing to PyPI

Building and uploading is handled by `uv publish`. CI publishes automatically
when a `v*` tag is pushed:

```console
git tag v0.3.0 && git push origin v0.3.0
```

- Set the `PYPI_API_TOKEN` repository secret (a PyPI API token with upload
  scope on the `tokenlinter` project) in Settings → Secrets and variables →
  Actions. Without it the publish job fails at upload — tests still pass.
- Local alternative: `uv build && UV_PUBLISH_TOKEN=<token> uv publish`.
- TestPyPI dry run: `UV_PUBLISH_URL=https://test.pypi.org/legacy/ uv publish`.

The version must match the released tag (`pyproject.toml` → `version`), and CI
runs `uv build` so wheel and sdist are always built from the pushed commit.

## Development

```console
uv run pytest
uv run ruff check .
```

## License

MIT