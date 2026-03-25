"""
BreadcrumbManager – zentrale Verwaltung des Breadcrumb-Pfads.

Pfad-Segmente für Bereiche/Workspaces: nur wenn die Nav-Entry-ID in der aktiven
Feature-Menge erlaubt ist (``nav_context``), sonst fail-soft neutraler Fallback.
"""

from PySide6.QtCore import QObject, Signal

from app.gui.breadcrumbs.model import BreadcrumbItem, BreadcrumbAction
from app.gui.navigation.nav_areas import NavArea
from app.gui.navigation.nav_context import (
    is_area_visible_in_nav,
    is_nav_entry_allowed,
    neutral_breadcrumb_fallback_title,
)
from app.gui.icons.nav_mapping import (
    NAV_AREA_ICONS,
    get_workspace_icon,
)
from app.core.navigation.navigation_registry import get_all_entries


def _build_workspace_info() -> dict[str, tuple[str, str]]:
    """workspace_id -> (area_id, title) from navigation registry."""
    result: dict[str, tuple[str, str]] = {}
    for entry in get_all_entries().values():
        if entry.workspace:
            result[entry.id] = (entry.area, entry.title)
    return result


WORKSPACE_INFO: dict[str, tuple[str, str]] = _build_workspace_info()

AREA_TITLES: dict[str, str] = {a: t for a, t in NavArea.all_areas()}


class BreadcrumbManager(QObject):
    """
    Zentraler Manager für Breadcrumbs.
    - Verwaltet aktuellen Pfad
    - Emittiert path_changed
    - Hilfsmethoden für Workspaces
    """

    path_changed = Signal(list)  # list[BreadcrumbItem]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path: list[BreadcrumbItem] = []

    def _set_neutral_fallback(self) -> None:
        """Kein gültiger Nav-Kontext (z. B. inaktives Feature) — ein neutraler Krümel."""
        self.set_path([
            BreadcrumbItem(
                id="_nav_fallback",
                title=neutral_breadcrumb_fallback_title(),
                icon="",
                action=BreadcrumbAction.DETAIL,
            ),
        ])

    def set_path(self, items: list[BreadcrumbItem]) -> None:
        """Setzt den kompletten Pfad."""
        self._path = list(items)
        self.path_changed.emit(self._path)

    def set_area(self, area_id: str) -> None:
        """Setzt Breadcrumb auf Hauptbereich. Bei COMMAND_CENTER + Projekt: nur Projektname."""
        if not is_area_visible_in_nav(area_id):
            self._set_neutral_fallback()
            return
        items: list[BreadcrumbItem] = []
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.gui.navigation.nav_areas import NavArea
            mgr = get_project_context_manager()
            proj = mgr.get_active_project()
            if (
                area_id == NavArea.COMMAND_CENTER
                and proj
                and isinstance(proj, dict)
                and is_nav_entry_allowed("command_center")
            ):
                proj_name = proj.get("name", "Projekt")
                items.append(BreadcrumbItem(
                    id=NavArea.COMMAND_CENTER,
                    title=proj_name,
                    icon=NAV_AREA_ICONS.get(NavArea.COMMAND_CENTER, ""),
                    action=BreadcrumbAction.AREA,
                    area_id=NavArea.COMMAND_CENTER,
                ))
                self.set_path(items)
                return
        except Exception:
            pass
        title = "Aktives Projekt" if area_id == NavArea.COMMAND_CENTER else AREA_TITLES.get(area_id, area_id)
        icon = NAV_AREA_ICONS.get(area_id, "")
        items.append(BreadcrumbItem(id=area_id, title=title, icon=icon, action=BreadcrumbAction.AREA))
        self.set_path(items)

    def set_workspace(self, area_id: str, workspace_id: str) -> None:
        """Setzt Breadcrumb auf Project / Workspace (Format: Projekt / Workspace / Detail)."""
        if not is_area_visible_in_nav(area_id):
            self._set_neutral_fallback()
            return
        if not is_nav_entry_allowed(workspace_id):
            self.set_area(area_id)
            return
        items: list[BreadcrumbItem] = []
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.gui.navigation.nav_areas import NavArea
            mgr = get_project_context_manager()
            proj = mgr.get_active_project()
            if (
                proj
                and isinstance(proj, dict)
                and is_nav_entry_allowed("command_center")
            ):
                proj_name = proj.get("name", "Projekt")
                items.append(BreadcrumbItem(
                    id=NavArea.COMMAND_CENTER,
                    title=proj_name,
                    icon=NAV_AREA_ICONS.get(NavArea.COMMAND_CENTER, ""),
                    action=BreadcrumbAction.AREA,
                    area_id=NavArea.COMMAND_CENTER,
                ))
        except Exception:
            pass
        info = WORKSPACE_INFO.get(workspace_id)
        ws_title = info[1] if info else workspace_id
        ws_icon = get_workspace_icon(workspace_id) or ""
        items.append(BreadcrumbItem(
            id=workspace_id,
            title=ws_title,
            icon=ws_icon,
            action=BreadcrumbAction.WORKSPACE,
            area_id=area_id,
        ))
        self.set_path(items)

    def set_path_with_detail(self, area_id: str, workspace_id: str, detail_title: str) -> None:
        """Setzt Breadcrumb auf Project / Workspace / Detail (z.B. AI Research Lab / Chat / Session 3)."""
        if not is_area_visible_in_nav(area_id):
            self._set_neutral_fallback()
            return
        if not is_nav_entry_allowed(workspace_id):
            self.set_area(area_id)
            return
        items: list[BreadcrumbItem] = []
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.gui.navigation.nav_areas import NavArea
            mgr = get_project_context_manager()
            proj = mgr.get_active_project()
            if (
                proj
                and isinstance(proj, dict)
                and is_nav_entry_allowed("command_center")
            ):
                proj_name = proj.get("name", "Projekt")
                items.append(BreadcrumbItem(
                    id=NavArea.COMMAND_CENTER,
                    title=proj_name,
                    icon=NAV_AREA_ICONS.get(NavArea.COMMAND_CENTER, ""),
                    action=BreadcrumbAction.AREA,
                    area_id=NavArea.COMMAND_CENTER,
                ))
        except Exception:
            pass
        info = WORKSPACE_INFO.get(workspace_id)
        ws_title = info[1] if info else workspace_id
        ws_icon = get_workspace_icon(workspace_id) or ""
        items.append(BreadcrumbItem(
            id=workspace_id,
            title=ws_title,
            icon=ws_icon,
            action=BreadcrumbAction.WORKSPACE,
            area_id=area_id,
        ))
        items.append(BreadcrumbItem(id="", title=detail_title, icon="", action=BreadcrumbAction.DETAIL))
        self.set_path(items)

    def get_path(self) -> list[BreadcrumbItem]:
        """Liefert den aktuellen Pfad."""
        return list(self._path)


def get_breadcrumb_manager() -> BreadcrumbManager:
    """Singleton-Zugriff. Muss nach App-Start mit Instanz initialisiert werden."""
    return _manager


_manager: BreadcrumbManager | None = None


def set_breadcrumb_manager(manager: BreadcrumbManager) -> None:
    """Setzt die globale BreadcrumbManager-Instanz."""
    global _manager
    _manager = manager
