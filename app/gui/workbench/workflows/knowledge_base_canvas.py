"""
Task canvas: create/manage a knowledge base (name → folder → index → embeddings → ready).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QSplitter, QVBoxLayout, QWidget

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader


class KnowledgeBaseWorkflowCanvas(WorkbenchCanvasBase):
    def __init__(self, kb_id: str = "new-kb", display_name: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.kb_id = kb_id
        self.display_name = display_name or kb_id

        def _log(msg: str) -> None:
            win = self.window()
            if hasattr(win, "console_panel"):
                win.console_panel.log_output(f"[KB {self.display_name}] {msg}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(
            WorkflowCanvasHeader(
                f"Knowledge base · {self.display_name}",
                "Left: pipeline + files. Inspector: embedding, chunking, retriever.",
                [
                    ("Reindex", lambda: _log("Reindex (hook)")),
                    ("Add Files", lambda: _log("Add Files (hook)")),
                    ("Test Retrieval", lambda: _log("Test Retrieval (hook)")),
                ],
                parent=self,
            )
        )

        split = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget(split)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.setSpacing(8)
        ll.addWidget(QLabel("Setup steps"))
        self._steps = QListWidget(left)
        for label in (
            "1. Name",
            "2. Choose folder",
            "3. Index documents",
            "4. Generate embeddings",
            "5. Ready for use",
        ):
            QListWidgetItem(label, self._steps)
        self._steps.setMaximumHeight(140)
        self._steps.setCurrentRow(0)
        ll.addWidget(self._steps)
        ll.addWidget(QLabel("Indexed files"))
        self._files = QListWidget(left)
        self._files.addItem("(No files yet — use Add Files)")
        ll.addWidget(self._files, 1)
        ll.addWidget(QLabel("Index status: idle (stub)"))
        split.addWidget(left)
        preview = QLabel("Preview / diff area (stub)")
        preview.setWordWrap(True)
        preview.setObjectName("workbenchInspectorHint")
        split.addWidget(preview)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 1)
        outer.addWidget(split, 1)

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.WF_KNOWLEDGE_BASE

    @property
    def tab_key(self) -> str:
        return f"wf:knowledge:{self.kb_id}"

    @property
    def tab_title(self) -> str:
        return f"KB · {self.display_name}"
