"""
ChatHeaderWidget – Kompakte Topbar.
Modell, Modus, Routing, Cloud, Eskalation – logisch gruppiert.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt

from app.core.models.roles import ModelRole, get_role_display_name, all_roles
from app.resources.styles import get_theme_colors


class ChatHeaderWidget(QWidget):
    """Kompakte Header-Zone mit Modell- und Chat-Steuerung."""

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        self.setObjectName("chatHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)

        colors = get_theme_colors(self.theme)
        self._colors = colors

        # Agent-Auswahl (Persona)
        self.agent_combo = QComboBox()
        self.agent_combo.setObjectName("headerAgentCombo")
        self.agent_combo.setMinimumWidth(140)
        self.agent_combo.setPlaceholderText("Agent wählen…")
        self.agent_combo.setToolTip("Aktiver Agent / Persona für diesen Chat")
        layout.addWidget(self.agent_combo)

        # Separator
        sep_agent = QFrame()
        sep_agent.setFrameShape(QFrame.VLine)
        sep_agent.setStyleSheet(f"color: {colors['top_bar_border']};")
        sep_agent.setFixedWidth(1)
        layout.addWidget(sep_agent)

        # Gruppe 1: Modell + Rolle
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("headerModelCombo")
        self.model_combo.setMinimumWidth(180)
        self.model_combo.setPlaceholderText("Modell wählen…")
        layout.addWidget(self.model_combo)

        self.role_combo = QComboBox()
        self.role_combo.setObjectName("headerRoleCombo")
        self.role_combo.setMinimumWidth(90)
        self.role_combo.setToolTip("Modus: Rolle für Modellauswahl")
        for role in all_roles():
            self.role_combo.addItem(get_role_display_name(role), role)
        layout.addWidget(self.role_combo)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {colors['top_bar_border']};")
        sep.setFixedWidth(1)
        layout.addWidget(sep)

        # Gruppe 2: Routing & Cloud
        self.auto_routing_check = QCheckBox("Auto")
        self.auto_routing_check.setObjectName("headerAutoRouting")
        self.auto_routing_check.setToolTip("Automatische Modellauswahl nach Prompt-Inhalt")
        layout.addWidget(self.auto_routing_check)

        self.cloud_check = QCheckBox("Cloud")
        self.cloud_check.setObjectName("headerCloud")
        self.cloud_check.setToolTip("Cloud-Eskalation erlauben (OLLAMA_API_KEY)")
        layout.addWidget(self.cloud_check)

        self.overkill_btn = QPushButton("Eskalieren")
        self.overkill_btn.setObjectName("overkillButton")
        self.overkill_btn.setToolTip("Mit stärkerem Modell erneut versuchen")
        self.overkill_btn.setCheckable(True)
        layout.addWidget(self.overkill_btn)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet(f"color: {colors['top_bar_border']};")
        sep2.setFixedWidth(1)
        layout.addWidget(sep2)

        # Gruppe 3: Thinking & Websuche
        self.think_mode_combo = QComboBox()
        self.think_mode_combo.setObjectName("headerThinkMode")
        self.think_mode_combo.setMinimumWidth(100)
        self.think_mode_combo.setToolTip("Thinking-Modus")
        self.think_mode_combo.addItems(["auto", "off", "low", "medium", "high"])
        layout.addWidget(self.think_mode_combo)

        self.web_search_check = QCheckBox("Websuche")
        self.web_search_check.setObjectName("headerWebSearch")
        self.web_search_check.setToolTip(
            "Aktuelle Websuchergebnisse als Kontext nutzen"
        )
        layout.addWidget(self.web_search_check)

        # RAG Toggle
        self.rag_check = QCheckBox("RAG")
        self.rag_check.setObjectName("headerRAG")
        self.rag_check.setToolTip(
            "Retrieval Augmented Generation: Kontext aus indexierten Dokumenten nutzen"
        )
        layout.addWidget(self.rag_check)

        # Self-Improving Toggle
        self.self_improving_check = QCheckBox("Self-Improve")
        self.self_improving_check.setObjectName("headerSelfImproving")
        self.self_improving_check.setToolTip(
            "Wissen aus Antworten extrahieren und in den Knowledge Store aufnehmen"
        )
        layout.addWidget(self.self_improving_check)

        layout.addStretch()

        self._apply_theme_styles()

    def _apply_theme_styles(self):
        c = self._colors
        self.setStyleSheet(
            f"""
            QWidget#chatHeader {{
                background-color: {c['top_bar_bg']};
                border-bottom: 1px solid {c['top_bar_border']};
            }}
            QCheckBox#headerAutoRouting,
            QCheckBox#headerCloud,
            QCheckBox#headerWebSearch,
            QCheckBox#headerRAG,
            QCheckBox#headerSelfImproving {{
                color: {c['muted']};
                font-size: 12px;
                font-weight: 500;
            }}
        """
        )

    def refresh_theme(self, theme: str):
        """Theme-Update nach Einstellungsänderung."""
        self.theme = theme
        self._colors = get_theme_colors(theme)
        self._apply_theme_styles()
