"""
Execution context passed into command handlers and enable predicates.

Built fresh when the palette opens so handlers always see current docks and canvas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.gui.workbench.canvas.canvas_base import WorkbenchCanvasBase
    from app.gui.workbench.canvas.canvas_router import CanvasRouter
    from app.gui.workbench.focus.active_object import ActiveObject
    from app.gui.workbench.main_workbench import MainWorkbench


@dataclass(slots=True)
class WorkbenchCommandContext:
    """Snapshot of UI state for routing palette commands."""

    window: MainWorkbench
    active_canvas: WorkbenchCanvasBase | None
    active_object: ActiveObject

    @property
    def canvas_router(self) -> CanvasRouter:
        return self.window.canvas_router
