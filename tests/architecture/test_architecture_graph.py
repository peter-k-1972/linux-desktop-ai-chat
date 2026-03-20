"""
Architektur-Guard: Architecture Graph Generator.

Prüft, dass das Architecture-Graph-Skript existiert, die JSON-Map nutzt
und eine gültige DOT-Ausgabe mit zentralen Knoten erzeugt.

Regeln: docs/04_architecture/ARCHITECTURE_GRAPH_REPORT.md
"""

import subprocess
import sys
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import PROJECT_ROOT

SCRIPT = PROJECT_ROOT / "scripts" / "dev" / "render_architecture_graph.py"
MAP_JSON = PROJECT_ROOT / "docs" / "04_architecture" / "ARCHITECTURE_MAP.json"
OUTPUT_DOT = PROJECT_ROOT / "docs" / "04_architecture" / "ARCHITECTURE_GRAPH.dot"

REQUIRED_NODES = [
    "layer_GUI",
    "layer_Services",
    "layer_Providers",
    "layer_Core",
    "domain_agents",
    "domain_rag",
    "reg_Model_Registry",
    "governance_block",
    "legacy_block",
]
REQUIRED_EDGES = [
    "layer_GUI -> layer_Services",
    "layer_Services -> layer_Providers",
    "layer_Providers -> layer_Core",
]


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_script_exists():
    """Sentinel: scripts/dev/render_architecture_graph.py existiert."""
    assert SCRIPT.exists(), (
        f"Architecture-Graph-Skript fehlt: {SCRIPT}. "
        "Siehe docs/04_architecture/ARCHITECTURE_GRAPH_REPORT.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_json_exists():
    """Sentinel: ARCHITECTURE_MAP.json existiert als Quelle."""
    assert MAP_JSON.exists(), (
        f"ARCHITECTURE_MAP.json fehlt: {MAP_JSON}. "
        "Bitte zuerst: python scripts/dev/architecture_map.py --json"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_generates_dot():
    """Sentinel: Skript erzeugt ARCHITECTURE_GRAPH.dot."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--no-svg"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Skript fehlgeschlagen: {result.stderr}"
    assert OUTPUT_DOT.exists(), "ARCHITECTURE_GRAPH.dot wurde nicht erzeugt"


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_dot_contains_required_nodes():
    """Sentinel: DOT enthält zentrale Knoten."""
    if not OUTPUT_DOT.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT), "--no-svg"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_DOT.read_text(encoding="utf-8")
    missing = [n for n in REQUIRED_NODES if n not in content]
    assert not missing, (
        f"ARCHITECTURE_GRAPH.dot fehlen Knoten: {missing}. "
        "Erwartet: Hauptlayer, Domänen, Registries, Governance, Legacy."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_dot_contains_required_edges():
    """Sentinel: DOT enthält zentrale Beziehungen."""
    if not OUTPUT_DOT.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT), "--no-svg"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_DOT.read_text(encoding="utf-8")
    missing = [e for e in REQUIRED_EDGES if e not in content]
    assert not missing, (
        f"ARCHITECTURE_GRAPH.dot fehlen Kanten: {missing}. "
        "Erwartet: GUI->Services, Services->Providers, Providers->Core."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_uses_json_source():
    """Sentinel: Skript nutzt ARCHITECTURE_MAP.json als Quelle."""
    if not OUTPUT_DOT.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT), "--no-svg"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_DOT.read_text(encoding="utf-8")
    assert "digraph Architecture" in content, "DOT ist kein gültiger digraph"
    assert "cluster_layers" in content or "layer_GUI" in content, (
        "DOT scheint nicht aus JSON-Map generiert"
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_graph_not_trivial():
    """Sentinel: DOT-Ausgabe ist nicht leer / nicht trivial."""
    if not OUTPUT_DOT.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT), "--no-svg"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_DOT.read_text(encoding="utf-8")
    assert len(content) > 500, "ARCHITECTURE_GRAPH.dot ist zu kurz (trivial)"
    assert "Hauptlayer" in content or "cluster_layers" in content, "Kern-Cluster fehlen"
