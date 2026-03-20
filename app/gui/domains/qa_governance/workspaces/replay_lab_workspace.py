"""
ReplayLabWorkspace – Replay Cases, Status, letzte Runs.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.qa_governance.workspaces.base_analysis_workspace import BaseAnalysisWorkspace
from app.gui.domains.qa_governance.panels.replay_lab_panels import (
    ReplayListPanel,
    ReplaySummaryPanel,
    ReplayDetailPanel,
)


class ReplayLabWorkspace(BaseAnalysisWorkspace):
    """Workspace für Replay Lab."""

    def __init__(self, parent=None):
        super().__init__("qa_replay_lab", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(ReplaySummaryPanel(self))

        self._list_panel = ReplayListPanel(self)
        self._list_panel.replay_selected.connect(self._on_replay_selected)
        content_layout.addWidget(self._list_panel)

        self._detail_panel = ReplayDetailPanel(self)
        content_layout.addWidget(self._detail_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _on_replay_selected(self, replay):
        self._detail_panel.set_replay(replay)
        if self._inspector_host:
            from app.gui.inspector.replay_inspector import ReplayInspector
            content = ReplayInspector(
                replay_id=replay.id,
                status=replay.status,
                last_run="—",
                result_summary="—",
            )
            self._inspector_host.set_content(content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Replay-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        from app.gui.inspector.replay_inspector import ReplayInspector
        content = ReplayInspector(
            replay_id="(keine)",
            status="—",
            last_run="—",
            result_summary="—",
        )
        inspector_host.set_content(content, content_token=content_token)
