"""
QAGovernanceNav – Sekundäre Navigation innerhalb von QA & Governance.

Bereichsleiste: Test Inventory, Coverage Map, Gap Analysis, Incidents, Replay Lab.
Ruhig, analytisch, Governance-Anmutung.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QFrame
from PySide6.QtCore import Signal, Qt
from app.gui.icons import IconManager
from app.gui.icons.nav_mapping import QA_WORKSPACE_ICONS


class QAGovernanceNav(QFrame):
    """Sub-Navigation für QA-&-Governance-Bereiche."""

    workspace_selected = Signal(str)

    WORKSPACES = [
        ("qa_test_inventory", "Test Inventory"),
        ("qa_coverage_map", "Coverage Map"),
        ("qa_gap_analysis", "Gap Analysis"),
        ("qa_incidents", "Incidents"),
        ("qa_replay_lab", "Replay Lab"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("qaGovernanceNav")
        self.setMinimumWidth(180)
        self.setMaximumWidth(220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(4)

        title = QLabel("QA & Governance")
        title.setObjectName("domainNavTitle")
        layout.addWidget(title)

        subtitle = QLabel("Prüfen · Bewerten · Nachvollziehen")
        subtitle.setObjectName("domainNavSubtitle")
        layout.addWidget(subtitle)

        self._list = QListWidget()
        self._list.setObjectName("qaGovernanceNavList")
        self._list.setSpacing(4)
        self._list.itemClicked.connect(self._on_item_clicked)

        for area_id, title in self.WORKSPACES:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, area_id)
            icon_name = QA_WORKSPACE_ICONS.get(area_id)
            if icon_name:
                item.setIcon(IconManager.get(icon_name, size=18))
            self._list.addItem(item)

        layout.addWidget(self._list, 1)

    def _on_item_clicked(self, item: QListWidgetItem):
        area_id = item.data(Qt.ItemDataRole.UserRole)
        if area_id:
            self.workspace_selected.emit(area_id)

    def set_current(self, area_id: str) -> None:
        """Setzt den aktuell ausgewählten Eintrag."""
        for i in range(self._list.count()):
            if self._list.item(i).data(Qt.ItemDataRole.UserRole) == area_id:
                self._list.setCurrentRow(i)
                break
