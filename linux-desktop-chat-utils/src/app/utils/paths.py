"""
Central path resolution for the application.

Provides project root and assets directory for icons, themes, and media.
Assets are consolidated in assets/ at project root (see ARCHITECTURE_PROPOSAL).
"""

from __future__ import annotations

import os
from pathlib import Path

# Relativer Default für Legacy-Konfiguration (icons_path); kein UI-Laden — nur Konstante zentral.
DEFAULT_LEGACY_ICONS_PATH_STR = "assets/icons"

_PROJECT_ROOT: Path | None = None


def get_project_root() -> Path:
    """Project root (directory containing app/, docs/, assets/, etc.)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    env = os.environ.get("LDC_REPO_ROOT", "").strip()
    if env:
        _PROJECT_ROOT = Path(env).resolve()
        return _PROJECT_ROOT
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "linux-desktop-chat-features").is_dir():
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT
    # Legacy: Host-Layout app/utils/paths.py → drei Ebenen zum Repo-Root.
    _PROJECT_ROOT = here.parent.parent.parent
    return _PROJECT_ROOT


def get_assets_dir() -> Path:
    """Assets directory (icons, themes, media)."""
    return get_project_root() / "assets"


def get_icons_dir() -> Path:
    """Icons directory. SVG registry icons: assets/icons/svg/. Legacy icons: assets/icons/."""
    return get_assets_dir() / "icons"


def get_resource_icons_root() -> Path:
    """Design-system icon root (taxonomy under ``resources/icons/``). See docs/design/ICON_STYLE_GUIDE.md."""
    return get_project_root() / "resources" / "icons"


def get_themes_dir() -> Path:
    """Themes directory. Base QSS: assets/themes/base/."""
    return get_assets_dir() / "themes"
