"""
Theme-ID helpers: registered IDs (source: ThemeRegistry) and legacy light/dark bucket.

Used by AppSettings validation, theme changer persistence, and help UI that only knows light|dark.
"""

from __future__ import annotations


def registered_theme_ids() -> frozenset[str]:
    """Alle Theme-IDs der laufenden :class:`ThemeManager`-Registry (Built-ins + installiert)."""
    try:
        from app.gui.themes.manager import get_theme_manager

        return frozenset(tid for tid, _ in get_theme_manager().list_themes())
    except Exception:
        from app.gui.themes.registry import ThemeRegistry

        return frozenset(tid for tid, _ in ThemeRegistry().list_themes())


def is_registered_theme_id(theme_id: str) -> bool:
    return theme_id in registered_theme_ids()


def theme_id_to_legacy_light_dark(theme_id: str) -> str:
    """
    Map ``theme_id`` to persisted ``AppSettings.theme`` / help styling.

    Only ``light_default`` is ``light``; all other registered themes use the dark bucket
    (including ``dark_default`` and ``workbench``).
    """
    if theme_id == "light_default":
        return "light"
    return "dark"
