"""
QA Test Inventory – Datenmodelle.

Definiert Test-Eintrag und Top-Level-Struktur für QA_TEST_INVENTORY.json.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=False)
class TestEntry:
    """Einzelner Test-Eintrag im Inventar."""

    test_id: str
    test_name: str
    pytest_nodeid: str
    file_path: str
    test_type: str
    execution_mode: str
    test_domain: str
    markers: list[str]
    subsystem: str | None
    component: str | None
    failure_classes: list[str]
    guard_types: list[str]
    covers_regression: bool
    covers_replay: str
    regression_ids: list[str]
    replay_ids: list[str]
    inference_confidence: dict[str, str]
    inference_sources: dict[str, str]
    manual_review_required: bool
    notes: str | None

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu JSON-serialisierbarem Dict."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "pytest_nodeid": self.pytest_nodeid,
            "file_path": self.file_path,
            "test_type": self.test_type,
            "execution_mode": self.execution_mode,
            "test_domain": self.test_domain,
            "markers": self.markers,
            "subsystem": self.subsystem,
            "component": self.component,
            "failure_classes": self.failure_classes,
            "guard_types": self.guard_types,
            "covers_regression": self.covers_regression,
            "covers_replay": self.covers_replay,
            "regression_ids": self.regression_ids,
            "replay_ids": self.replay_ids,
            "inference_confidence": self.inference_confidence,
            "inference_sources": self.inference_sources,
            "manual_review_required": self.manual_review_required,
            "notes": self.notes,
        }


@dataclass(frozen=False)
class InventoryOutput:
    """Vollständige Inventar-Ausgabe."""

    schema_version: str
    generated_at: str
    input_sources: list[str]
    summary: dict[str, Any]
    tests: list[TestEntry]

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu JSON-serialisierbarem Dict."""
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "generator": "test_inventory",
            "input_sources": self.input_sources,
            "summary": self.summary,
            "test_count": len(self.tests),
            "tests": [t.to_dict() for t in self.tests],
        }
