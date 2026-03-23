"""
Task canvas: prompt editor + quick test chat; model params in Inspector.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QSplitter, QTextEdit, QVBoxLayout, QWidget

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader


class PromptDevelopmentCanvas(WorkbenchCanvasBase):
    def __init__(self, prompt_id: str = "draft", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.prompt_id = prompt_id

        def _log(msg: str) -> None:
            win = self.window()
            if hasattr(win, "console_panel"):
                win.console_panel.log_output(f"[Prompt {prompt_id}] {msg}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(
            WorkflowCanvasHeader(
                "Develop prompt",
                "Iterate in the editor; test output below. Inspector: model & sampling.",
                [
                    ("Test Prompt", lambda: _log("Test Prompt (hook)")),
                    ("Save", lambda: _log("Save (hook)")),
                    ("Duplicate", lambda: _log("Duplicate (hook)")),
                    ("Assign to Agent", lambda: _log("Assign to Agent (hook)")),
                ],
                parent=self,
            )
        )

        split = QSplitter(Qt.Orientation.Vertical)
        top = QWidget(split)
        tl = QVBoxLayout(top)
        tl.setContentsMargins(12, 12, 12, 8)
        tl.addWidget(QLabel("Prompt"))
        self._editor = QPlainTextEdit(top)
        self._editor.setPlaceholderText("Write your system + user prompt here…")
        tl.addWidget(self._editor, 1)
        split.addWidget(top)
        bottom = QWidget(split)
        bl = QVBoxLayout(bottom)
        bl.setContentsMargins(12, 0, 12, 12)
        bl.addWidget(QLabel("Test chat (read-only stub)"))
        self._chat = QTextEdit(bottom)
        self._chat.setReadOnly(True)
        self._chat.setPlaceholderText("Test responses will appear here…")
        bl.addWidget(self._chat, 1)
        split.addWidget(bottom)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 1)
        outer.addWidget(split, 1)

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.WF_PROMPT_DEV

    @property
    def tab_key(self) -> str:
        return f"wf:prompt:{self.prompt_id}"

    @property
    def tab_title(self) -> str:
        return "Develop prompt"
