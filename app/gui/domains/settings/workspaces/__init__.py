"""Settings Workspaces."""

from app.gui.domains.settings.workspaces.base_settings_workspace import BaseSettingsWorkspace
from app.gui.domains.settings.workspaces.appearance_workspace import AppearanceWorkspace
from app.gui.domains.settings.workspaces.system_workspace import SystemWorkspace
from app.gui.domains.settings.workspaces.models_workspace import ModelsWorkspace
from app.gui.domains.settings.workspaces.agents_workspace import AgentsWorkspace
from app.gui.domains.settings.workspaces.advanced_workspace import AdvancedWorkspace

__all__ = [
    "BaseSettingsWorkspace",
    "AppearanceWorkspace",
    "SystemWorkspace",
    "ModelsWorkspace",
    "AgentsWorkspace",
    "AdvancedWorkspace",
]
