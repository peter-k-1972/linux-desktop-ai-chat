"""
Agents Panels – Agent Registry, Profiles, Skills, Model Assignment.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, Signal


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class AgentRegistryPanel(QFrame):
    """Agent Registry – Verwaltungssicht auf Agenten. D27: Emits agent_selected on row selection."""

    agent_selected = Signal(str, str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentRegistryPanel")
        self.setMinimumHeight(200)
        self._table: QTableWidget | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Registry")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        demo_label = QLabel("Vorschau (Agenten bei Verbindung)")
        demo_label.setStyleSheet("font-size: 11px; color: #94a3b8; margin-bottom: 4px;")
        layout.addWidget(demo_label)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Agent", "Role", "Model", "Tools", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setRowCount(3)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        dummy_data = [
            ("Research Agent", "Research", "llama3.2", "5", "Active"),
            ("Code Agent", "Coding", "codellama", "8", "Active"),
            ("General Assistant", "General", "mistral:7b", "3", "Idle"),
        ]
        for row, (agent, role, model, tools, status) in enumerate(dummy_data):
            self._table.setItem(row, 0, QTableWidgetItem(agent))
            self._table.setItem(row, 1, QTableWidgetItem(role))
            self._table.setItem(row, 2, QTableWidgetItem(model))
            self._table.setItem(row, 3, QTableWidgetItem(tools))
            self._table.setItem(row, 4, QTableWidgetItem(status))

        layout.addWidget(self._table)

    def _on_selection_changed(self) -> None:
        """Emits agent_selected with row data when user selects a row."""
        if not self._table:
            return
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self.agent_selected.emit("(keine Auswahl)", "—", "—", "—", "—")
            return
        row = rows[0].row()
        agent = self._table.item(row, 0).text() if self._table.item(row, 0) else "—"
        role = self._table.item(row, 1).text() if self._table.item(row, 1) else "—"
        model = self._table.item(row, 2).text() if self._table.item(row, 2) else "—"
        tools = self._table.item(row, 3).text() if self._table.item(row, 3) else "—"
        status = self._table.item(row, 4).text() if self._table.item(row, 4) else "—"
        self.agent_selected.emit(agent, role, model, tools, status)


class AgentSummaryPanel(QFrame):
    """Agent Profiles / Skills / Model Assignment / Status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentSummaryPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Configuration Summary")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        for label, value in [
            ("Selected Agent", "Research Agent"),
            ("Skills / Capabilities", "Web Search, File Read, Code Exec"),
            ("Model Assignment", "llama3.2"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("color: #64748b; font-size: 12px; min-width: 140px;")
            val = QLabel(value)
            val.setStyleSheet("color: #1e293b; font-size: 12px;")
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)
