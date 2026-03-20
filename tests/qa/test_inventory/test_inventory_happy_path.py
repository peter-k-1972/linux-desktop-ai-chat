"""
QA Test Inventory – Happy Path.

- Discovery-Stabilität: Tests werden gesammelt, nodeids/file_paths erhalten
- Feldvollständigkeit: Pflichtfelder vorhanden, Struktur konsistent
- Summary-Korrektheit: Counts stimmen zur Testmenge
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_build_test_inventory

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "generated_at",
    "generator",
    "input_sources",
    "summary",
    "test_count",
    "tests",
}

REQUIRED_TEST_ENTRY = {
    "test_id",
    "test_name",
    "pytest_nodeid",
    "file_path",
    "test_type",
    "execution_mode",
    "test_domain",
    "markers",
    "subsystem",
    "component",
    "failure_classes",
    "guard_types",
    "covers_regression",
    "covers_replay",
    "regression_ids",
    "replay_ids",
    "inference_confidence",
    "inference_sources",
    "manual_review_required",
    "notes",
}


def _parse_stdout_json(stdout: str) -> dict:
    """Parst JSON aus stdout."""
    return json.loads(stdout)


@pytest.mark.unit
def test_build_inventory_produces_valid_json(minimal_catalog_path: Path) -> None:
    """Generator liefert gültiges JSON."""
    exit_code, stdout, stderr = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0, stderr
    data = _parse_stdout_json(stdout)
    assert isinstance(data, dict)


@pytest.mark.unit
def test_top_level_structure_complete(minimal_catalog_path: Path) -> None:
    """Top-Level enthält alle Pflichtfelder."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    missing = REQUIRED_TOP_LEVEL - set(data.keys())
    assert not missing, f"Fehlende Top-Level-Felder: {missing}"


@pytest.mark.unit
def test_test_entry_structure_complete(minimal_catalog_path: Path) -> None:
    """Jeder Test-Eintrag enthält alle Pflichtfelder."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    tests = data.get("tests", [])
    assert len(tests) > 0
    for i, t in enumerate(tests[:5]):
        missing = REQUIRED_TEST_ENTRY - set(t.keys())
        assert not missing, f"Test {i} fehlt: {missing}"


@pytest.mark.unit
def test_nodeid_and_file_path_preserved(minimal_catalog_path: Path) -> None:
    """pytest_nodeid und file_path gehen nicht verloren."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    tests = data.get("tests", [])
    for t in tests:
        assert "pytest_nodeid" in t
        assert "file_path" in t
        assert "::" in t["pytest_nodeid"] or t["file_path"].endswith(".py")
        assert t["file_path"].startswith("tests/") or t["file_path"] == "tests"


@pytest.mark.unit
def test_test_id_stable_and_traceable(minimal_catalog_path: Path) -> None:
    """test_id ist stabil und aus nodeid ableitbar."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    for t in data.get("tests", []):
        tid = t["test_id"]
        nodeid = t["pytest_nodeid"]
        assert tid.startswith("tests_")
        assert "__" in tid
        assert "::" not in tid
        assert "/" not in tid or "_" in tid


@pytest.mark.unit
def test_summary_counts_match_test_list(minimal_catalog_path: Path) -> None:
    """Summary test_count = len(tests)."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    tests = data.get("tests", [])
    summary = data.get("summary", {})
    assert summary.get("test_count") == len(tests)
    assert data.get("test_count") == len(tests)


@pytest.mark.unit
def test_by_test_type_sum_equals_total(minimal_catalog_path: Path) -> None:
    """Summe by_test_type = test_count."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    summary = data.get("summary", {})
    by_type = summary.get("by_test_type", {})
    total = summary.get("test_count", 0)
    assert sum(by_type.values()) == total


@pytest.mark.unit
def test_by_test_domain_sum_equals_total(minimal_catalog_path: Path) -> None:
    """Summe by_test_domain = test_count."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    summary = data.get("summary", {})
    by_domain = summary.get("by_test_domain", {})
    total = summary.get("test_count", 0)
    assert sum(by_domain.values()) == total


@pytest.mark.unit
def test_by_subsystem_sum_equals_total(minimal_catalog_path: Path) -> None:
    """Summe by_subsystem = test_count."""
    exit_code, stdout, _ = run_build_test_inventory(
        ["--dry-run", "--output", "-", "--catalog", str(minimal_catalog_path)],
    )
    assert exit_code == 0
    data = _parse_stdout_json(stdout)
    summary = data.get("summary", {})
    by_subsystem = summary.get("by_subsystem", {})
    total = summary.get("test_count", 0)
    assert sum(by_subsystem.values()) == total
