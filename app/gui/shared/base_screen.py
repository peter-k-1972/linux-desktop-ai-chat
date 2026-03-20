"""
BaseScreen – Basis für alle Workspace-Screens.

Einheitliche Schnittstelle: area_id, refresh(), refresh_theme().
"""

from PySide6.QtWidgets import QWidget


class BaseScreen(QWidget):
    """Basisklasse für alle Screen-Komponenten."""

    def __init__(self, area_id: str, parent=None):
        super().__init__(parent)
        self._area_id = area_id
        self.setObjectName(f"{area_id}Screen")

    @property
    def area_id(self) -> str:
        """Eindeutige ID des Screens (z.B. command_center, operations)."""
        return self._area_id

    def refresh(self) -> None:
        """Lädt Daten neu. Override in Subklassen."""
        pass

    def refresh_theme(self, theme: str = "light") -> None:
        """Aktualisiert Theme. Override in Subklassen."""
        pass
