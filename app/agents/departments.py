"""
Departments – Abteilungsstruktur für die Agentenorganisation.

Strukturierte Organisation mit 6 Hauptabteilungen.
Erweiterbar für ComfyUI, Multimedia-Pipelines, Tool-Execution, Delegation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Department(str, Enum):
    """Standard-Abteilungen der Agentenorganisation."""

    PLANNING = "planning"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    MEDIA = "media"
    AUTOMATION = "automation"
    SYSTEM = "system"


@dataclass
class DepartmentInfo:
    """Metadaten einer Abteilung."""

    id: str
    name: str
    description: str = ""
    color: Optional[str] = None  # Hex oder CSS-Farbe für Badge
    badge: Optional[str] = None  # Kurzes Badge-Label


# Anzeigenamen und Beschreibungen
DEPARTMENT_INFOS: Dict[Department, DepartmentInfo] = {
    Department.PLANNING: DepartmentInfo(
        id="planning",
        name="Planning",
        description="Planung, Projektmanagement, Strategie, Task-Zerlegung",
        color="#0ea5e9",
        badge="Planning",
    ),
    Department.RESEARCH: DepartmentInfo(
        id="research",
        name="Research",
        description="Recherche, Analyse, Faktenprüfung, Wissenssynthese",
        color="#06b6d4",
        badge="Research",
    ),
    Department.DEVELOPMENT: DepartmentInfo(
        id="development",
        name="Development",
        description="Programmierung, Code, Debugging, Dokumentation, Skripte",
        color="#10b981",
        badge="Development",
    ),
    Department.MEDIA: DepartmentInfo(
        id="media",
        name="Media",
        description="Multimedia: Bild, Video, Audio, Musik, Voice, Workflows",
        color="#f59e0b",
        badge="Media",
    ),
    Department.AUTOMATION: DepartmentInfo(
        id="automation",
        name="Automation",
        description="Automatisierung, Tools, Scheduler, Workflow-Orchestrierung",
        color="#84cc16",
        badge="Automation",
    ),
    Department.SYSTEM: DepartmentInfo(
        id="system",
        name="System",
        description="Systemadministration, Updates, Recovery, Monitoring",
        color="#475569",
        badge="System",
    ),
}


def get_department_info(dept: Department) -> DepartmentInfo:
    """Liefert die Metadaten einer Abteilung."""
    return DEPARTMENT_INFOS.get(dept, DepartmentInfo(id=dept.value, name=dept.value))


def get_department_display_name(dept: Department) -> str:
    """Liefert den Anzeigenamen einer Abteilung."""
    info = get_department_info(dept)
    return info.name


def all_departments() -> List[Department]:
    """Liefert alle definierten Abteilungen."""
    return list(Department)


def department_from_str(value: str) -> Optional[Department]:
    """Parst einen String zu einer Department-Enum."""
    if not value:
        return None
    v = value.strip().lower()
    for d in Department:
        if d.value == v:
            return d
    # Legacy-Aliase für Migration (alte DB-Einträge)
    _legacy_map = {
        "general": Department.PLANNING,
        "code": Department.DEVELOPMENT,
        "knowledge": Department.RESEARCH,
        "image": Department.MEDIA,
        "video": Department.MEDIA,
        "audio": Department.MEDIA,
        "music": Department.MEDIA,
        "workflow": Department.AUTOMATION,
    }
    return _legacy_map.get(v)
