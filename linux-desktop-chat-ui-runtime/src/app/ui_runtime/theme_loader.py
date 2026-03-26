"""Datei-Laden und Parsing von Theme-Manifesten (JSON)."""

from __future__ import annotations

import json
from pathlib import Path

from app.ui_runtime.manifest_models import ThemeManifest, theme_manifest_from_dict


def load_theme_manifest_from_path(path: Path) -> ThemeManifest:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Manifest muss ein JSON-Objekt sein")
    return theme_manifest_from_dict(data, source_path=path.resolve())
