"""
Shell-Stile – Delegation an Theme-System.

DEPRECATED: Nutze app.gui.themes.get_theme_manager() direkt.
Diese Module bleibt für Rückwärtskompatibilität.
"""

from app.gui.themes import get_theme_manager


def get_shell_stylesheet(theme: str = "light") -> str:
    """
    Liefert das vollständige Stylesheet.
    Mapped 'light' -> light_default, 'dark' -> dark_default.
    """
    theme_id = "light_default" if theme == "light" else "dark_default"
    manager = get_theme_manager()
    manager.set_theme(theme_id)
    return manager.get_stylesheet()
