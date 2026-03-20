"""Workspace – Tab-/Stack-Host für Screens."""

from app.gui.workspace.workspace_host import WorkspaceHost
from app.gui.workspace.screen_registry import ScreenRegistry, get_screen_registry

__all__ = ["WorkspaceHost", "ScreenRegistry", "get_screen_registry"]
