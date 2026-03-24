"""
JSON-Theme-Dateien laden (Import-Pipeline).

Unabhängig von :mod:`app.gui.themes.loader` (QSS/stylesheet).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ThemeLoadError(Exception):
    """Theme-Datei nicht lesbar oder kein gültiges JSON."""


def load_theme_file(path: str) -> dict[str, Any]:
    """
    Liest eine Theme-JSON-Datei und liefert ein Dict.

    :raises ThemeLoadError: bei fehlender Datei, IO- oder JSON-Fehlern.
    """
    p = Path(path).expanduser()
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise ThemeLoadError(f"Theme-Datei konnte nicht gelesen werden: {path}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ThemeLoadError(f"Ungültiges JSON in Theme-Datei: {path}") from exc
    if not isinstance(data, dict):
        raise ThemeLoadError("Theme-JSON muss ein Objekt (Dict) sein.")
    return data
