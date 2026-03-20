"""
Central path resolution for the application.

Provides project root and assets directory for icons, themes, and media.
Assets are consolidated in assets/ at project root (see ARCHITECTURE_PROPOSAL).
"""

from pathlib import Path

_PROJECT_ROOT: Path | None = None


def get_project_root() -> Path:
    """Project root (directory containing app/, docs/, assets/, etc.)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        # app/utils/paths.py -> app/utils -> app -> project root
        _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    return _PROJECT_ROOT


def get_assets_dir() -> Path:
    """Assets directory (icons, themes, media)."""
    return get_project_root() / "assets"


def get_icons_dir() -> Path:
    """Icons directory. SVG registry icons: assets/icons/svg/. Legacy icons: assets/icons/."""
    return get_assets_dir() / "icons"


def get_themes_dir() -> Path:
    """Themes directory. Base QSS: assets/themes/base/."""
    return get_assets_dir() / "themes"
