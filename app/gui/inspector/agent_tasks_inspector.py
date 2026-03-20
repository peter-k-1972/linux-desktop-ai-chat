"""AgentTasksInspector – Inspector-Inhalt für Agent Tasks."""

from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

from app.agents.agent_task_runner import AgentTaskResult


class AgentTasksInspector(QWidget):
    """Inspector für Agent Tasks: Agentenstatus, Task-Kontext, letztes Ergebnis."""

    def __init__(
        self,
        last_result: Optional[AgentTaskResult] = None,
        sending: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("agentTasksInspector")
        self._last_result = last_result
        self._sending = sending
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        status = "Wird gesendet…" if self._sending else "Bereit"
        if self._last_result:
            if self._last_result.success:
                status = f"Abgeschlossen: {self._last_result.agent_name}"
            else:
                status = f"Fehler: {self._last_result.error or 'Unbekannt'}"

        for title, text in [
            ("Agentenstatus", status),
            ("Task-Kontext", self._format_task_context()),
            ("Tool / Model", self._format_model_info()),
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

    def _format_task_context(self) -> str:
        if not self._last_result:
            return "Aktiver Task, Delegationen."
        p = (self._last_result.prompt or "")[:80]
        if len(self._last_result.prompt or "") > 80:
            p += "…"
        return f"Agent: {self._last_result.agent_name}\nPrompt: {p}"

    def _format_model_info(self) -> str:
        if not self._last_result or not self._last_result.model:
            return "Modell wird bei Task-Ausführung angezeigt."
        return f"Modell: {self._last_result.model}\nDauer: {self._last_result.duration_sec:.1f}s"
