"""
InspectorHost – Host für kontextabhängige Inspector-Panels.

Zeigt Kontext, Auswahl, Details. set_content() für dynamischen Inhalt.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QStackedWidget,
)
from PySide6.QtCore import Qt


class InspectorHost(QWidget):
    """Host-Container für Inspector-Panels. Unterstützt dynamischen Inhalt."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inspectorHost")
        self._stack = QStackedWidget()
        self._content_token = 0
        self._setup_default_content()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)

    def _setup_default_content(self):
        """Standard-Platzhalter."""
        default = QWidget()
        layout = QVBoxLayout(default)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        for title, text in [
            ("Kontext", "Kein Kontext ausgewählt."),
            ("Auswahl", "Wählen Sie ein Objekt aus."),
            ("Details", "Objektinformationen erscheinen hier."),
        ]:
            group = QGroupBox(title)
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setObjectName("panelMeta")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()
        self._stack.addWidget(default)

    def set_content(self, widget: QWidget, content_token: int | None = None) -> None:
        """Setzt den Inspector-Inhalt. Ersetzt vorherigen dynamischen Inhalt.
        content_token: Optional. Wenn gesetzt und != _content_token, wird verworfen (stale)."""
        if content_token is not None and content_token != self._content_token:
            widget.deleteLater()
            return
        # Entferne vorherigen Custom-Content (Index 1 falls vorhanden)
        while self._stack.count() > 1:
            w = self._stack.widget(1)
            self._stack.removeWidget(w)
            w.deleteLater()
        self._stack.addWidget(widget)
        self._stack.setCurrentIndex(1)

    def prepare_for_setup(self) -> int:
        """Löscht Inhalt und gibt Token für nachfolgendes set_content. Verhindert stale Updates."""
        self._content_token += 1
        self.clear_content()
        return self._content_token

    def clear_content(self) -> None:
        """Zeigt wieder den Standard-Platzhalter."""
        while self._stack.count() > 1:
            w = self._stack.widget(1)
            self._stack.removeWidget(w)
            w.deleteLater()
        self._stack.setCurrentIndex(0)
