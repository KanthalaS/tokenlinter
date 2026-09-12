"""Alias resolution: flattening, dangling refs, cycles, resolved values."""

from __future__ import annotations

from tokenlinter.aliases import (
    flatten_tokens,
    lint_aliases,
    resolve_aliases,
)

DOC = {
    "color": {
        "brand": {"primary": {"$type": "color", "$value": "#0a7d33"}},
        "hover": {"$type": "color", "$value": "{color.brand.primary}"},
    },
    "spacing": {"md": {"$type": "dimension", "$value": "16px"}},
}


def test_flatten_tokens_maps_paths_to_tokens() -> None:
    flat = flatten_tokens(DOC)
    assert set(flat) == {"color.brand.primary", "color.hover", "spacing.md"}


def test_pure_alias_resolves_through_chain() -> None:
    doc = {"a": {"$value": "{b}"}, "b": {"$value": "{c}"}, "c": {"$value": "#000000"}}
    report = resolve_aliases(flatten_tokens(doc))
    assert report.errors == []
    assert report.resolved == {"a": "#000000", "b": "#000000", "c": "#000000"}


def test_non_string_leaves_resolve_as_is() -> None:
    doc = {"n": {"$type": "number", "$value": 42}}
    report = resolve_aliases(flatten_tokens(doc))
    assert report.errors == []
    assert report.resolved == {"n": 42}


def test_dangling_reference_reported() -> None:
    doc = {"a": {"$value": "{missing.target}"}}
    assert lint_aliases(doc) == [
        "$.a: dangling alias reference {missing.target} (target not found)"
    ]


def test_mixed_string_dangling_reference_reported() -> None:
    doc = {"a": {"$value": "1px solid {color.nope}"}}
    assert lint_aliases(doc) == [
        "$.a: dangling alias reference {color.nope} (target not found)"
    ]


def test_mixed_string_with_valid_ref_is_clean() -> None:
    doc = {"b": {"$value": "#fff"}, "a": {"$value": "1px solid {b}"}}
    assert lint_aliases(doc) == []


def test_self_reference_is_cyclic() -> None:
    doc = {"a": {"$value": "{a}"}}
    assert lint_aliases(doc) == ["$.a: cyclic alias reference: {a} -> {a}"]


def test_two_token_cycle_reported_once() -> None:
    doc = {"a": {"$value": "{b}"}, "b": {"$value": "{a}"}}
    assert lint_aliases(doc) == ["$.a: cyclic alias reference: {a} -> {b} -> {a}"]


def test_three_token_cycle_reported_once() -> None:
    doc = {"a": {"$value": "{b}"}, "b": {"$value": "{c}"}, "c": {"$value": "{a}"}}
    assert lint_aliases(doc) == [
        "$.a: cyclic alias reference: {a} -> {b} -> {c} -> {a}"
    ]


def test_mid_chain_dangling_anchored_at_direct_referrer() -> None:
    doc = {"a": {"$value": "{b}"}, "b": {"$value": "{ghost}"}}
    assert lint_aliases(doc) == [
        "$.b: dangling alias reference {ghost} (target not found)"
    ]


def test_whitespace_padded_alias_resolves() -> None:
    doc = {"b": {"$value": "#fff"}, "a": {"$value": "{ b }"}}
    report = resolve_aliases(flatten_tokens(doc))
    assert report.errors == []
    assert report.resolved["a"] == "#fff"
