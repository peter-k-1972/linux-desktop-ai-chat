"""
ThemeManager – zentrale Steuerung des Theme-Systems.

Lädt Themes, wendet sie an, stellt Tokens bereit.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.registry import ThemeRegistry
from app.gui.themes.loader import load_stylesheet
from app.gui.themes.canonical_token_ids import flat_key


class ThemeManager(QObject):
    """
    Singleton ThemeManager.
    - Lädt und aktiviert Themes
    - Stellt Tokens bereit
    - Emittiert theme_changed für spätere Settings-Integration
    """

    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._registry = ThemeRegistry()
        self._current: ThemeDefinition | None = None
        self._current_id: str = "light_default"

    @property
    def registry(self) -> ThemeRegistry:
        """Registry mit allen Built-in- und Benutzer-Themes."""
        return self._registry

    def reload_themes(self) -> None:
        """
        Registry neu laden (z. B. nach Theme-Import) und aktuelles Theme erneut anwenden.
        """
        cid = self._current_id
        self._registry.reload_themes()
        if self._registry.get(cid):
            self.set_theme(cid)
        else:
            self.set_theme("light_default")

    def set_theme(self, theme_id: str) -> bool:
        """
        Aktiviert ein Theme.
        Gibt True zurück bei Erfolg.
        """
        theme = self._registry.get(theme_id)
        if not theme:
            return False
        self._current = theme
        self._current_id = theme_id
        stylesheet = load_stylesheet(theme)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
        self.theme_changed.emit(theme_id)
        return True

    def get_theme(self) -> ThemeDefinition | None:
        """Liefert das aktuell aktive Theme."""
        if not self._current:
            self.set_theme(self._current_id)
        return self._current

    def get_current_id(self) -> str:
        """ID des aktuellen Themes."""
        return self._current_id

    def get_tokens(self) -> dict[str, str]:
        """
        Liefert die Design-Tokens des aktuellen Themes.
        Für Widgets, die Tokens programmatisch nutzen.
        """
        theme = self.get_theme()
        if not theme:
            return {}
        return theme.get_tokens_dict()

    def color(self, token: str) -> str:
        """
        Löst eine Farbe aus dem aktiven Theme.

        ``token`` ist kanonisch (``color.fg.primary``) oder flach (``color_fg_primary``).
        """
        if not token:
            return ""
        tokens = self.get_tokens()
        flat = flat_key(token) if "." in token else token
        return tokens.get(flat) or tokens.get(token, "")

    def get_stylesheet(self) -> str:
        """Liefert das vollständige Stylesheet des aktuellen Themes."""
        theme = self.get_theme()
        if not theme:
            return ""
        return load_stylesheet(theme)

    def list_themes(self) -> list[tuple[str, str]]:
        """[(id, name), ...] aller verfügbaren Themes."""
        return self._registry.list_themes()


_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    """Singleton-Zugriff auf den ThemeManager."""
    global _manager
    if _manager is None:
        _manager = ThemeManager()
    return _manager
