"""
Tests für Phase 3 Replay-Binding-Enrichment.
"""

from __future__ import annotations

import pytest

from scripts.qa.enrich_replay_binding import _build_binding_map, enrich_inventory


def test_enrich_inventory_with_binding() -> None:
    """Test mit Binding: covers_replay=yes, replay_ids gesetzt."""
    inventory = {
        "tests": [
            {
                "test_id": "tests_failure_modes_test_foo__test_rag",
                "pytest_nodeid": "tests/failure_modes/test_foo.py::test_rag",
                "covers_replay": "unknown",
                "replay_ids": [],
            },
        ],
    }
    bindings = {
        "INC-001": {
            "identity": {"incident_id": "INC-001", "replay_id": "REPLAY-INC-001"},
            "regression_catalog": {"regression_test": "tests/failure_modes/test_foo.py::test_rag"},
        },
    }
    enriched, trace = enrich_inventory(inventory, bindings)
    assert len(trace) == 1
    assert trace[0]["replay_id"] == "REPLAY-INC-001"
    t = enriched["tests"][0]
    assert t["covers_replay"] == "yes"
    assert t["replay_ids"] == ["REPLAY-INC-001"]


def test_enrich_inventory_no_binding() -> None:
    """Ohne Bindings: Inventory unverändert (covers_replay bleibt)."""
    inventory = {
        "tests": [
            {"test_id": "t1", "pytest_nodeid": "tests/x.py::t1", "covers_replay": "unknown"},
        ],
    }
    enriched, trace = enrich_inventory(inventory, {})
    assert len(trace) == 0
    assert enriched["tests"][0]["covers_replay"] == "unknown"


def test_build_binding_map_skips_empty_regression_test() -> None:
    """Bindings ohne regression_test oder replay_id werden ignoriert."""
    bindings = {
        "INC-001": {
            "identity": {"incident_id": "INC-001"},  # kein replay_id
            "regression_catalog": {"regression_test": "tests/x.py::t1"},
        },
        "INC-002": {
            "identity": {"incident_id": "INC-002", "replay_id": "REPLAY-INC-002"},
            "regression_catalog": {"regression_test": None},
        },
    }
    m = _build_binding_map(bindings)
    assert len(m) == 0
