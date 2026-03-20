"""
RuntimeAgentInspector – Inspector für Agent-Details im Runtime-Bereich.

Current Task, Status, Last Action.
Unterscheidet sich von AgentInspector (Control Center Verwaltungssicht).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class RuntimeAgentInspector(QWidget):
    """Inspector für Agent-Kontext im Runtime-/Debug-Bereich (Laufzeit-Ansicht)."""

    def __init__(
        self,
        agent: str = "(keine)",
        current_task: str = "—",
        status: str = "—",
        last_action: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("runtimeAgentInspector")
        self._agent = agent
        self._current_task = current_task
        self._status = status
        self._last_action = last_action
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Agent", self._agent),
            ("Current Task", self._current_task),
            ("Status", self._status),
            ("Last Action", self._last_action),
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
