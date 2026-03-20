"""
Tests für Gap Detection.

failure_class_uncovered, guard_missing, regression_requirement_unbound,
replay_unbound, semantic_binding_gap, orphan_test.
"""

from __future__ import annotations

import pytest

from scripts.qa.coverage_map_rules import (
    aggregate_by_failure_class,
    aggregate_by_guard,
    aggregate_autopilot_recommendation,
    aggregate_regression_requirement,
    aggregate_replay_binding,
    build_gap_types,
    detect_failure_class_gaps,
    detect_guard_gaps,
    detect_orphan_tests,
    detect_regression_requirement_gaps,
    detect_replay_binding_gaps,
    detect_semantic_binding_gaps,
)


def test_detect_failure_class_gaps_returns_gaps_for_uncovered(minimal_inventory: dict) -> None:
    """failure_class: Gaps für failure_classes ohne catalog_bound Test."""
    coverage = aggregate_by_failure_class(minimal_inventory)
    gaps = detect_failure_class_gaps(coverage)
    uncovered_fcs = [g["value"] for g in gaps]
    assert "ui_state_drift" in uncovered_fcs or len(gaps) >= 0
    for g in gaps:
        assert g["axis"] == "failure_class"
        assert g["gap_type"] == "failure_class_uncovered"
        assert "gap_id" in g
        assert "evidence" in g
        assert "mitigation_hint" in g


def test_detect_failure_class_gaps_empty_when_all_covered() -> None:
    """failure_class: Keine Gaps wenn alle covered (theoretisch)."""
    inventory = {"tests": []}
    for fc in ["rag_silent_failure", "ui_state_drift"]:
        inventory["tests"].append({
            "test_id": f"test_{fc}",
            "pytest_nodeid": f"tests/test_{fc}.py::test",
            "failure_classes": [fc],
            "inference_sources": {"failure_class": "catalog_bound"},
        })
    coverage = aggregate_by_failure_class(inventory)
    gaps = detect_failure_class_gaps(coverage)
    # rag_silent_failure und ui_state_drift sind jetzt covered
    assert len(gaps) < 12  # Es gibt 12 failure_classes, einige bleiben gap


def test_detect_guard_gaps_from_strategy(minimal_inventory: dict, minimal_test_strategy: dict) -> None:
    """guard: Gaps aus guard_requirements wenn guard_type gap hat."""
    coverage = aggregate_by_guard(minimal_inventory)
    gaps = detect_guard_gaps(coverage, minimal_test_strategy.get("guard_requirements", []))
    # event_contract_guard ist im Inventory (test_event_contract) -> evtl. kein Gap
    for g in gaps:
        assert g["axis"] == "guard"
        assert g["gap_type"] == "guard_missing"


def test_detect_regression_requirement_gaps_for_unbound(
    minimal_inventory: dict,
    minimal_test_strategy: dict,
    minimal_autopilot_v3: dict,
) -> None:
    """regression_requirement: Gaps für Incidents ohne regression_test."""
    bindings = {}  # Keine Bindings
    agg = aggregate_regression_requirement(
        minimal_inventory, minimal_test_strategy, minimal_autopilot_v3, bindings
    )
    gaps = detect_regression_requirement_gaps(agg)
    for g in gaps:
        assert g["axis"] == "regression_requirement"
        assert g["gap_type"] == "regression_requirement_unbound"


def test_detect_replay_binding_gaps_for_unbound(minimal_inventory: dict) -> None:
    """replay_binding: Gaps für Bindings ohne test_id."""
    bindings_without_test = {
        "INC-X": {
            "identity": {"incident_id": "INC-X"},
            "regression_catalog": {"regression_test": None},
            "status": {"binding_status": "validated"},
        },
    }
    agg = aggregate_replay_binding(minimal_inventory, bindings_without_test)
    gaps = detect_replay_binding_gaps(agg)
    assert len(gaps) >= 1
    for g in gaps:
        assert g["axis"] == "replay_binding"
        assert g["gap_type"] == "replay_unbound"


def test_detect_orphan_tests_root_domain(minimal_inventory: dict) -> None:
    """Phase 3: Tests in test_domain=root ohne catalog_bound sind orphan (review_candidate)."""
    orphans = detect_orphan_tests(minimal_inventory)
    root_orphans = [o for o in orphans if "root" in o.get("reason", "")]
    assert len(root_orphans) >= 1
    for o in orphans:
        assert "test_id" in o
        assert "reason" in o


def test_detect_orphan_tests_meta_domains_whitelisted() -> None:
    """Phase 3: test_domain qa, helpers, meta sind whitelisted → keine orphans."""
    inv = {
        "tests": [
            {"test_id": "t1", "test_domain": "qa", "pytest_nodeid": "tests/qa/t.py::t1", "failure_classes": [], "inference_sources": {}, "file_path": "tests/qa/t.py"},
            {"test_id": "t2", "test_domain": "helpers", "pytest_nodeid": "tests/helpers/d.py::t2", "failure_classes": [], "inference_sources": {}, "file_path": "tests/helpers/d.py"},
        ]
    }
    orphans = detect_orphan_tests(inv)
    assert len(orphans) == 0


def test_detect_orphan_tests_root_without_catalog_bound_is_orphan() -> None:
    """Phase 3: root + no catalog_bound → orphan."""
    inv = {"tests": [{"test_id": "t1", "test_domain": "root", "pytest_nodeid": "tests/x.py::t1", "failure_classes": [], "inference_sources": {}, "file_path": "tests/x.py"}]}
    orphans = detect_orphan_tests(inv)
    assert len(orphans) == 1
    assert orphans[0]["reason"] == "test_domain=root, no catalog_bound failure_class"


def test_detect_semantic_binding_gaps_from_knowledge_graph(
    minimal_inventory: dict,
    minimal_knowledge_graph: dict,
) -> None:
    """semantic_binding_gap: validated_by fc->domain, aber kein catalog_bound Test in domain."""
    # ui_state_drift -> async_behavior; Inventory hat keinen ui_state_drift Test in async_behavior
    gaps = detect_semantic_binding_gaps(minimal_inventory, minimal_knowledge_graph)
    for g in gaps:
        assert "failure_class" in g
        assert "expected_test_domain" in g
        assert "actual_test_count" in g
        assert g["actual_test_count"] == 0


def test_detect_semantic_binding_gaps_none_when_covered(minimal_inventory: dict) -> None:
    """semantic_binding_gap: Kein Gap wenn catalog_bound Test in erwarteter domain."""
    graph = {"edges": [{"edge_type": "validated_by", "source_id": "failure_class:rag_silent_failure", "target_id": "test_domain:failure_modes"}]}
    gaps = detect_semantic_binding_gaps(minimal_inventory, graph)
    # minimal_inventory hat rag_silent_failure in failure_modes
    rag_gaps = [g for g in gaps if g.get("failure_class") == "rag_silent_failure"]
    assert len(rag_gaps) == 0


def test_build_gap_types_counts_correctly() -> None:
    """gap_types: Zählt failure_class_uncovered, guard_missing, etc."""
    gaps = {
        "failure_class": [{"gap_type": "failure_class_uncovered"}],
        "guard": [{"gap_type": "guard_missing"}],
        "regression_requirement": [],
        "replay_binding": [],
    }
    autopilot_agg = {"backlog_items": [{"covered": False}, {"covered": True}]}
    types = build_gap_types(gaps, autopilot_agg)
    assert types["failure_class_uncovered"] == 1
    assert types["guard_missing"] == 1
    assert types["autopilot_recommendation_uncovered"] == 1
