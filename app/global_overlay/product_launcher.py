"""
Kanonischer GUI-Produktlauncher (Repository-Wurzel).

Recovery- und Relaunch-Pfade (Overlay, GUI-Switching) nutzen **denselben**
Pfad wie ein manueller Produktstart — zentral hier abgeleitet, nicht verstreut.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from app.gui_registry import resolve_repo_root

CANONICAL_GUI_LAUNCHER_SCRIPT: Final[str] = "run_gui_shell.py"


def resolve_canonical_gui_launcher_path() -> Path:
    """Absoluter Pfad zu ``run_gui_shell.py`` unter :func:`resolve_repo_root`."""
    return (resolve_repo_root() / CANONICAL_GUI_LAUNCHER_SCRIPT).resolve()


def canonical_gui_launcher_is_present() -> bool:
    """True wenn der Launcher im erwarteten Repo-Layout existiert."""
    try:
        return resolve_canonical_gui_launcher_path().is_file()
    except Exception:
        return False
