"""Project settings – read-only Übersicht zum aktuell aktiven Projekt."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.shared import apply_settings_layout

if TYPE_CHECKING:
    from app.ui_application.ports.settings_project_overview_port import SettingsProjectOverviewPort


class ProjectCategory(BaseSettingsCategory):
    """Zeigt Metadaten des aktiven Projekts; Bearbeitung erfolgt unter Operations → Projekte."""

    def __init__(self, parent=None, *, project_overview_port: SettingsProjectOverviewPort | None = None):
        self._project_overview_port = project_overview_port
        self._project_presenter = None
        super().__init__("settings_project", parent)
        self._setup_ui()
        self._wire_project_overview()

    def _wire_project_overview(self) -> None:
        from app.gui.domains.settings.settings_project_overview_sink import SettingsProjectOverviewSink
        from app.ui_application.adapters.service_settings_project_overview_adapter import (
            ServiceSettingsProjectOverviewAdapter,
        )
        from app.ui_application.presenters.settings_project_overview_presenter import (
            SettingsProjectOverviewPresenter,
        )

        port = self._project_overview_port or ServiceSettingsProjectOverviewAdapter()
        sink = SettingsProjectOverviewSink(self._body)
        self._project_presenter = SettingsProjectOverviewPresenter(sink, port)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        apply_settings_layout(layout)

        head = QLabel("Aktives Projekt")
        head.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(head)

        self._body = QLabel()
        self._body.setWordWrap(True)
        self._body.setObjectName("projectSettingsBody")
        layout.addWidget(self._body)

        foot = QLabel(
            "Projekt umbenennen, anlegen oder löschen: Operations → Projekte "
            "oder Projektwahl in der Kopfzeile."
        )
        foot.setWordWrap(True)
        foot.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(foot)
        layout.addStretch()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if self._project_presenter is None:
            return
        from app.ui_contracts.workspaces.settings_project_overview import (
            RefreshSettingsActiveProjectCommand,
        )

        self._project_presenter.handle_command(RefreshSettingsActiveProjectCommand())
