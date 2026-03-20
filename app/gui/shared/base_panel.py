"""
BasePanel – Basis für Dashboard- und Domain-Panels.

Einheitliche Schnittstelle für Karten und Panels.
"""

from PySide6.QtWidgets import QFrame


class BasePanel(QFrame):
    """Basisklasse für Panel-Komponenten (Karten, Explorer, etc.)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("basePanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)

    def refresh(self) -> None:
        """Lädt Daten neu. Override in Subklassen."""
        pass
