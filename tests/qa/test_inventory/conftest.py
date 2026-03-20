"""
Pytest Fixtures für QA Test Inventory Tests.

Stellt minimale Catalog-Fixtures und Hilfsfunktionen bereit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "qa" / "build_test_inventory.py"


def _minimal_catalog_content() -> str:
    """Minimaler REGRESSION_CATALOG für Tests."""
    return """# Test Catalog

## Zuordnung: Tests → Fehlerklassen

### failure_modes/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_chroma_unreachable | test_rag_service_handles_chroma_unreachable | rag_silent_failure |
| test_rag_retrieval_failure | test_chat_continues_when_rag_fails | rag_silent_failure |

### async_behavior/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_signal_after_widget_destroy | test_signal_after_widget_destroy_no_crash | late_signal_use_after_destroy |

## Historische Bugs
"""


@pytest.fixture
def minimal_catalog_path(tmp_path: Path) -> Path:
    """Minimaler REGRESSION_CATALOG.md für isolierte Tests."""
    catalog = tmp_path / "REGRESSION_CATALOG.md"
    catalog.write_text(_minimal_catalog_content(), encoding="utf-8")
    return catalog


@pytest.fixture
def empty_catalog_path(tmp_path: Path) -> Path:
    """Leerer Catalog (nur Header, keine Zuordnung)."""
    catalog = tmp_path / "REGRESSION_CATALOG.md"
    catalog.write_text("# Test Catalog\n\n## Zuordnung\n\n## Historische Bugs\n", encoding="utf-8")
    return catalog


def run_build_test_inventory(
    args: list[str],
    cwd: Path | None = None,
) -> tuple[int, str, str]:
    """Führt build_test_inventory.py aus. cwd=None => Projekt-Root."""
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH)] + args,
        cwd=str(cwd or _PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr
