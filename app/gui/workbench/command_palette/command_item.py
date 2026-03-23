"""
Command definition type for the palette registry.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from app.gui.workbench.command_palette.command_context import WorkbenchCommandContext


class CommandCategory(str, Enum):
    NAVIGATION = "Navigation"
    WORKFLOWS = "Workflows"
    ACTIONS = "Actions"
    CREATE = "Create"
    SYSTEM = "System"


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    """
    Declarative command: label shown in palette, category, optional gating, handler.

    ``keywords`` extend fuzzy matching beyond the visible label (e.g. synonyms).
    """

    id: str
    label: str
    category: CommandCategory
    handler: Callable[[WorkbenchCommandContext], None]
    keywords: tuple[str, ...] = ()
    enabled_when: Callable[[WorkbenchCommandContext], bool] | None = None
