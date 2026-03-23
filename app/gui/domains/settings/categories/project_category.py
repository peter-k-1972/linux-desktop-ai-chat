"""Project settings – read-only Übersicht zum aktuell aktiven Projekt."""

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout

from app.gui.domains.settings.categories.base_category import BaseSettingsCategory
from app.gui.shared import apply_settings_layout


class ProjectCategory(BaseSettingsCategory):
    """Zeigt Metadaten des aktiven Projekts; Bearbeitung erfolgt unter Operations → Projekte."""

    def __init__(self, parent=None):
        super().__init__("settings_project", parent)
        self._setup_ui()

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
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.services.project_service import get_project_service

            pid = get_project_context_manager().get_active_project_id()
            if pid is None:
                self._body.setText(
                    "Es ist kein Projekt aktiv. Wählen Sie ein Projekt in der Kopfzeile "
                    "oder unter Operations → Projekte."
                )
                return
            svc = get_project_service()
            proj = svc.get_project(pid)
            if not proj:
                self._body.setText("Aktives Projekt konnte nicht geladen werden.")
                return
            n_chats = svc.count_chats_of_project(pid)
            desc = (proj.get("description") or "").strip() or "—"
            pol = proj.get("default_context_policy")
            pol_disp = "—"
            if pol is not None and str(pol).strip():
                s = str(pol).strip()
                pol_disp = s if len(s) <= 240 else s[:237] + "…"
            self._body.setText(
                f"{proj.get('name', '?')} (ID {pid})\n\n"
                f"Status: {proj.get('status', '—')}\n"
                f"Beschreibung: {desc}\n"
                f"Zugeordnete Chats: {n_chats}\n"
                f"Standard-Kontextpolicy (gespeichert): {pol_disp}\n"
                f"Aktualisiert: {proj.get('updated_at', '—')}"
            )
        except Exception as exc:
            self._body.setText(f"Projektdaten konnten nicht geladen werden: {exc}")
