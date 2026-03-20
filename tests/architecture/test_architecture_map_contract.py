"""
Architektur-Guard: Architecture Map Contract Validator.

Prüft, dass der Validator existiert, die Architecture Map lesen kann
und zentrale Konsistenzprüfungen durchführt.

Regeln: docs/04_architecture/ARCHITECTURE_MAP_CONTRACT.md
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import PROJECT_ROOT

SCRIPT = PROJECT_ROOT / "scripts" / "dev" / "validate_architecture_map.py"
MAP_JSON = PROJECT_ROOT / "docs" / "04_architecture" / "ARCHITECTURE_MAP.json"

REQUIRED_CATEGORIES = ["layers", "domains", "entrypoints", "registries", "services", "governance"]


@pytest.mark.architecture
@pytest.mark.contract
def test_validate_architecture_map_script_exists():
    """Sentinel: scripts/dev/validate_architecture_map.py existiert."""
    assert SCRIPT.exists(), (
        f"Architecture-Map-Validator fehlt: {SCRIPT}. "
        "Siehe docs/04_architecture/ARCHITECTURE_MAP_CONTRACT.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_validate_architecture_map_json_exists():
    """Sentinel: ARCHITECTURE_MAP.json existiert als Quelle."""
    assert MAP_JSON.exists(), (
        f"ARCHITECTURE_MAP.json fehlt: {MAP_JSON}. "
        "Bitte zuerst: python scripts/dev/architecture_map.py --json"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_can_read_and_validate_map():
    """Sentinel: Validator kann Map lesen und prüfen."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Validator fehlgeschlagen: {result.stderr}"
    assert "OK" in result.stdout or "Bestanden" in result.stdout


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_json_output_contains_categories():
    """Sentinel: JSON-Ausgabe enthält zentrale Prüfkategorien."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Validator --json fehlgeschlagen: {result.stderr}"
    data = json.loads(result.stdout)
    assert "results" in data
    categories = {r["category"] for r in data["results"]}
    for cat in REQUIRED_CATEGORIES:
        assert cat in categories or any(cat in c for c in categories), (
            f"Kategorie {cat} fehlt in Validator-Ausgabe"
        )


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_checks_core_architecture_nodes():
    """Sentinel: Validator prüft zentrale Architekturknoten."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    items = [r["item"] for r in data["results"]]
    assert "GUI" in items or any("GUI" in str(i) for i in items), "GUI-Layer wird nicht geprüft"
    assert "Services" in items or any("service" in str(i).lower() for i in items), (
        "Services werden nicht geprüft"
    )
    assert any("governance" in str(r.get("category", "")).lower() for r in data["results"]), (
        "Governance wird nicht geprüft"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_detects_empty_or_broken_map():
    """Sentinel: Leere oder kaputte Map würde auffallen."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    assert data["total"] >= 20, "Validator prüft zu wenig (Map könnte trivial sein)"
    assert "map_structure" in [r["category"] for r in data["results"]] or data["total"] > 25, (
        "Map-Struktur wird nicht explizit geprüft"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_checks_governance_files():
    """Sentinel: Governance-Policy-Dateien aus der Map werden geprüft."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    gov_results = [r for r in data["results"] if r.get("category") == "governance"]
    assert len(gov_results) >= 5, "Zu wenige Governance-Blöcke werden geprüft"
    all_ok = all(r["ok"] for r in gov_results)
    assert all_ok, f"Governance-Prüfungen fehlgeschlagen: {[r for r in gov_results if not r['ok']]}"


@pytest.mark.architecture
@pytest.mark.contract
def test_validator_fails_on_missing_layer(tmp_path):
    """Sentinel: Manipulierte Map mit fehlendem Layer führt zu Fehler."""
    if not MAP_JSON.exists():
        pytest.skip("ARCHITECTURE_MAP.json fehlt")
    original = json.loads(MAP_JSON.read_text(encoding="utf-8"))
    broken = json.loads(json.dumps(original))
    broken["layers"] = [{"name": "Bogus", "path": "app/nonexistent_layer_xyz_12345/", "role": "x"}]
    broken_json = tmp_path / "broken_map.json"
    broken_json.write_text(json.dumps(broken, indent=2), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--map", str(broken_json)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0, "Validator sollte bei fehlendem Layer fehlschlagen"
    assert "Bogus" in result.stdout or "nonexistent" in result.stdout or "fehlt" in result.stdout
