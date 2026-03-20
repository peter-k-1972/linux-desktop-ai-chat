"""
Pytest Fixtures für QA Coverage Map Tests.

Stellt minimale Inventory-, Strategy-, Graph- und Autopilot-Fixtures bereit.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _minimal_inventory() -> dict:
    """Minimales Inventory mit catalog_bound und inferred Tests."""
    return {
        "schema_version": "1.0",
        "generated_at": "2026-03-15T12:00:00Z",
        "test_count": 4,
        "tests": [
            {
                "test_id": "tests_failure_modes_test_foo.py__test_rag_failure",
                "pytest_nodeid": "tests/failure_modes/test_foo.py::test_rag_failure",
                "file_path": "tests/failure_modes/test_foo.py",
                "test_name": "test_rag_failure",
                "test_domain": "failure_modes",
                "test_type": "failure_mode",
                "subsystem": "RAG",
                "failure_classes": ["rag_silent_failure"],
                "guard_types": ["failure_replay_guard"],
                "inference_sources": {"failure_class": "catalog_bound", "subsystem": "inferred"},
                "manual_review_required": False,
            },
            {
                "test_id": "tests_async_behavior_test_signal.py__test_signal_no_crash",
                "pytest_nodeid": "tests/async_behavior/test_signal.py::test_signal_no_crash",
                "file_path": "tests/async_behavior/test_signal.py",
                "test_name": "test_signal_no_crash",
                "test_domain": "async_behavior",
                "test_type": "async_behavior",
                "subsystem": "Chat",
                "failure_classes": ["late_signal_use_after_destroy"],
                "guard_types": [],
                "inference_sources": {"failure_class": "catalog_bound", "subsystem": "inferred"},
                "manual_review_required": False,
            },
            {
                "test_id": "tests_root_test_bar.py__test_bar",
                "pytest_nodeid": "tests/test_bar.py::test_bar",
                "file_path": "tests/test_bar.py",
                "test_name": "test_bar",
                "test_domain": "root",
                "test_type": "unknown",
                "subsystem": None,
                "failure_classes": [],
                "guard_types": [],
                "inference_sources": {"failure_class": "unknown", "subsystem": "unknown"},
                "manual_review_required": True,
            },
            {
                "test_id": "tests_contracts_test_event.py__test_event_contract",
                "pytest_nodeid": "tests/contracts/test_event.py::test_event_contract",
                "file_path": "tests/contracts/test_event.py",
                "test_name": "test_event_contract",
                "test_domain": "contracts",
                "test_type": "contract",
                "subsystem": "Debug/EventBus",
                "failure_classes": ["debug_false_truth"],
                "guard_types": ["event_contract_guard"],
                "inference_sources": {"failure_class": "catalog_bound", "subsystem": "inferred"},
                "manual_review_required": False,
            },
        ],
    }


def _minimal_test_strategy() -> dict:
    """Minimale Test Strategy mit regression_requirements und guard_requirements."""
    return {
        "schema_version": "1.0",
        "regression_requirements": [
            {"id": "TR-001", "incident_id": "INC-20260315-001", "failure_class": "ui_state_drift", "subsystem": "Chat"},
        ],
        "guard_requirements": [
            {"guard_type": "event_contract_guard", "failure_class": "ui_state_drift", "subsystem": "Chat"},
        ],
    }


def _minimal_knowledge_graph() -> dict:
    """Minimaler Knowledge Graph mit validated_by Edges."""
    return {
        "schema_version": "1.0",
        "nodes": [],
        "edges": [
            {"edge_type": "validated_by", "source_id": "failure_class:ui_state_drift", "target_id": "test_domain:async_behavior"},
            {"edge_type": "validated_by", "source_id": "failure_class:rag_silent_failure", "target_id": "test_domain:failure_modes"},
        ],
    }


def _minimal_autopilot_v3() -> dict:
    """Minimaler Autopilot v3 mit recommended_test_backlog."""
    return {
        "schema_version": "3.0",
        "recommended_test_backlog": [
            {"id": "RTB-001", "subsystem": "RAG", "failure_class": "rag_silent_failure", "guard_type": "failure_replay_guard", "test_domain": "failure_modes"},
        ],
        "translation_gap_findings": [
            {"id": "TR-001", "gap_type": "incident_not_bound_to_regression", "incident_id": "INC-20260315-001"},
        ],
    }


def _minimal_bindings() -> dict:
    """Minimales bindings.json mit regression_test."""
    return {
        "schema_version": "1.0",
        "identity": {"incident_id": "INC-20260315-001", "replay_id": "REPLAY-INC-20260315-001"},
        "regression_catalog": {"failure_class": "ui_state_drift", "regression_test": "tests/failure_modes/test_foo.py::test_rag_failure"},
        "status": {"binding_status": "validated"},
    }


@pytest.fixture
def minimal_inventory() -> dict:
    """Minimales QA_TEST_INVENTORY für isolierte Tests."""
    return _minimal_inventory()


@pytest.fixture
def minimal_test_strategy() -> dict:
    """Minimale QA_TEST_STRATEGY."""
    return _minimal_test_strategy()


@pytest.fixture
def minimal_knowledge_graph() -> dict:
    """Minimaler QA_KNOWLEDGE_GRAPH."""
    return _minimal_knowledge_graph()


@pytest.fixture
def minimal_autopilot_v3() -> dict:
    """Minimaler QA_AUTOPILOT_V3."""
    return _minimal_autopilot_v3()


@pytest.fixture
def minimal_bindings() -> dict:
    """Minimales bindings.json."""
    return _minimal_bindings()


@pytest.fixture
def inventory_with_gap() -> dict:
    """Inventory ohne Tests für ui_state_drift (für semantic_binding_gap)."""
    inv = _minimal_inventory()
    # Kein Test für ui_state_drift in async_behavior
    return inv


@pytest.fixture
def empty_inventory() -> dict:
    """Leeres Inventory."""
    return {"schema_version": "1.0", "test_count": 0, "tests": []}
