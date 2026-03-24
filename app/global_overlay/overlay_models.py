"""
Reine Datenmodelle für das produktweite Overlay (ohne Qt).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OverlaySurfaceKind(str, Enum):
    """Welche Overlay-Oberfläche gemeint ist."""

    NORMAL = "normal"
    EMERGENCY = "emergency"


@dataclass(frozen=True, slots=True)
class OverlayStatusSnapshot:
    """Read-only Status für Overlay-Anzeige (Slice 1)."""

    product_title: str
    active_gui_id: str
    gui_display_name: str
    gui_type: str
    default_fallback_gui_id: str
    preferred_gui_id: str
    theme_style_hint: str
    app_release_version: str
    bridge_interface_version: str
    ui_contracts_release_version: str
    backend_bundle_version: str
