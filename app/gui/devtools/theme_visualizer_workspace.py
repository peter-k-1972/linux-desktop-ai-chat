"""
Runtime/Debug-Workspace: Einstieg zum Theme-Visualizer (separates Fenster).

Sichtbar nur wenn Devtools per Env freigeschaltet sind.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ThemeVisualizerEntryWorkspace(QWidget):
    """Kurze Erklärung + Aktion — kein eingebetteter Voll-Visualizer im Stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rd_theme_visualizerWorkspace")

        lay = QVBoxLayout(self)
        title = QLabel("<h2>Theme Visualizer</h2>")
        title.setWordWrap(True)
        lay.addWidget(title)
        body = QLabel(
            "Öffnet das QA-Tool in einem eigenen Fenster. "
            "Theme-Vorschau wirkt nur im Visualizer-Fenster; die Shell behält ihr aktives Theme."
        )
        body.setWordWrap(True)
        lay.addWidget(body)

        btn = QPushButton("Theme Visualizer öffnen…")
        btn.clicked.connect(self._open)
        lay.addWidget(btn)
        lay.addStretch(1)

    @staticmethod
    def workspace_id() -> str:
        return "rd_theme_visualizer"

    def _open(self) -> None:
        from app.gui.devtools.theme_visualizer_launcher import open_theme_visualizer

        open_theme_visualizer(self.window())
