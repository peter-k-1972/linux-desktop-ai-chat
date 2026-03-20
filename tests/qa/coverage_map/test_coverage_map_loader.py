"""
Tests für coverage_map_loader.

Input-Verarbeitung: Inventory, Strategy, Graph, Autopilot werden korrekt geladen.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.qa.coverage_map_loader import (
    load_all_inputs,
    load_autopilot_v3,
    load_inventory,
    load_json,
    load_knowledge_graph,
    load_test_strategy,
)


def test_load_json_existing_file(tmp_path: Path) -> None:
    """load_json lädt gültige JSON-Datei."""
    f = tmp_path / "test.json"
    f.write_text('{"a": 1}', encoding="utf-8")
    data = load_json(f)
    assert data == {"a": 1}


def test_load_json_missing_file(tmp_path: Path) -> None:
    """load_json gibt None bei fehlender Datei."""
    data = load_json(tmp_path / "nonexistent.json")
    assert data is None


def test_load_json_invalid_file(tmp_path: Path) -> None:
    """load_json gibt None bei ungültigem JSON."""
    f = tmp_path / "bad.json"
    f.write_text("not json", encoding="utf-8")
    data = load_json(f)
    assert data is None


def test_load_inventory_requires_file(tmp_path: Path) -> None:
    """load_inventory wirft bei fehlender Datei."""
    with pytest.raises(FileNotFoundError, match="QA_TEST_INVENTORY"):
        load_inventory(tmp_path)


def test_load_inventory_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """load_inventory lädt gültiges Inventory."""
    qa_dir = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "qa"
    if not (qa_dir / "QA_TEST_INVENTORY.json").exists():
        pytest.skip("QA_TEST_INVENTORY.json nicht vorhanden")
    data = load_inventory(qa_dir)
    assert "tests" in data
    assert "test_count" in data or "tests" in data
    assert isinstance(data["tests"], list)


def test_load_test_strategy_optional(tmp_path: Path) -> None:
    """load_test_strategy gibt None bei fehlender Datei."""
    data = load_test_strategy(tmp_path)
    assert data is None


def test_load_knowledge_graph_optional(tmp_path: Path) -> None:
    """load_knowledge_graph gibt None bei fehlender Datei."""
    data = load_knowledge_graph(tmp_path)
    assert data is None


def test_load_autopilot_v3_optional(tmp_path: Path) -> None:
    """load_autopilot_v3 gibt None bei fehlender Datei."""
    data = load_autopilot_v3(tmp_path)
    assert data is None


def test_load_all_inputs_requires_inventory(tmp_path: Path) -> None:
    """load_all_inputs wirft bei fehlendem Inventory."""
    with pytest.raises(FileNotFoundError):
        load_all_inputs(tmp_path)


def test_load_all_inputs_with_minimal_qa_dir(tmp_path: Path) -> None:
    """load_all_inputs lädt bei vorhandenem Inventory."""
    inv_path = tmp_path / "QA_TEST_INVENTORY.json"
    inv_path.write_text(json.dumps({"schema_version": "1.0", "test_count": 0, "tests": []}), encoding="utf-8")
    inputs = load_all_inputs(tmp_path)
    assert "inventory" in inputs
    assert inputs["inventory"]["test_count"] == 0
    assert "input_sources" in inputs
    assert "docs/qa/QA_TEST_INVENTORY.json" in inputs["input_sources"]
