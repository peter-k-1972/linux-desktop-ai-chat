"""
MetricsInspector – Inspector-Inhalt für Detailwerte.

CPU, Model Runtime, Request Count.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class MetricsInspector(QWidget):
    """Inspector für Metrics-Kontext im Runtime-/Debug-Bereich."""

    def __init__(
        self,
        cpu: str = "—",
        model_runtime: str = "—",
        request_count: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("metricsInspector")
        self._cpu = cpu
        self._model_runtime = model_runtime
        self._request_count = request_count
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("CPU Usage", self._cpu),
            ("Model Runtime", self._model_runtime),
            ("Request Count", self._request_count),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px; font-family: monospace;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()
