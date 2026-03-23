"""
Task canvas: one prompt, multiple model columns for side-by-side comparison.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QScrollArea, QTextEdit, QVBoxLayout, QWidget

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader


class _ModelColumn(QWidget):
    def __init__(self, model_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        title = QLabel(model_name)
        title.setObjectName("workbenchPanelHeaderTitle")
        lay.addWidget(title)
        self.response = QTextEdit(self)
        self.response.setReadOnly(True)
        self.response.setPlaceholderText("Response…")
        lay.addWidget(self.response, 1)
        self.stats = QLabel("Tokens: — (stub)")
        self.stats.setObjectName("workbenchInspectorHint")
        lay.addWidget(self.stats)


class ModelCompareCanvas(WorkbenchCanvasBase):
    def __init__(self, compare_id: str = "session-1", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.compare_id = compare_id
        self._columns: list[_ModelColumn] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(
            WorkflowCanvasHeader(
                "Compare models",
                "Same prompt across models. Add columns, run once, export when satisfied.",
                [
                    ("Add Model", lambda: self._add_column()),
                    ("Run Comparison", lambda: self._notify("Run Comparison (hook)")),
                    ("Export Results", lambda: self._notify("Export Results (hook)")),
                ],
                parent=self,
            )
        )

        prompt_wrap = QWidget(self)
        pl = QVBoxLayout(prompt_wrap)
        pl.setContentsMargins(12, 12, 12, 8)
        pl.addWidget(QLabel("Shared prompt"))
        self._prompt = QPlainTextEdit(prompt_wrap)
        self._prompt.setPlaceholderText("Enter the prompt to send to every selected model…")
        self._prompt.setMaximumHeight(140)
        pl.addWidget(self._prompt)
        outer.addWidget(prompt_wrap)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        host = QWidget()
        self._row = QHBoxLayout(host)
        self._row.setContentsMargins(12, 0, 12, 12)
        self._row.setSpacing(12)
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)

        self._add_column("Model A")
        self._add_column("Model B")

    def _notify(self, msg: str) -> None:
        win = self.window()
        if hasattr(win, "console_panel"):
            win.console_panel.log_output(f"[Compare] {msg}")

    def _add_column(self, name: str | None = None) -> None:
        idx = len(self._columns) + 1
        col = _ModelColumn(name or f"Model {idx}", self)
        self._columns.append(col)
        self._row.addWidget(col, 1)
        self._notify(f"Added column: {name or f'Model {idx}'}")

    def model_column_count(self) -> int:
        return len(self._columns)

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.WF_MODEL_COMPARE

    @property
    def tab_key(self) -> str:
        return f"wf:model-compare:{self.compare_id}"

    @property
    def tab_title(self) -> str:
        return "Compare models"
