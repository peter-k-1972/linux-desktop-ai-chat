"""
ProjectSwitcherButton – Button zum Wechseln des aktiven Projekts.

Zeigt [ Current Project Name ▼ ], öffnet bei Klick den ProjectSwitcherDialog.
Verwendet ProjectContextManager und project_context_changed Event.
"""

from typing import Optional

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.project_switcher.project_switcher_dialog import ProjectSwitcherDialog


class ProjectSwitcherButton(QPushButton):
    """
    Klickbarer Button mit aktuellem Projektnamen.

    - Zeigt [ Current Project Name ▼ ]
    - Öffnet ProjectSwitcherDialog bei Klick
    - Ruft ProjectContextManager.set_active_project(project_id) bei Auswahl
    - Aktualisiert Label bei project_context_changed
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectSwitcherButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)
        self._update_label("Kein Projekt")
        self.clicked.connect(self._on_clicked)
        self._connect_project_context()

    def _connect_project_context(self) -> None:
        """Abonniert project_context_changed und aktualisiert Label."""
        from app.gui.events.project_events import subscribe_project_events
        subscribe_project_events(self._on_project_context_changed)
        # Initial state from ProjectContextManager
        self._refresh_from_manager()

    def _refresh_from_manager(self) -> None:
        """Liest aktuellen Zustand aus ProjectContextManager."""
        from app.core.context.project_context_manager import get_project_context_manager
        mgr = get_project_context_manager()
        proj = mgr.get_active_project()
        pid = mgr.get_active_project_id()
        if proj and isinstance(proj, dict):
            self._update_label(proj.get("name", "Projekt"))
        else:
            self._update_label("Kein Projekt")

    def _on_project_context_changed(self, payload: dict) -> None:
        """Reagiert auf project_context_changed Event."""
        project_id = payload.get("project_id")
        if project_id is None:
            self._update_label("Kein Projekt")
            return
        from app.core.context.project_context_manager import get_project_context_manager
        proj = get_project_context_manager().get_active_project()
        if proj and isinstance(proj, dict):
            self._update_label(proj.get("name", "Projekt"))
        else:
            self._update_label("Projekt")

    def _update_label(self, text: str) -> None:
        icon = IconManager.get(IconRegistry.PROJECTS, size=16)
        self.setIcon(icon)
        self.setText(f"  {text}  ▼")
        self.setToolTip(f"Aktives Projekt: {text}\nKlicken zum Wechseln")

    def _on_clicked(self) -> None:
        dialog = ProjectSwitcherDialog(self)
        dialog.project_selected.connect(self._on_project_selected)
        dialog.exec()

    def _on_project_selected(self, project_id: Optional[int]) -> None:
        """Setzt das ausgewählte Projekt über ProjectContextManager."""
        from app.core.context.project_context_manager import get_project_context_manager
        get_project_context_manager().set_active_project(project_id)
        # Label wird über project_context_changed aktualisiert
