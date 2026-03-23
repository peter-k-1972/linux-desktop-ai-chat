"""
Task canvas: open an agent and chat/test in one place; inspector holds config/runtime sections.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QSplitter, QVBoxLayout, QWidget

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader


class AgentTestCanvas(WorkbenchCanvasBase):
    """Explorer / Tasks → Test Agent; header actions are wired to console stubs until services exist."""

    def __init__(self, agent_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.agent_id = agent_id
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        def _log(msg: str) -> None:
            win = self.window()
            if hasattr(win, "console_panel"):
                win.console_panel.log_output(f"[Agent {agent_id}] {msg}")

        outer.addWidget(
            WorkflowCanvasHeader(
                f"Test agent · {agent_id}",
                "Chat on the left; configuration and runtime live in the Inspector.",
                [
                    ("Run Agent", lambda: _log("Run Agent (hook)")),
                    ("Reset Context", lambda: _log("Reset Context (hook)")),
                    ("Duplicate Agent", lambda: _log("Duplicate Agent (hook)")),
                    ("Open Full Settings", lambda: _log("Open Full Settings (hook)")),
                ],
                parent=self,
            )
        )

        split = QSplitter(self)
        split.setOrientation(Qt.Orientation.Horizontal)
        left = QWidget(split)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.addWidget(QLabel("Chat / test"))
        self._transcript = QPlainTextEdit(left)
        self._transcript.setPlaceholderText("Agent replies will appear here…")
        self._transcript.setReadOnly(True)
        ll.addWidget(self._transcript, 1)
        row = QHBoxLayout()
        self._input = QLineEdit(left)
        self._input.setPlaceholderText("Message the agent…")
        send = QPushButton("Send")
        send.clicked.connect(lambda: self._on_send(_log))
        row.addWidget(self._input, 1)
        row.addWidget(send)
        ll.addLayout(row)
        split.addWidget(left)
        hint = QLabel("Inspector → Configuration, Runtime, Context, Tools, Memory")
        hint.setWordWrap(True)
        hint.setObjectName("workbenchInspectorHint")
        split.addWidget(hint)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 1)
        outer.addWidget(split, 1)

    def _on_send(self, log) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._transcript.appendPlainText(f"You: {text}")
        self._input.clear()
        log(f"Send stub: {text!r}")

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.WF_AGENT_TEST

    @property
    def tab_key(self) -> str:
        return f"wf:agent-test:{self.agent_id}"

    @property
    def tab_title(self) -> str:
        return f"Test · {self.agent_id}"
