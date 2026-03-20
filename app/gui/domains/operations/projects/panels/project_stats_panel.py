"""
ProjectStatsPanel – Kennzahlen-Karte für den Project Overview.

Chats, Quellen, Prompts.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class _StatCard(QFrame):
    """Einzelne Kennzahl-Karte."""

    def __init__(self, label: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("projectStatCard")
        self.setStyleSheet("""
            #projectStatCard {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 14px 16px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        icon = IconManager.get(icon_name, size=20)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(20, 20))
        layout.addWidget(icon_label)
        inner = QVBoxLayout()
        inner.setSpacing(2)
        self._value_label = QLabel("0")
        self._value_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #f1f1f4;")
        inner.addWidget(self._value_label)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        inner.addWidget(lbl)
        layout.addLayout(inner, 1)

    def set_value(self, value: int) -> None:
        self._value_label.setText(str(value))


class ProjectStatsPanel(QFrame):
    """Panel mit Projekt-Kennzahlen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectStatsPanel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._chat_card = _StatCard("Chats", IconRegistry.CHAT)
        self._source_card = _StatCard("Quellen", IconRegistry.KNOWLEDGE)
        self._prompt_card = _StatCard("Prompts", IconRegistry.PROMPT_STUDIO)

        layout.addWidget(self._chat_card, 1)
        layout.addWidget(self._source_card, 1)
        layout.addWidget(self._prompt_card, 1)

        self.setStyleSheet("#projectStatsPanel { background: transparent; }")

    def set_stats(self, chat_count: int, source_count: int, prompt_count: int) -> None:
        """Aktualisiert die Kennzahlen."""
        self._chat_card.set_value(chat_count)
        self._source_card.set_value(source_count)
        self._prompt_card.set_value(prompt_count)
