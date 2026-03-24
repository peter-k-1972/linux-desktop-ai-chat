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
from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelState


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

        self._read_summary = QLabel("")
        self._read_summary.setObjectName("agentTaskPanelReadSummary")
        self._read_summary.setWordWrap(True)
        self._read_summary.setStyleSheet("font-size: 12px; color: #4b5563;")
        layout.addWidget(self._read_summary)

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

    def apply_task_panel_state(self, state: AgentTaskPanelState) -> None:
        """Slice 4: reiner Read-Zustand aus Presenter (keine Service-Aufrufe)."""
        if not isinstance(state, AgentTaskPanelState):
            return
        if state.phase == "loading":
            self._read_summary.setText("Tasks werden geladen …")
            return
        if state.phase == "error":
            self._read_summary.setText(state.error_message or "Fehler.")
            return
        if state.panel is None:
            self._read_summary.clear()
            return
        p = state.panel
        parts = [f"Zugeordnete Tasks (DebugStore): {p.task_count}"]
        if p.recent_tasks:
            parts.append("Zuletzt:")
            parts.extend(f"• {line}" for line in p.recent_tasks)
        self._read_summary.setText("\n".join(parts))

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
