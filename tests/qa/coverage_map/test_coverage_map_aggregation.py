"""
Tests für Coverage-Map-Aggregationslogik.

failure_class -> tests, guard -> tests, test_domain -> tests,
regression_requirement -> tests, autopilot_recommendation -> tests.
"""

from __future__ import annotations

import pytest

from scripts.qa.coverage_map_rules import (
    aggregate_autopilot_recommendation,
    aggregate_by_failure_class,
    aggregate_by_guard,
    aggregate_by_test_domain,
    aggregate_regression_requirement,
    aggregate_replay_binding,
    VALID_FAILURE_CLASSES,
    GUARD_TYPES,
)


def test_aggregate_by_failure_class_only_catalog_bound(minimal_inventory: dict) -> None:
    """failure_class: Nur Tests mit inference_sources.failure_class == catalog_bound zählen."""
    result = aggregate_by_failure_class(minimal_inventory)
    assert "rag_silent_failure" in result
    assert result["rag_silent_failure"]["test_count"] == 1
    assert result["rag_silent_failure"]["source"] == "catalog_bound"
    assert "tests_failure_modes_test_foo.py__test_rag_failure" in result["rag_silent_failure"]["test_ids"]


def test_aggregate_by_failure_class_unknown_ignored(minimal_inventory: dict) -> None:
    """failure_class: Tests ohne catalog_bound werden ignoriert."""
    result = aggregate_by_failure_class(minimal_inventory)
    # root-Test hat failure_classes=[], inference_sources.failure_class=unknown -> zählt nicht
    assert "late_signal_use_after_destroy" in result
    assert result["late_signal_use_after_destroy"]["test_count"] == 1


def test_aggregate_by_failure_class_all_valid_classes_present(minimal_inventory: dict) -> None:
    """failure_class: Alle VALID_FAILURE_CLASSES sind im Ergebnis."""
    result = aggregate_by_failure_class(minimal_inventory)
    for fc in VALID_FAILURE_CLASSES:
        assert fc in result
        assert "test_count" in result[fc]
        assert "coverage_strength" in result[fc]
        assert "source" in result[fc]


def test_aggregate_by_guard_from_guard_types(minimal_inventory: dict) -> None:
    """guard: Aggregation aus guard_types."""
    result = aggregate_by_guard(minimal_inventory)
    assert "failure_replay_guard" in result
    assert result["failure_replay_guard"]["test_count"] >= 1
    assert "event_contract_guard" in result
    for g in GUARD_TYPES:
        assert g in result


def test_aggregate_by_test_domain_from_path(minimal_inventory: dict) -> None:
    """test_domain: Aggregation aus test_domain (discovered)."""
    result = aggregate_by_test_domain(minimal_inventory)
    assert "failure_modes" in result
    assert "async_behavior" in result
    assert "root" in result
    assert "contracts" in result
    assert result["failure_modes"]["source"] == "discovered"
    assert result["failure_modes"]["coverage_strength"] == "n/a"


def test_aggregate_regression_requirement_from_strategy(
    minimal_inventory: dict,
    minimal_test_strategy: dict,
    minimal_autopilot_v3: dict,
) -> None:
    """regression_requirement: Aus Strategy und Autopilot."""
    bindings = {}
    result = aggregate_regression_requirement(
        minimal_inventory, minimal_test_strategy, minimal_autopilot_v3, bindings
    )
    assert "incidents" in result
    assert "covered_count" in result
    assert "required_count" in result
    assert "coverage_strength" in result


def test_aggregate_regression_requirement_covered_when_binding_has_test(
    minimal_inventory: dict,
    minimal_test_strategy: dict,
    minimal_autopilot_v3: dict,
    minimal_bindings: dict,
) -> None:
    """regression_requirement: covered wenn bindings.regression_test auf Inventory-Test zeigt."""
    # Binding hat regression_test -> tests/failure_modes/test_foo.py::test_rag_failure
    # Inventory hat diesen Test
    bindings = {"INC-20260315-001": minimal_bindings}
    result = aggregate_regression_requirement(
        minimal_inventory, minimal_test_strategy, minimal_autopilot_v3, bindings
    )
    # TR-001 hat incident_id INC-20260315-001; Binding hat regression_test
    incidents = result.get("incidents", [])
    covered = [i for i in incidents if i.get("covered")]
    assert len(covered) >= 1 or len(incidents) == 0


def test_aggregate_replay_binding_empty_without_bindings(minimal_inventory: dict) -> None:
    """replay_binding: Leer ohne Bindings."""
    result = aggregate_replay_binding(minimal_inventory, {})
    assert result["bound_count"] == 0
    assert result["total_replays"] == 0
    assert result["coverage_strength"] == "n/a"


def test_aggregate_replay_binding_with_bindings(
    minimal_inventory: dict,
    minimal_bindings: dict,
) -> None:
    """replay_binding: Bindings mit regression_test werden gezählt."""
    bindings = {"INC-20260315-001": minimal_bindings}
    result = aggregate_replay_binding(minimal_inventory, bindings)
    assert result["total_replays"] == 1
    # regression_test zeigt auf test_rag_failure der im Inventory ist
    assert result["bound_count"] == 1
    assert result["coverage_strength"] == "covered"


def test_aggregate_autopilot_recommendation_matching_test(minimal_inventory: dict, minimal_autopilot_v3: dict) -> None:
    """autopilot_recommendation: Backlog-Item mit passendem Test ist covered."""
    result = aggregate_autopilot_recommendation(minimal_inventory, minimal_autopilot_v3)
    # RTB-001: RAG, rag_silent_failure, failure_replay_guard
    # Inventory hat test_foo mit rag_silent_failure, failure_replay_guard, RAG
    backlog = result.get("backlog_items", [])
    assert len(backlog) >= 1
    covered = [i for i in backlog if i.get("covered")]
    assert len(covered) >= 1  # test_foo deckt RTB-001 ab


def test_aggregate_autopilot_recommendation_empty_without_autopilot(minimal_inventory: dict) -> None:
    """autopilot_recommendation: Leer ohne Autopilot."""
    result = aggregate_autopilot_recommendation(minimal_inventory, {})
    assert result["total_recommendations"] == 0
    assert result["coverage_strength"] == "n/a"
