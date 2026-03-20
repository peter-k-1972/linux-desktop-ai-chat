"""
Architektur-Guard: Root-Entrypoint Governance.

Prüft, dass im Projekt-Root nur definierte Startskripte (.py, .sh) existieren.
Neue Startskripte ohne Architektur-Review fallen auf.

Regeln: docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md
Config: tests/architecture/arch_guard_config.ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS
"""

import pytest
from pathlib import Path

from tests.architecture.arch_guard_config import (
    ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS,
    PROJECT_ROOT,
)


def _get_root_scripts() -> set[str]:
    """Sammelt alle .py und .sh Dateien im Projekt-Root."""
    scripts = set()
    for ext in (".py", ".sh"):
        for path in PROJECT_ROOT.glob(f"*{ext}"):
            if path.is_file():
                scripts.add(path.name)
    return scripts


@pytest.mark.architecture
@pytest.mark.contract
def test_root_entrypoint_scripts_are_allowed():
    """
    Sentinel: Nur erlaubte Startskripte im Projekt-Root.

    Verhindert Drift durch neue Root-Skripte ohne Architektur-Review.
    Neue Skripte müssen in ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS ergänzt werden.
    """
    root_scripts = _get_root_scripts()
    unexpected = root_scripts - ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS
    assert not unexpected, (
        f"Root-Entrypoint Governance: Unerwartete Skripte im Projekt-Root: {sorted(unexpected)}. "
        f"Erlaubt: {sorted(ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS)}. "
        "Neue Startskripte erfordern Architektur-Review und Eintrag in ROOT_ENTRYPOINT_POLICY.md."
    )


@pytest.mark.architecture
@pytest.mark.contract
def test_allowed_root_entrypoints_exist():
    """
    Sentinel: Alle definierten Root-Entrypoints existieren.
    """
    missing = []
    for name in ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS:
        path = PROJECT_ROOT / name
        if not path.exists():
            missing.append(name)
    assert not missing, (
        f"Root-Entrypoint Governance: Erwartete Skripte fehlen: {missing}. "
        f"Siehe arch_guard_config.ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS."
    )
