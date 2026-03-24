"""
Zustandslogik Overlay — ohne Qt, unit-testbar.
"""

from __future__ import annotations

from typing import Any

from app.global_overlay.overlay_models import OverlaySurfaceKind


class OverlayController:
    """
    Hält Sichtbarkeitszustand für normales und Emergency-Overlay.

    Regel: höchstens eine Oberfläche sichtbar; Öffnen einer schließt die andere.
    """

    __slots__ = ("_emergency_visible", "_last_focus_widget", "_normal_visible")

    def __init__(self) -> None:
        self._normal_visible = False
        self._emergency_visible = False
        self._last_focus_widget: Any = None

    @property
    def normal_visible(self) -> bool:
        return self._normal_visible

    @property
    def emergency_visible(self) -> bool:
        return self._emergency_visible

    @property
    def last_focus_widget(self) -> Any:
        return self._last_focus_widget

    def set_last_focus_widget(self, widget: Any) -> None:
        self._last_focus_widget = widget

    def clear_last_focus_widget(self) -> None:
        self._last_focus_widget = None

    def toggle_normal_overlay(self) -> OverlaySurfaceKind | None:
        """
        Toggelt das normale Overlay.

        Returns:
            ``NORMAL`` wenn jetzt geöffnet, ``None`` wenn geschlossen.
        """
        if self._normal_visible:
            self._normal_visible = False
            return None
        self._emergency_visible = False
        self._normal_visible = True
        return OverlaySurfaceKind.NORMAL

    def toggle_emergency_overlay(self) -> OverlaySurfaceKind | None:
        if self._emergency_visible:
            self._emergency_visible = False
            return None
        self._normal_visible = False
        self._emergency_visible = True
        return OverlaySurfaceKind.EMERGENCY

    def close_overlay(self) -> None:
        """Schließt beide Oberflächen."""
        self._normal_visible = False
        self._emergency_visible = False

    def close_normal_only(self) -> None:
        self._normal_visible = False

    def close_emergency_only(self) -> None:
        self._emergency_visible = False
