"""Workspace-Hinweise – wo Operations-Einstellungen im Produkt liegen."""

from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.shared import apply_settings_layout


class WorkspaceCategory(BaseSettingsCategory):
    """
    Kein separates Speicher-Schema „Workspace“ in den Settings.

    Orientierung, welche Bereiche wo konfiguriert werden.
    """

    def __init__(self, parent=None):
        super().__init__("settings_workspace", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        apply_settings_layout(layout)

        head = QLabel("Arbeitsbereiche (Operations)")
        head.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(head)

        body = QLabel(
            "Es gibt keine eigene Kategorie mit zusätzlichen Workspace-Schlüsseln in der "
            "Datenbank. Stattdessen gelten die globalen Einstellungen und die jeweiligen "
            "Workspaces:\n\n"
            "• Knowledge / RAG, Prompt Studio, Workflows, Agent Tasks, Chat: Sidebar → "
            "Operations (jeweiliger Workspace).\n"
            "• Modell- und Provider-Überblick: Control Center.\n"
            "• Persistente Schalter zu Daten und Prompts: Settings → Data bzw. verknüpfte "
            "Hilfetexte unter AI / Models und Privacy.\n\n"
            "Diese Seite dient der Orientierung, nicht der Speicherung neuer Werte."
        )
        body.setWordWrap(True)
        layout.addWidget(body)
        layout.addStretch()
