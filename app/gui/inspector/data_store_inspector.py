"""
DataStoreInspector – Inspector-Inhalt für Data-Store-Details.

Typ, Zustand, Nutzung, Health.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class DataStoreInspector(QWidget):
    """Inspector für Data-Store-Kontext im Control Center."""

    def __init__(
        self,
        store_type: str = "(keine)",
        state: str = "—",
        usage: str = "—",
        health: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("dataStoreInspector")
        self._store_type = store_type
        self._state = state
        self._usage = usage
        self._health = health
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Typ", self._store_type),
            ("Zustand", self._state),
            ("Nutzung / Health", f"{self._usage} · {self._health}"),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()
