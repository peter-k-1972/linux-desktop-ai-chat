"""
ChatSidePanel – Rechte Seitenleiste mit Tabs (Modelle | Prompts).
Studio-Panel-Design, einklappbar, sauber vom Chat getrennt.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from app.resources.styles import get_theme_colors
from app.debug import get_debug_store

from app.gui.domains.settings.panels.model_settings_panel import ModelSettingsPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel import (
    PromptManagerPanel,
)
from app.gui.shared.panel_constants import _PROMPTS_PANEL_FIXED_WIDTH
from app.gui.domains.runtime_debug.panels.agent_debug_panel import AgentDebugPanel


def _side_panel_width():
    return _PROMPTS_PANEL_FIXED_WIDTH()


class ChatSidePanel(QWidget):
    """
    Rechte Seitenleiste: Tab 1 = Modell-Einstellungen, Tab 2 = Promptverwaltung.
    """

    settings_changed = Signal()
    prompt_apply_requested = Signal(object)
    prompt_as_system_requested = Signal(object)
    prompt_to_composer_requested = Signal(object)

    def __init__(
        self,
        settings,
        orchestrator=None,
        prompt_service=None,
        theme: str = "dark",
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.orchestrator = orchestrator
        self.prompt_service = prompt_service
        self.theme = theme
        self._collapsed = False
        self.init_ui()

    def init_ui(self):
        self.setObjectName("chatSidePanel")
        w = _side_panel_width()
        self.setMinimumWidth(w)
        self.setMaximumWidth(w)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("sidePanelTabs")

        # Tab 1: Modell-Einstellungen
        self.model_panel = ModelSettingsPanel(
            settings=self.settings,
            orchestrator=self.orchestrator,
            theme=self.theme,
        )
        self.model_panel.settings_changed.connect(self.settings_changed.emit)
        self.tabs.addTab(self.model_panel, "Modelle")

        # Tab 2: Promptverwaltung
        from app.prompts import PromptService
        self.prompt_panel = PromptManagerPanel(
            prompt_service=self.prompt_service or PromptService(),
            settings=self.settings,
            theme=self.theme,
        )
        self.prompt_panel.prompt_apply_requested.connect(self.prompt_apply_requested.emit)
        self.prompt_panel.prompt_as_system_requested.connect(self.prompt_as_system_requested.emit)
        self.prompt_panel.prompt_to_composer_requested.connect(self.prompt_to_composer_requested.emit)
        self.tabs.addTab(self.prompt_panel, "Prompts")

        # Tab 3: Agent Debug (nur wenn aktiviert)
        if getattr(self.settings, "debug_panel_enabled", True):
            self.debug_panel = AgentDebugPanel(
                store=get_debug_store(),
                theme=self.theme,
                enabled=True,
            )
            self.tabs.addTab(self.debug_panel, "Debug")
        else:
            self.debug_panel = None

        layout.addWidget(self.tabs)
        self._apply_theme()

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        bg = "#2d2d2d" if self.theme == "dark" else "#f5f5f5"
        border = colors.get("top_bar_border", "#505050")
        fg = colors.get("fg", "#e8e8e8")
        self.setStyleSheet(f"""
            QWidget#chatSidePanel {{
                background-color: {bg};
                border-left: 1px solid {border};
            }}
            QTabWidget#sidePanelTabs::pane {{
                border: none;
                background: transparent;
                top: -1px;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {fg};
                padding: 10px 20px;
                font-weight: 600;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                border-bottom: 2px solid {colors.get('accent', '#4a90d9')};
            }}
        """)

    def set_model_list(self, models: list):
        """Modelle an das ModelSettingsPanel übergeben."""
        self.model_panel.set_model_list(models)

    def update_provider_status(self, local_ok: bool, cloud_ok: bool, api_key: bool):
        """Provider-Status aktualisieren."""
        self.model_panel.update_provider_status(local_ok, cloud_ok, api_key)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self.model_panel.refresh_theme(theme)
        self.prompt_panel.refresh_theme(theme)
        if self.debug_panel:
            self.debug_panel.set_theme(theme)
        self._apply_theme()
