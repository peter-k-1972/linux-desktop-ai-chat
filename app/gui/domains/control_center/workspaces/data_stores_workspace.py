"""
DataStoresWorkspace – SQLite, RAG/Chroma, Dateisystem (gemessene Zustände).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from app.gui.domains.control_center.workspaces.base_management_workspace import BaseManagementWorkspace
from app.gui.domains.control_center.panels.data_stores_panels import (
    DataStoreOverviewPanel,
    DataStoreHealthPanel,
)
from app.services.infrastructure_snapshot import build_data_store_rows


class DataStoresWorkspace(BaseManagementWorkspace):
    """Workspace: Data-Store-Status aus Infrastruktur-Snapshots."""

    def __init__(self, parent=None):
        super().__init__("cc_data_stores", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(DataStoreOverviewPanel(self))
        content_layout.addWidget(DataStoreHealthPanel(self))

        detail = QFrame()
        detail.setObjectName("dataStoreDetailArea")
        detail.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Hinweis")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        dl.addWidget(title)
        label = QLabel(
            "Detaillierte Nutzungsmetriken (z. B. Session-Anzahl, Vektoranzahl) "
            "erscheinen hier nicht aggregiert — siehe Tabelle und QA-/Metrik-Ansichten."
        )
        label.setWordWrap(True)
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        dl.addWidget(label)
        content_layout.addWidget(detail)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt DataStore-spezifischen Inspector. D9: content_token optional."""
        self._inspector_host = inspector_host
        from app.gui.inspector.data_store_inspector import DataStoreInspector

        rows = build_data_store_rows()
        if rows:
            r = rows[0]
            content = DataStoreInspector(
                store_type=f"{r.store} ({r.store_type})",
                state=r.state,
                usage=r.connection,
                health=r.state,
            )
        else:
            content = DataStoreInspector()
        inspector_host.set_content(content, content_token=content_token)
