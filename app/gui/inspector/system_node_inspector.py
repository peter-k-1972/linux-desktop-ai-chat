"""
SystemNodeInspector – Inspector für Node-Details im System Graph.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class SystemNodeInspector(QWidget):
    """Inspector für System-Node-Kontext im Runtime-/Debug-Bereich."""

    def __init__(
        self,
        node: str = "(keine)",
        status: str = "—",
        connections: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("systemNodeInspector")
        self._node = node
        self._status = status
        self._connections = connections
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Node", self._node),
            ("Status", self._status),
            ("Connections", self._connections),
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
