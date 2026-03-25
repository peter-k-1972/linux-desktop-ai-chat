"""
SidebarConfig – Navigationsstruktur nach Arbeitskontext.

Uses app.core.navigation.navigation_registry as single source of truth.
Sections: PROJECT, WORKSPACE, SYSTEM, OBSERVABILITY, QUALITY, SETTINGS.

Wenn eine globale FeatureRegistry gesetzt ist, werden Einträge nach
``collect_active_navigation_entry_ids`` gefiltert (Edition → aktive Features).
Ohne Registry: unverändert alle Registry-Einträge (Legacy/Tests).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from app.core.navigation.navigation_registry import get_all_entries, get_sidebar_sections as get_registry_sections

if TYPE_CHECKING:
    from app.features import FeatureRegistry


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


def get_sidebar_sections(*, feature_registry: Optional["FeatureRegistry"] = None) -> list[NavSection]:
    """Liefert die Sidebar-Sektionen aus dem Navigation Registry, optional feature-gefiltert."""
    from app.features import (
        collect_active_navigation_entry_ids,
        get_feature_registry,
    )
    from app.gui.navigation.nav_context import allowed_navigation_entry_ids

    if feature_registry is not None:
        allowed: Optional[frozenset[str]] = collect_active_navigation_entry_ids(feature_registry)
    else:
        allowed = allowed_navigation_entry_ids()

    entries = get_all_entries()
    sections_def = get_registry_sections()

    result = []
    for sec_def in sections_def:
        items = []
        for eid in sec_def.entry_ids:
            if allowed is not None and eid not in allowed:
                continue
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
        if not items:
            continue
        result.append(NavSection(
            id=sec_def.id,
            title=sec_def.title,
            items=items,
            default_expanded=sec_def.default_expanded,
        ))
    return result
