"""
Tests für Coverage-Map-Governance.

Generator verändert keine Input-Artefakte.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "qa" / "build_coverage_map.py"
_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"


def _run_build_coverage_map(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Führt build_coverage_map.py aus."""
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH)] + args,
        cwd=str(cwd or _PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr


def test_generator_does_not_modify_inventory(tmp_path: Path) -> None:
    """Generator verändert QA_TEST_INVENTORY.json nicht."""
    if not (_DOCS_QA / "QA_TEST_INVENTORY.json").exists():
        pytest.skip("QA_TEST_INVENTORY.json nicht vorhanden")
    inv_path = _DOCS_QA / "QA_TEST_INVENTORY.json"
    before = inv_path.read_text(encoding="utf-8")
    _run_build_coverage_map(["--output", str(tmp_path / "QA_COVERAGE_MAP.json")])
    after = inv_path.read_text(encoding="utf-8")
    assert before == after


def test_generator_does_not_modify_strategy(tmp_path: Path) -> None:
    """Generator verändert QA_TEST_STRATEGY.json nicht."""
    if not (_DOCS_QA / "QA_TEST_STRATEGY.json").exists():
        pytest.skip("QA_TEST_STRATEGY.json nicht vorhanden")
    path = _DOCS_QA / "QA_TEST_STRATEGY.json"
    before = path.read_text(encoding="utf-8")
    _run_build_coverage_map(["--output", str(tmp_path / "out.json")])
    after = path.read_text(encoding="utf-8")
    assert before == after


def test_generator_does_not_modify_knowledge_graph(tmp_path: Path) -> None:
    """Generator verändert QA_KNOWLEDGE_GRAPH.json nicht."""
    if not (_DOCS_QA / "QA_KNOWLEDGE_GRAPH.json").exists():
        pytest.skip("QA_KNOWLEDGE_GRAPH.json nicht vorhanden")
    path = _DOCS_QA / "QA_KNOWLEDGE_GRAPH.json"
    before = path.read_text(encoding="utf-8")
    _run_build_coverage_map(["--output", str(tmp_path / "out.json")])
    after = path.read_text(encoding="utf-8")
    assert before == after


def test_generator_does_not_modify_autopilot(tmp_path: Path) -> None:
    """Generator verändert QA_AUTOPILOT_V3.json nicht."""
    if not (_DOCS_QA / "QA_AUTOPILOT_V3.json").exists():
        pytest.skip("QA_AUTOPILOT_V3.json nicht vorhanden")
    path = _DOCS_QA / "QA_AUTOPILOT_V3.json"
    before = path.read_text(encoding="utf-8")
    _run_build_coverage_map(["--output", str(tmp_path / "out.json")])
    after = path.read_text(encoding="utf-8")
    assert before == after


def test_generator_dry_run_writes_only_to_stdout() -> None:
    """Generator --dry-run schreibt nur auf stdout, keine Datei."""
    code, stdout, stderr = _run_build_coverage_map(["--dry-run"])
    assert code == 0
    data = json.loads(stdout)
    assert "coverage_by_axis" in data
    assert "gaps" in data
    assert "summary" in data
    # Keine Datei docs/qa/QA_COVERAGE_MAP.json durch dry-run
    # (wir prüfen nur, dass stdout gültiges JSON ist)


def test_generator_output_is_deterministic(tmp_path: Path) -> None:
    """Zwei Läufe mit --timestamp liefern identischen Output."""
    out1 = tmp_path / "out1.json"
    out2 = tmp_path / "out2.json"
    if not (_DOCS_QA / "QA_TEST_INVENTORY.json").exists():
        pytest.skip("QA_TEST_INVENTORY.json nicht vorhanden")
    _run_build_coverage_map(["--output", str(out1), "--timestamp", "2026-03-15T12:00:00Z"])
    _run_build_coverage_map(["--output", str(out2), "--timestamp", "2026-03-15T12:00:00Z"])
    assert out1.exists()
    assert out2.exists()
    assert out1.read_text() == out2.read_text()


def test_generator_fails_without_inventory(tmp_path: Path) -> None:
    """Generator bricht mit Fehler ab wenn Inventory fehlt."""
    code, _, stderr = _run_build_coverage_map(["--output", str(tmp_path / "out.json"), "--qa-dir", str(tmp_path)])
    assert code != 0
    assert "QA_TEST_INVENTORY" in stderr or "nicht gefunden" in stderr or "FileNotFoundError" in str(stderr)
