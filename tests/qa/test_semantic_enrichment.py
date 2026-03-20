"""
Tests für Phase 3 Semantische Anreicherung.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from scripts.qa.semantic_enrichment import (
    _apply_failure_class_hints,
    _apply_guard_type_overrides,
    apply_semantic_enrichment,
)


def test_apply_failure_class_hints_adds_inferred() -> None:
    """Hints mit confidence=medium setzen inferred."""
    tests = [
        {
            "test_id": "t1",
            "file_path": "tests/failure_modes/test_chroma_unreachable.py",
            "test_name": "test_rag_fails",
            "failure_classes": [],
            "inference_sources": {"failure_class": "unknown"},
        },
    ]
    hints = {
        "file_patterns": [
            {"pattern": "test_chroma_unreachable", "failure_class": "rag_silent_failure", "confidence": "high"},
        ],
    }
    n = _apply_failure_class_hints(tests, hints)
    assert n == 1
    assert tests[0]["failure_classes"] == ["rag_silent_failure"]
    assert tests[0]["inference_sources"]["failure_class"] == "catalog_bound"


def test_apply_failure_class_hints_skips_catalog_bound() -> None:
    """Tests mit catalog_bound werden nicht überschrieben."""
    tests = [
        {
            "file_path": "tests/x/test_chroma_unreachable.py",
            "failure_classes": ["other"],
            "inference_sources": {"failure_class": "catalog_bound"},
        },
    ]
    hints = {"file_patterns": [{"pattern": "test_chroma_unreachable", "failure_class": "rag_silent_failure"}]}
    n = _apply_failure_class_hints(tests, hints)
    assert n == 0
    assert tests[0]["failure_classes"] == ["other"]


def test_apply_guard_type_overrides() -> None:
    """Overrides setzen guard_types."""
    tests = [
        {"test_id": "tests_contracts_test_debug_event_contract__test_x", "guard_types": []},
    ]
    overrides = {
        "overrides": [
            {"test_id_pattern": "tests_contracts_test_debug_event_contract*", "guard_types": ["event_contract_guard"]},
        ],
    }
    n = _apply_guard_type_overrides(tests, overrides)
    assert n == 1
    assert tests[0]["guard_types"] == ["event_contract_guard"]


def test_apply_semantic_enrichment_integration() -> None:
    """Vollständige Anreicherung mit Config-Dateien."""
    with tempfile.TemporaryDirectory() as tmp:
        qa_dir = Path(tmp)
        (qa_dir / "phase3_failure_class_hints.json").write_text(
            '{"file_patterns":[{"pattern":"test_foo","failure_class":"rag_silent_failure","confidence":"high"}]}'
        )
        (qa_dir / "phase3_guard_type_overrides.json").write_text(
            '{"overrides":[{"test_id_pattern":"*test_foo*","guard_types":["event_contract_guard"]}]}'
        )
        inventory = {
            "tests": [
                {
                    "test_id": "tests_x_test_foo__test_bar",
                    "file_path": "tests/x/test_foo.py",
                    "test_name": "test_bar",
                    "failure_classes": [],
                    "inference_sources": {"failure_class": "unknown", "subsystem": "inferred"},
                    "guard_types": [],
                    "manual_review_required": True,
                },
            ],
            "summary": {},
        }
        stats = apply_semantic_enrichment(inventory, qa_dir)
        assert stats["failure_class_hints"] >= 1 or stats["guard_type_overrides"] >= 1
