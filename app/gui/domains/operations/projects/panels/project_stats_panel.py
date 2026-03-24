"""
ProjectStatsPanel – Archiv-Übersicht: Workflows, Chats, Agenten, Dateien.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared.layout_constants import WIDGET_SPACING, apply_card_inner_layout
from app.gui.theme import design_metrics as dm


class _StatCard(QFrame):
    """Einzelne Kennzahl-Karte."""

    def __init__(self, label: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("projectStatCard")
        self.setStyleSheet(
            f"""
            #projectStatCard {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: {dm.RADIUS_LG_PX}px;
                padding: 0px;
            }}
            """
        )
        layout = QHBoxLayout(self)
        apply_card_inner_layout(layout)
        layout.setSpacing(WIDGET_SPACING)
        icon = IconManager.get(icon_name, size=dm.ICON_MD_PX)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(dm.ICON_MD_PX, dm.ICON_MD_PX))
        layout.addWidget(icon_label)
        inner = QVBoxLayout()
        inner.setSpacing(dm.SPACE_2XS_PX)
        self._value_label = QLabel("0")
        self._value_label.setStyleSheet(
            f"font-size: {dm.TEXT_XL_PX}px; font-weight: 600; color: #f1f1f4;"
        )
        inner.addWidget(self._value_label)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size: {dm.TEXT_XS_PX}px; color: #64748b;"
        )
        inner.addWidget(lbl)
        layout.addLayout(inner, 1)

    def set_value(self, value: int) -> None:
        self._value_label.setText(str(value))


class ProjectStatsPanel(QFrame):
    """Strukturierte Übersicht der Archiv-Inhalte (vier Bereiche)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectStatsPanel")
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(WIDGET_SPACING)

        cap = QLabel("Archiv-Inhalt")
        cap.setStyleSheet(
            f"font-weight: 600; font-size: {dm.TEXT_SM_PX}px; color: #94a3b8; letter-spacing: 0.02em;"
        )
        outer.addWidget(cap)

        row = QHBoxLayout()
        row.setSpacing(WIDGET_SPACING)

        self._workflow_card = _StatCard("Workflows", IconRegistry.SYSTEM_GRAPH)
        self._chat_card = _StatCard("Chats", IconRegistry.CHAT)
        self._agent_card = _StatCard("Agenten", IconRegistry.AGENTS)
        self._file_card = _StatCard("Dateien", IconRegistry.DATA_STORES)

        row.addWidget(self._workflow_card, 1)
        row.addWidget(self._chat_card, 1)
        row.addWidget(self._agent_card, 1)
        row.addWidget(self._file_card, 1)
        outer.addLayout(row)

        self.setStyleSheet("#projectStatsPanel { background: transparent; }")

    def set_stats(
        self,
        workflow_count: int,
        chat_count: int,
        agent_count: int,
        file_link_count: int,
    ) -> None:
        """Aktualisiert die Kennzahlen."""
        self._workflow_card.set_value(workflow_count)
        self._chat_card.set_value(chat_count)
        self._agent_card.set_value(agent_count)
        self._file_card.set_value(file_link_count)
