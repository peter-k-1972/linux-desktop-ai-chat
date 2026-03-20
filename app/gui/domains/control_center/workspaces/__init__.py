"""Control Center Workspaces."""

from app.gui.domains.control_center.workspaces.base_management_workspace import BaseManagementWorkspace
from app.gui.domains.control_center.workspaces.models_workspace import ModelsWorkspace
from app.gui.domains.control_center.workspaces.providers_workspace import ProvidersWorkspace
from app.gui.domains.control_center.workspaces.agents_workspace import AgentsWorkspace
from app.gui.domains.control_center.workspaces.tools_workspace import ToolsWorkspace
from app.gui.domains.control_center.workspaces.data_stores_workspace import DataStoresWorkspace

__all__ = [
    "BaseManagementWorkspace",
    "ModelsWorkspace",
    "ProvidersWorkspace",
    "AgentsWorkspace",
    "ToolsWorkspace",
    "DataStoresWorkspace",
]
