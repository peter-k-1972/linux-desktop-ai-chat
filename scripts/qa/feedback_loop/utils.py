"""
QA Feedback Loop – Hilfsfunktionen.

Deterministische Utilities für Pfade, JSON, Typen.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Projekt-Root: scripts/qa/feedback_loop/ -> 4 Ebenen hoch
_FEEDBACK_LOOP_DIR = Path(__file__).resolve().parent
_QA_DIR = _FEEDBACK_LOOP_DIR.parent
_SCRIPTS_DIR = _QA_DIR.parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent

DEFAULT_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"
DEFAULT_INCIDENTS_DIR = DEFAULT_DOCS_QA / "incidents"


def get_project_root() -> Path:
    """Projekt-Root-Verzeichnis."""
    return _PROJECT_ROOT


def get_docs_qa_dir(base: Path | None = None) -> Path:
    """docs/qa Verzeichnis."""
    return (base or _PROJECT_ROOT) / "docs" / "qa"


def get_incidents_dir(base: Path | None = None) -> Path:
    """docs/qa/incidents Verzeichnis."""
    return get_docs_qa_dir(base) / "incidents"


def load_json(path: Path | None) -> dict[str, Any] | None:
    """Lädt JSON-Datei. Gibt None bei Fehler oder fehlender Datei."""
    if path is None:
        return None
    if not path.exists() or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def safe_get(data: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    """Sichere verschachtelte Dict-Zugriffe. keys = "a", "b", "c" -> data["a"]["b"]["c"]."""
    if data is None:
        return default
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        if key not in current:
            return default
        current = current[key]
    return current
