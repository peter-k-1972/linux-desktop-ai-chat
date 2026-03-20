"""
SidebarConfig – Navigationsstruktur nach Arbeitskontext.

Uses app.core.navigation.navigation_registry as single source of truth.
Sections: PROJECT, WORKSPACE, SYSTEM, OBSERVABILITY, QUALITY, SETTINGS.
"""

from dataclasses import dataclass
from typing import Optional

from app.core.navigation.navigation_registry import get_all_entries, get_sidebar_sections as get_registry_sections
from app.gui.navigation.nav_areas import NavArea


@dataclass
class NavItem:
    """Ein Navigations-Eintrag (compat with existing sidebar)."""

    area_id: str
    workspace_id: Optional[str]
    title: str
    icon: str
    tooltip: Optional[str] = None

    @property
    def nav_key(self) -> str:
        """Eindeutiger Schlüssel für Auswahl (workspace_id oder area_id)."""
        return self.workspace_id or self.area_id


@dataclass
class NavSection:
    """Eine Sektion mit Header und Items (compat with existing sidebar)."""

    id: str
    title: str
    items: list[NavItem]
    default_expanded: bool = True


def get_sidebar_sections() -> list[NavSection]:
    """Liefert die Sidebar-Sektionen aus dem Navigation Registry."""
    entries = get_all_entries()
    sections_def = get_registry_sections()

    result = []
    for sec_def in sections_def:
        items = []
        for eid in sec_def.entry_ids:
            entry = entries.get(eid)
            if not entry:
                continue
            items.append(NavItem(
                area_id=entry.area,
                workspace_id=entry.workspace,
                title=entry.title,
                icon=entry.icon or "",
                tooltip=entry.description or None,
            ))
        result.append(NavSection(
            id=sec_def.id,
            title=sec_def.title,
            items=items,
            default_expanded=sec_def.default_expanded,
        ))
    return result
