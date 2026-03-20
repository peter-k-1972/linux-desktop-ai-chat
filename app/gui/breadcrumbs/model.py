"""
BreadcrumbItem – Modell für ein Breadcrumb-Element.
"""

from dataclasses import dataclass
from enum import Enum


class BreadcrumbAction(Enum):
    """Aktion beim Klick auf ein Breadcrumb."""

    AREA = "area"  # Navigiere zu Hauptbereich (area_id)
    WORKSPACE = "workspace"  # Navigiere zu Workspace (area_id + workspace_id)
    DETAIL = "detail"  # Kein Navigationsziel (nur Anzeige)


@dataclass
class BreadcrumbItem:
    """
    Ein Breadcrumb-Element.

    Attributes:
        id: Eindeutige ID (area_id oder workspace_id)
        title: Anzeigename
        icon: Icon-Name für IconManager (optional)
        action: AREA | WORKSPACE | DETAIL
        area_id: Für WORKSPACE – übergeordneter Bereich
    """

    id: str
    title: str
    icon: str = ""
    action: BreadcrumbAction = BreadcrumbAction.AREA
    area_id: str = ""
