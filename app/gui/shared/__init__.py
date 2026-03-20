"""Shared – Basisklassen, Layout-Konstanten und wiederverwendbare Komponenten."""

from app.gui.shared.base_screen import BaseScreen
from app.gui.shared.base_panel import BasePanel
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.shared.layout_constants import (
    PANEL_PADDING,
    SIDEBAR_PADDING,
    SIDEBAR_SPACING,
    WORKSPACE_PADDING,
    WORKSPACE_SPACING,
    WIDGET_SPACING,
    apply_panel_layout,
    apply_sidebar_layout,
    apply_workspace_layout,
    apply_header_layout,
    apply_settings_layout,
)

__all__ = [
    "BaseScreen",
    "BasePanel",
    "BaseOperationsWorkspace",
    "PANEL_PADDING",
    "SIDEBAR_PADDING",
    "SIDEBAR_SPACING",
    "WORKSPACE_PADDING",
    "WORKSPACE_SPACING",
    "WIDGET_SPACING",
    "apply_panel_layout",
    "apply_sidebar_layout",
    "apply_workspace_layout",
    "apply_header_layout",
    "apply_settings_layout",
]
