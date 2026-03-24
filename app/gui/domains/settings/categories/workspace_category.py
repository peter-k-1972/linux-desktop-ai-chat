"""Workspace-Hinweise – wo Operations-Einstellungen im Produkt liegen."""

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.shared import apply_settings_layout
from app.workspace_presets.preset_activation import get_active_workspace_preset


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

        preset_block = self._build_workspace_preset_readonly_section()
        layout.addWidget(preset_block)

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

    def _build_workspace_preset_readonly_section(self) -> QLabel:
        """Slice 5: aktiver Arbeitsmodus nur Anzeige (keine Bearbeitung in Settings)."""
        try:
            p = get_active_workspace_preset()
            tags = ", ".join(html.escape(t) for t in p.tags) if p.tags else "—"
            text = (
                "<p style='font-weight:600;margin-bottom:4px;'>Aktiver Workspace-Preset (Arbeitsmodus)</p>"
                f"<p style='margin:0 0 8px 0;'><b>{html.escape(p.display_name)}</b> "
                f"<code>({html.escape(p.preset_id)})</code><br/>"
                f"<span style='color:#555;'>{html.escape(p.description)}</span><br/>"
                f"<small>Tags: {tags}</small></p>"
                "<p style='margin:0;color:#666;font-size:12px;'>Presets werden im "
                "System-Overlay verwaltet, nicht hier.</p>"
            )
        except Exception:
            text = (
                "<p style='font-weight:600;'>Aktiver Workspace-Preset</p>"
                "<p style='color:#666;'>Zurzeit nicht verfügbar.</p>"
            )
        box = QLabel(text)
        box.setWordWrap(True)
        box.setTextFormat(Qt.RichText)
        box.setStyleSheet(
            "background:#f5f5f5;border:1px solid #e0e0e0;border-radius:4px;padding:10px;"
        )
        return box
