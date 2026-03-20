"""
Unit Tests: QA Feedback Loop – Loader.

Testet load_feedback_inputs_from_paths, Pfad-Handling, fehlende Dateien,
leere Datei, ungültiges JSON, unvollständige JSON-Struktur.
"""

from pathlib import Path

import pytest

from scripts.qa.feedback_loop import load_feedback_inputs_from_paths


def test_load_from_paths_empty_file_returns_none(tmp_path: Path) -> None:
    """Leere Datei führt zu None (load_json liefert None bei JSONDecodeError)."""
    p = tmp_path / "empty.json"
    p.write_text("", encoding="utf-8")
    inputs = load_feedback_inputs_from_paths(incident_index_path=p)
    assert inputs.incident_index is None
    assert "incidents/index.json" in inputs.missing_sources


def test_load_from_paths_invalid_json_returns_none(tmp_path: Path) -> None:
    """Ungültige JSON-Datei führt zu None."""
    p = tmp_path / "bad.json"
    p.write_text("{invalid json}", encoding="utf-8")
    inputs = load_feedback_inputs_from_paths(incident_index_path=p)
    assert inputs.incident_index is None


def test_load_from_paths_empty_dict_treated_as_missing(tmp_path: Path) -> None:
    """Leeres JSON-Dict ({}) wird als nicht geladen gewertet (Loader prüft truthiness)."""
    p = tmp_path / "empty_dict.json"
    p.write_text("{}", encoding="utf-8")
    inputs = load_feedback_inputs_from_paths(incident_index_path=p)
    assert inputs.incident_index is None
    assert "incidents/index.json" in inputs.missing_sources


def test_load_from_paths_incomplete_structure_loads_as_dict(tmp_path: Path) -> None:
    """Unvollständige JSON-Struktur (minimales Dict ohne incidents) wird geladen – Normalizer behandelt fehlende Keys."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)
    # Minimales Dict mit schema_version, aber ohne incidents – Loader akzeptiert es (truthy)
    (inc_dir / "index.json").write_text('{"schema_version": "1.0"}', encoding="utf-8")
    (inc_dir / "analytics.json").write_text('{"qa_coverage": {}}', encoding="utf-8")
    (tmp_path / "QA_AUTOPILOT_V2.json").write_text('{"recommended_focus_subsystem": ""}', encoding="utf-8")

    inputs = load_feedback_inputs_from_paths(
        incident_index_path=inc_dir / "index.json",
        analytics_path=inc_dir / "analytics.json",
        autopilot_path=tmp_path / "QA_AUTOPILOT_V2.json",
    )
    assert inputs.incident_index is not None
    assert "schema_version" in inputs.incident_index
    assert "incidents" not in inputs.incident_index  # unvollständig
    assert inputs.analytics is not None
    assert "incidents/index.json" in inputs.loaded_sources


def test_load_from_paths_success(feedback_loop_fixtures_dir: Path) -> None:
    """Loader lädt alle vorhandenen Dateien."""
    inc_dir = feedback_loop_fixtures_dir / "incidents"
    inputs = load_feedback_inputs_from_paths(
        incident_index_path=inc_dir / "index.json",
        analytics_path=inc_dir / "analytics.json",
        autopilot_path=feedback_loop_fixtures_dir / "QA_AUTOPILOT_V2.json",
        control_center_path=feedback_loop_fixtures_dir / "QA_CONTROL_CENTER.json",
        priority_score_path=feedback_loop_fixtures_dir / "QA_PRIORITY_SCORE.json",
    )
    assert inputs.incident_index is not None
    assert inputs.analytics is not None
    assert inputs.autopilot_v2 is not None
    assert inputs.control_center is not None
    assert inputs.priority_score is not None
    assert "incidents/index.json" in inputs.loaded_sources


def test_load_from_paths_missing_returns_none(tmp_path: Path) -> None:
    """Fehlende Dateien führen zu None in den entsprechenden Feldern."""
    inputs = load_feedback_inputs_from_paths(
        incident_index_path=tmp_path / "nonexistent_index.json",
        analytics_path=tmp_path / "nonexistent_analytics.json",
        autopilot_path=tmp_path / "nonexistent_autopilot.json",
        control_center_path=None,
        priority_score_path=None,
    )
    assert inputs.incident_index is None
    assert inputs.analytics is None
    assert inputs.autopilot_v2 is None
    assert inputs.control_center is None
    assert inputs.priority_score is None
    assert "incidents/index.json" in inputs.missing_sources
