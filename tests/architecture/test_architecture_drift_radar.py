"""
Architektur-Guard: Architecture Drift Radar.

Prüft Existenz, Konsistenz und Ausgabe des Drift-Radar-Skripts.
Regeln: docs/architecture/ARCHITECTURE_DRIFT_RADAR_POLICY.md
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import (
    DOCS_ARCH,
    DRIFT_RADAR_JSON,
    DRIFT_RADAR_SCRIPT,
    DRIFT_RADAR_STATUS,
    EXPECTED_DRIFT_CATEGORIES,
    EXPECTED_GOVERNANCE_DOMAINS,
    PROJECT_ROOT,
)


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_radar_script_exists():
    """
    Sentinel: Radar-Skript existiert unter scripts/architecture/.
    """
    assert DRIFT_RADAR_SCRIPT.exists(), (
        f"Architecture Drift Radar: Skript fehlt: {DRIFT_RADAR_SCRIPT}. "
        "Siehe docs/architecture/ARCHITECTURE_DRIFT_RADAR_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_radar_produces_structured_output():
    """
    Sentinel: Radar erzeugt strukturierte JSON- und Markdown-Ausgabe.
    """
    result = subprocess.run(
        [sys.executable, str(DRIFT_RADAR_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, (
        f"Architecture Drift Radar: Skript schlug fehl. stderr: {result.stderr}"
    )
    assert DRIFT_RADAR_JSON.exists(), (
        "Architecture Drift Radar: JSON-Datei wurde nicht erzeugt."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_radar_json_structure():
    """
    Sentinel: JSON-Ausgabe hat erwartete Struktur (version, summary, drift_categories).
    """
    if not DRIFT_RADAR_JSON.exists():
        pytest.skip("JSON nicht vorhanden – führe Radar zuerst aus")
    data = json.loads(DRIFT_RADAR_JSON.read_text(encoding="utf-8"))
    assert "version" in data, "JSON fehlt: version"
    assert "summary" in data, "JSON fehlt: summary"
    assert "drift_categories" in data, "JSON fehlt: drift_categories"
    assert "status" in data["summary"], "summary fehlt: status"
    assert data["summary"]["status"] in ("ok", "drift"), "summary.status ungültig"


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_categories_complete():
    """
    Sentinel: Definierte Drift-Kategorien sind vollständig und stabil.
    """
    if not DRIFT_RADAR_JSON.exists():
        pytest.skip("JSON nicht vorhanden")
    data = json.loads(DRIFT_RADAR_JSON.read_text(encoding="utf-8"))
    actual = set(data.get("drift_categories", {}).keys())
    missing = EXPECTED_DRIFT_CATEGORIES - actual
    assert not missing, (
        f"Architecture Drift Radar: Fehlende Drift-Kategorien: {missing}. "
        f"Erwartet: {EXPECTED_DRIFT_CATEGORIES}."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_radar_references_governance_domains():
    """
    Sentinel: Radar referenziert vorhandene Governance-Domänen.
    """
    if not DRIFT_RADAR_JSON.exists():
        pytest.skip("JSON nicht vorhanden")
    data = json.loads(DRIFT_RADAR_JSON.read_text(encoding="utf-8"))
    # governance_files prüft Policy-Dateien
    gov = data.get("governance_files", {})
    assert len(gov) >= 5, (
        "Architecture Drift Radar: governance_files sollte mindestens 5 Einträge haben."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_drift_radar_status_structure_when_exists():
    """
    Sentinel: Markdown-Status hat erwartete Struktur (wenn vorhanden).
    """
    if not DRIFT_RADAR_STATUS.exists():
        pytest.skip(
            "Status nicht vorhanden – führe 'python scripts/architecture/architecture_drift_radar.py' aus"
        )
    content = DRIFT_RADAR_STATUS.read_text(encoding="utf-8")
    assert "Zusammenfassung" in content or "Summary" in content, (
        "Status sollte Zusammenfassung enthalten."
    )
    assert "Drift-Kategorien" in content or "drift" in content.lower(), (
        "Status sollte Drift-Kategorien enthalten."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_expected_governance_domains_defined():
    """
    Sentinel: EXPECTED_GOVERNANCE_DOMAINS ist definiert und nicht leer.
    """
    assert len(EXPECTED_GOVERNANCE_DOMAINS) >= 5, (
        "Architecture Drift Radar: EXPECTED_GOVERNANCE_DOMAINS sollte mindestens 5 Domänen haben."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_expected_drift_categories_defined():
    """
    Sentinel: EXPECTED_DRIFT_CATEGORIES ist definiert und enthält Kern-Kategorien.
    """
    core = {"layer_drift", "registry_drift", "startup_drift"}
    assert core.issubset(EXPECTED_DRIFT_CATEGORIES), (
        f"Architecture Drift Radar: EXPECTED_DRIFT_CATEGORIES fehlt: {core - EXPECTED_DRIFT_CATEGORIES}."
    )
