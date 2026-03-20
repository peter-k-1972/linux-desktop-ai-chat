"""
AgentTaskPanel – Task starten: Prompt eingeben, Agent auswählen.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Signal
from app.gui.shared import BasePanel


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


class AgentTaskPanel(BasePanel):
    """Eingabe: Prompt, Agent-Auswahl, Start-Button."""

    task_requested = Signal(str, str)  # agent_id, prompt

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentTaskPanel")
        self.setMinimumHeight(140)
        self._agents: list = []
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Task starten")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._prompt = QTextEdit()
        self._prompt.setPlaceholderText("Auftrag oder Frage an den Agenten…")
        self._prompt.setMaximumHeight(80)
        self._prompt.setStyleSheet(
            "QTextEdit { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px; }"
        )
        layout.addWidget(self._prompt)

        row = QHBoxLayout()
        self._agent_combo = QComboBox()
        self._agent_combo.setMinimumWidth(200)
        self._agent_combo.setStyleSheet(
            "QComboBox { border: 1px solid #d1d5db; border-radius: 8px; padding: 6px; }"
        )
        row.addWidget(QLabel("Agent:"))
        row.addWidget(self._agent_combo, 1)

        self._start_btn = QPushButton("Task starten")
        self._start_btn.setStyleSheet(
            "QPushButton { background: #8b5cf6; color: white; border-radius: 8px; "
            "padding: 8px 16px; font-weight: 600; }"
            "QPushButton:hover { background: #7c3aed; }"
            "QPushButton:disabled { background: #9ca3af; }"
        )
        self._start_btn.clicked.connect(self._on_start)
        row.addWidget(self._start_btn)

        layout.addLayout(row)

    def set_agents(self, agents: list) -> None:
        """Setzt die Agentenliste für die ComboBox."""
        self._agents = agents
        self._agent_combo.clear()
        if not agents:
            self._agent_combo.addItem("Bitte Projekt auswählen", None)
        else:
            for p in agents:
                self._agent_combo.addItem(p.effective_display_name, p.id)
            self._agent_combo.setCurrentIndex(0)

    def set_selected_agent(self, agent_id: str) -> None:
        """Wählt einen Agenten per ID."""
        for i in range(self._agent_combo.count()):
            if self._agent_combo.itemData(i) == agent_id:
                self._agent_combo.setCurrentIndex(i)
                break

    def set_sending(self, sending: bool) -> None:
        """Deaktiviert Start-Button während Task läuft."""
        self._start_btn.setEnabled(not sending)

    def _on_start(self) -> None:
        prompt = (self._prompt.toPlainText() or "").strip()
        if not prompt:
            return
        agent_id = self._agent_combo.currentData()
        if not agent_id:
            return
        self.task_requested.emit(agent_id, prompt)
