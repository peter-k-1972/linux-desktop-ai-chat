"""
Central focus coordinator: active object follows the canvas tab and broadcasts updates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from app.gui.workbench.canvas.canvas_base import WorkbenchCanvasBase
from app.gui.workbench.focus.active_object import ActiveObject, active_object_from_canvas
from app.gui.workbench.focus.object_status import ObjectStatus

if TYPE_CHECKING:
    from app.gui.workbench.main_workbench import MainWorkbench


class WorkbenchFocusController(QObject):
    """
    Emits when the user’s active domain object changes (usually with the tab).

    Use :meth:`set_active_object` for programmatic overrides; normally the shell
    calls :meth:`set_active_from_canvas` from the tab strip.
    """

    active_object_changed = Signal(object)

    def __init__(self, window: MainWorkbench) -> None:
        super().__init__(window)
        self._window = window
        self._active = ActiveObject.none()

    @property
    def active_object(self) -> ActiveObject:
        return self._active

    def set_active_object(
        self,
        object_type: str,
        object_id: str | None,
        *,
        tab_key: str | None = None,
        status: ObjectStatus | None = None,
    ) -> None:
        """Set focus explicitly (e.g. tests or future cross-panel sync)."""
        tk = tab_key
        if tk is None:
            cur = self._window.canvas_tabs.current_canvas()
            tk = cur.tab_key if cur is not None else None
        st = status if status is not None else self._active.status
        self._active = ActiveObject(object_type, object_id, tk, st)
        self.active_object_changed.emit(self._active)

    def set_active_from_canvas(self, canvas: WorkbenchCanvasBase | None) -> None:
        """Derive focus from the active tab’s widget."""
        base = active_object_from_canvas(canvas)
        tab_key = canvas.tab_key if canvas is not None else None
        status = ObjectStatus.READY
        if tab_key is not None:
            status = self._window.canvas_tabs.tab_status(tab_key)
        self._active = ActiveObject(
            base.object_type,
            base.object_id,
            tab_key,
            status,
        )
        self.active_object_changed.emit(self._active)

    def set_active_status(self, status: ObjectStatus) -> None:
        """Update status for the current focus (e.g. after Run); keeps type/id/tab_key."""
        self._active = ActiveObject(
            self._active.object_type,
            self._active.object_id,
            self._active.tab_key,
            status,
        )
        self.active_object_changed.emit(self._active)
