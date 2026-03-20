"""
ModelInspector – Inspector-Inhalt für Model-Details.

Modellname, Status, Größe, Typ, Metadaten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class ModelInspector(QWidget):
    """Inspector für Model-Kontext im Control Center."""

    def __init__(
        self,
        model_name: str = "(keine)",
        status: str = "—",
        size: str = "—",
        model_type: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("modelInspector")
        self._model_name = model_name
        self._status = status
        self._size = size
        self._model_type = model_type
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Modell", self._model_name),
            ("Status", self._status),
            ("Größe / Typ", f"{self._size} · {self._model_type}"),
            ("Metadaten", "Context: 128k · Backend: Ollama"),
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
