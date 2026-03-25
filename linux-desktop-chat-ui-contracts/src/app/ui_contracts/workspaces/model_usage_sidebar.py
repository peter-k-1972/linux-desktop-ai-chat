"""
Model usage sidebar hint (Qt-frei).

Kurzer Hinweistext aus Model-Usage-GUI; Anzeige über Presenter → Port → Adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True, slots=True)
class ModelUsageSidebarHintState:
    """Einzeiler für die Sidebar (leer = ausblenden)."""

    hint_text: str


@dataclass(frozen=True, slots=True)
class RefreshModelUsageSidebarHintCommand:
    """Hinweis neu vom Port laden."""


ModelUsageSidebarCommand = Union[RefreshModelUsageSidebarHintCommand]

__all__ = [
    "ModelUsageSidebarCommand",
    "ModelUsageSidebarHintState",
    "RefreshModelUsageSidebarHintCommand",
]
