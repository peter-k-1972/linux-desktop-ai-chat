"""
Architektur-Guard: Architecture Map Generator.

Prüft, dass das Architecture-Map-Skript existiert, ausführbar ist
und eine gültige Markdown-Ausgabe mit Kernsektionen erzeugt.

Regeln: docs/04_architecture/ARCHITECTURE_MAP_REPORT.md
"""

import subprocess
import sys
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import PROJECT_ROOT

SCRIPT = PROJECT_ROOT / "scripts" / "dev" / "architecture_map.py"
OUTPUT_MD = PROJECT_ROOT / "docs" / "04_architecture" / "ARCHITECTURE_MAP.md"
REQUIRED_SECTIONS = [
    "## 1. Executive Summary",
    "## 2. Layers",
    "## 3. Domains",
    "## 4. Canonical Entrypoints",
    "## 5. Registries",
    "## 6. Services",
    "## 7. Providers",
    "## 8. Governance Blocks",
    "## 9. Known Legacy / Transitional",
]
BASELINE_REFERENCES = ["arch_guard_config", "ARCHITECTURE_BASELINE", "Governance"]


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_script_exists():
    """Sentinel: scripts/dev/architecture_map.py existiert."""
    assert SCRIPT.exists(), (
        f"Architecture-Map-Skript fehlt: {SCRIPT}. "
        "Siehe docs/04_architecture/ARCHITECTURE_MAP_REPORT.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_generates_markdown():
    """Sentinel: Skript erzeugt ARCHITECTURE_MAP.md."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Skript fehlgeschlagen: {result.stderr}"
    assert OUTPUT_MD.exists(), "ARCHITECTURE_MAP.md wurde nicht erzeugt"


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_contains_required_sections():
    """Sentinel: Markdown enthält alle Kernsektionen."""
    if not OUTPUT_MD.exists():
        # Skript vorher ausführen
        subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_MD.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    assert not missing, (
        f"ARCHITECTURE_MAP.md fehlen Sektionen: {missing}. "
        "Erwartet: Executive Summary, Layers, Domains, Entrypoints, Registries, "
        "Services, Providers, Governance Blocks, Legacy/Transitional."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_references_baseline():
    """Sentinel: Ausgabe referenziert Baseline/Governance."""
    if not OUTPUT_MD.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_MD.read_text(encoding="utf-8")
    refs = [r for r in BASELINE_REFERENCES if r in content]
    assert len(refs) >= 2, (
        f"ARCHITECTURE_MAP.md referenziert zu wenig Baseline: {refs}. "
        "Erwartet: arch_guard_config, Governance, ARCHITECTURE_BASELINE."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_architecture_map_not_trivial():
    """Sentinel: Ausgabe ist nicht leer / nicht trivial."""
    if not OUTPUT_MD.exists():
        subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
    content = OUTPUT_MD.read_text(encoding="utf-8")
    assert len(content) > 500, "ARCHITECTURE_MAP.md ist zu kurz (trivial)"
    assert "GUI" in content and "Services" in content, "Kern-Layer fehlen"
