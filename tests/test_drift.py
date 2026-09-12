"""Token-drift reports between two documents."""

from __future__ import annotations

from tokenlinter.drift import compare_documents, format_drift

BASE = {
    "color": {
        "brand": {"primary": {"$type": "color", "$value": "#0a7d33"}},
        "hover": {"$type": "color", "$value": "{color.brand.primary}"},
    },
    "spacing": {"md": {"$type": "dimension", "$value": "16px"}},
}


def test_identical_documents_have_no_drift() -> None:
    report = compare_documents(BASE, BASE)
    assert not report.has_drift
    assert report.unchanged == 3


def test_value_change_is_reported() -> None:
    changed = {
        "color": {
            "brand": {"primary": {"$type": "color", "$value": "#0b8a3a"}},
            "hover": {"$type": "color", "$value": "{color.brand.primary}"},
        },
        "spacing": {"md": {"$type": "dimension", "$value": "16px"}},
    }
    report = compare_documents(BASE, changed)
    assert report.has_drift
    # The alias follower's effective value changes too — drift is value-based.
    assert report.changed == {
        "color.brand.primary": ("#0a7d33", "#0b8a3a"),
        "color.hover": ("#0a7d33", "#0b8a3a"),
    }
    assert "~ $.color.brand.primary: '#0a7d33' -> '#0b8a3a'" in format_drift(report)


def test_added_and_removed_tokens() -> None:
    missing = {"spacing": {"md": {"$type": "dimension", "$value": "16px"}}}
    report = compare_documents(BASE, missing)
    assert set(report.removed) == {"color.brand.primary", "color.hover"}
    added = {"x": {"$value": "1"}, **BASE}
    report = compare_documents(BASE, added)
    assert set(report.added) == {"x"}


def test_alias_vs_literal_is_not_drift() -> None:
    # Same structure as BASE; only the hover representation differs
    # (alias vs literal) — resolved values match, so no drift.
    literal = {
        "color": {
            "brand": {"primary": {"$type": "color", "$value": "#0a7d33"}},
            "hover": {"$type": "color", "$value": "#0a7d33"},
        },
        "spacing": {"md": {"$type": "dimension", "$value": "16px"}},
    }
    report = compare_documents(BASE, literal)
    assert not report.has_drift
