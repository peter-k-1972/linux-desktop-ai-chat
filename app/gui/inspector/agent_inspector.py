"""
AgentInspector – Inspector-Inhalt für Agent-Details.

Rolle, Modellbindung, Toolset, Status.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class AgentInspector(QWidget):
    """Inspector für Agent-Kontext im Control Center (Verwaltungssicht)."""

    def __init__(
        self,
        agent: str = "(keine)",
        role: str = "—",
        model_binding: str = "—",
        toolset: str = "—",
        status: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("agentInspector")
        self._agent = agent
        self._role = role
        self._model_binding = model_binding
        self._toolset = toolset
        self._status = status
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Agent", self._agent),
            ("Rolle", self._role),
            ("Modellbindung", self._model_binding),
            ("Toolset", self._toolset),
            ("Status", self._status),
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
