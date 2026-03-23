"""
Base type and placeholder canvas implementations for the Workbench tab strip.

Domain panels will replace these widgets later; the tab router keys on ``tab_key``.
"""

from __future__ import annotations

from enum import Enum, auto

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.gui.workbench.ui import EmptyStateWidget


class CanvasKind(Enum):
    AGENT = auto()
    WORKFLOW = auto()
    CHAT = auto()
    FILE = auto()
    FEATURE = auto()
    AI_CANVAS = auto()
    WF_AGENT_TEST = auto()
    WF_KNOWLEDGE_BASE = auto()
    WF_WORKFLOW_BUILDER = auto()
    WF_PROMPT_DEV = auto()
    WF_MODEL_COMPARE = auto()


class WorkbenchCanvasBase(QWidget):
    """Canvas page shown inside :class:`CanvasTabs`."""

    @property
    def canvas_kind(self) -> CanvasKind:
        raise NotImplementedError

    @property
    def tab_key(self) -> str:
        raise NotImplementedError

    @property
    def tab_title(self) -> str:
        raise NotImplementedError


class _PlaceholderCanvas(WorkbenchCanvasBase):
    """Guided placeholder until domain UIs are embedded."""

    def __init__(self, kind: CanvasKind, key: str, title: str, *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._kind = kind
        self._key = key
        self._title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        hint = (
            "Use the explorer or Command Palette (Ctrl+Shift+P) to open related tools. "
            "The inspector on the right will show context when domain panels are wired in."
        )
        layout.addWidget(
            EmptyStateWidget(
                title,
                f"This is a placeholder for the {kind.name.replace('_', ' ').lower()} experience.",
                hint,
                parent=self,
            )
        )
        layout.addStretch(1)

    @property
    def canvas_kind(self) -> CanvasKind:
        return self._kind

    @property
    def tab_key(self) -> str:
        return self._key

    @property
    def tab_title(self) -> str:
        return self._title


class AgentEditorCanvas(_PlaceholderCanvas):
    def __init__(self, agent_id: str, parent: QWidget | None = None) -> None:
        super().__init__(
            CanvasKind.AGENT,
            f"agent:{agent_id}",
            f"Agent: {agent_id}",
            parent=parent,
        )
        self.agent_id = agent_id


class WorkflowEditorCanvas(_PlaceholderCanvas):
    def __init__(self, workflow_id: str, parent: QWidget | None = None) -> None:
        super().__init__(
            CanvasKind.WORKFLOW,
            f"workflow:{workflow_id}",
            f"Workflow: {workflow_id}",
            parent=parent,
        )
        self.workflow_id = workflow_id


class ChatCanvas(_PlaceholderCanvas):
    def __init__(self, session_key: str = "default", parent: QWidget | None = None) -> None:
        super().__init__(
            CanvasKind.CHAT,
            f"chat:{session_key}",
            "Chat",
            parent=parent,
        )
        self.session_key = session_key


class FileViewerCanvas(_PlaceholderCanvas):
    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(
            CanvasKind.FILE,
            f"file:{file_path}",
            file_path.split("/")[-1] or file_path,
            parent=parent,
        )
        self.file_path = file_path


class StubFeatureCanvas(_PlaceholderCanvas):
    """Placeholder page for explorer targets until domain panels are embedded."""

    def __init__(self, feature_key: str, title: str, parent: QWidget | None = None) -> None:
        super().__init__(
            CanvasKind.FEATURE,
            f"feature:{feature_key}",
            title,
            parent=parent,
        )
        self.feature_key = feature_key
