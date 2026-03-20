"""
Tests für Coverage Strength und Coverage Quality.

covered / partial / gap / n/a und high / medium / low.
"""

from __future__ import annotations

import pytest

from scripts.qa.coverage_map_rules import (
    _compute_coverage_strength,
    compute_coverage_quality,
    aggregate_by_failure_class,
    aggregate_by_guard,
)


def test_coverage_strength_n_a_when_expected_zero() -> None:
    """coverage_strength: n/a wenn expected_min == 0."""
    assert _compute_coverage_strength(0, 0) == "n/a"
    assert _compute_coverage_strength(5, 0) == "n/a"


def test_coverage_strength_covered_when_count_ge_expected() -> None:
    """coverage_strength: covered wenn test_count >= expected_min."""
    assert _compute_coverage_strength(1, 1) == "covered"
    assert _compute_coverage_strength(5, 1) == "covered"


def test_coverage_strength_partial_when_count_between_zero_and_expected() -> None:
    """coverage_strength: partial wenn 0 < test_count < expected_min."""
    assert _compute_coverage_strength(1, 2) == "partial"
    assert _compute_coverage_strength(2, 5) == "partial"


def test_coverage_strength_gap_when_count_zero() -> None:
    """coverage_strength: gap wenn test_count == 0 und expected_min > 0."""
    assert _compute_coverage_strength(0, 1) == "gap"
    assert _compute_coverage_strength(0, 5) == "gap"


def test_failure_class_strength_gap_for_uncovered(minimal_inventory: dict) -> None:
    """failure_class: coverage_strength=gap für failure_class ohne catalog_bound Test."""
    result = aggregate_by_failure_class(minimal_inventory)
    # ui_state_drift hat keinen Test im minimal_inventory
    assert "ui_state_drift" in result
    assert result["ui_state_drift"]["coverage_strength"] == "gap"
    assert result["ui_state_drift"]["test_count"] == 0


def test_failure_class_strength_covered_for_covered(minimal_inventory: dict) -> None:
    """failure_class: coverage_strength=covered wenn catalog_bound Test vorhanden."""
    result = aggregate_by_failure_class(minimal_inventory)
    assert result["rag_silent_failure"]["coverage_strength"] == "covered"
    assert result["rag_silent_failure"]["test_count"] >= 1


def test_compute_coverage_quality_default() -> None:
    """coverage_quality: high/medium pro Axis bei niedrigem manual_review share."""
    quality = compute_coverage_quality({}, 0.1)
    assert quality["failure_class"] == "high"
    assert quality["test_domain"] == "high"
    assert quality["guard"] == "medium"
    assert quality["autopilot_recommendation"] == "medium"


def test_compute_coverage_quality_degraded_at_high_manual_review() -> None:
    """coverage_quality: high -> medium wenn manual_review_share > 0.3."""
    quality = compute_coverage_quality({}, 0.35)
    assert quality["failure_class"] == "medium"
    assert quality["test_domain"] == "medium"
    assert quality["guard"] == "medium"
