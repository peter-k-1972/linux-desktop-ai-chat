"""
Architektur-Guard: Architecture Health Check.

Prüft Existenz, Ausführung und Signale des Health-Check-Skripts.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import PROJECT_ROOT

HEALTH_CHECK_SCRIPT = PROJECT_ROOT / "scripts" / "architecture" / "architecture_health_check.py"

# Erwartete Statuswerte
VALID_STATUSES = frozenset({"OK", "WARNING", "FAIL"})

# Erwartete Check-Kategorien (muss Health-Check liefern)
EXPECTED_CHECK_KEYS = frozenset({
    "baseline",
    "governance_policies",
    "arch_guard_config",
    "entrypoints",
    "architecture_tests",
    "docs_path",
    "drift_radar",
})


@pytest.mark.architecture
@pytest.mark.contract
def test_health_check_script_exists():
    """Sentinel: Health-Check-Skript existiert."""
    assert HEALTH_CHECK_SCRIPT.exists(), (
        f"Architecture Health Check: Skript fehlt: {HEALTH_CHECK_SCRIPT}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_health_check_produces_structured_output():
    """Sentinel: Health-Check liefert strukturierte JSON-Ausgabe."""
    result = subprocess.run(
        [sys.executable, str(HEALTH_CHECK_SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode in (0, 1, 2), (
        f"Health-Check: unerwarteter Exit-Code {result.returncode}"
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Health-Check JSON ungültig: {e}")

    assert "overall" in data, "JSON fehlt: overall"
    assert data["overall"] in VALID_STATUSES, (
        f"overall muss in {VALID_STATUSES} sein, got {data['overall']}"
    )
    assert "results" in data, "JSON fehlt: results"
    assert "failures" in data, "JSON fehlt: failures"
    assert "warnings" in data, "JSON fehlt: warnings"


@pytest.mark.architecture
@pytest.mark.contract
def test_health_check_references_governance_domains():
    """Sentinel: Health-Check prüft zentrale Governance-Bereiche."""
    result = subprocess.run(
        [sys.executable, str(HEALTH_CHECK_SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    results = data.get("results", {})
    actual_keys = set(results.keys())
    missing = EXPECTED_CHECK_KEYS - actual_keys
    assert not missing, (
        f"Health-Check fehlt Checks: {missing}. Erwartet: {EXPECTED_CHECK_KEYS}"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_health_check_status_model_stable():
    """Sentinel: Statusmodell ist stabil (OK, WARNING, FAIL)."""
    # Prüfe dass das Skript genau diese drei Status liefern kann
    result = subprocess.run(
        [sys.executable, str(HEALTH_CHECK_SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    overall = data.get("overall")
    assert overall in VALID_STATUSES, f"overall={overall} nicht in {VALID_STATUSES}"


@pytest.mark.architecture
@pytest.mark.contract
def test_health_check_not_silently_empty():
    """Sentinel: Health-Check liefert keine stillschweigend leere Ausgabe."""
    result = subprocess.run(
        [sys.executable, str(HEALTH_CHECK_SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    results = data.get("results", {})
    assert len(results) >= 5, (
        "Health-Check muss mindestens 5 Check-Ergebnisse liefern"
    )
    # Mindestens ein Check muss eine aussagekräftige Message haben
    messages = [r.get("message", "") for r in results.values() if isinstance(r, dict)]
    assert any(m for m in messages if m), (
        "Health-Check-Ergebnisse müssen Messages enthalten"
    )
