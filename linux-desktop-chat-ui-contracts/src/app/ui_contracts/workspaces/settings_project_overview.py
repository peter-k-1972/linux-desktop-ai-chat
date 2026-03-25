"""
Settings — aktives Projekt (Read-only Übersicht), Qt-frei.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

SettingsActiveProjectMode = Literal["no_active", "not_found", "ok", "error"]


@dataclass(frozen=True, slots=True)
class ActiveProjectSummaryDto:
    """Kompakte Projektmetadaten für die Anzeige."""

    project_id: int
    name: str
    status: str
    description_display: str
    chat_count: int
    default_context_policy_display: str
    updated_at_display: str


@dataclass(frozen=True, slots=True)
class SettingsActiveProjectViewState:
    """Ergebnis des Leseports (Adapter fängt Exceptions → mode=error)."""

    mode: SettingsActiveProjectMode
    error_message: str | None = None
    summary: ActiveProjectSummaryDto | None = None


@dataclass(frozen=True, slots=True)
class SettingsProjectCategoryBodyState:
    """Text für das Body-QLabel."""

    body_text: str


@dataclass(frozen=True, slots=True)
class RefreshSettingsActiveProjectCommand:
    """Kategorie sichtbar geworden / manuell aktualisieren."""


SettingsProjectOverviewCommand = Union[RefreshSettingsActiveProjectCommand]
