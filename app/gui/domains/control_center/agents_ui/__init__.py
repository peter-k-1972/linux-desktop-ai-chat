"""Agents UI – Canonical Agent Manager flow.

Migrated from app.ui.agents (Phase 1). AgentManagerPanel, AgentListPanel, etc.
"""

from app.gui.domains.control_center.agents_ui.agent_manager_panel import (
    AgentManagerPanel,
    AgentManagerDialog,
)
from app.gui.domains.control_center.agents_ui.agent_list_panel import AgentListPanel
from app.gui.domains.control_center.agents_ui.agent_list_item import AgentListItem
from app.gui.domains.control_center.agents_ui.agent_profile_panel import AgentProfilePanel
from app.gui.domains.control_center.agents_ui.agent_avatar_widget import AgentAvatarWidget
from app.gui.domains.control_center.agents_ui.agent_form_widgets import (
    AgentProfileForm,
    AgentCapabilitiesEditor,
)
from app.gui.domains.control_center.agents_ui.agent_performance_tab import (
    AgentPerformanceTab,
)

__all__ = [
    "AgentManagerPanel",
    "AgentManagerDialog",
    "AgentListPanel",
    "AgentListItem",
    "AgentProfilePanel",
    "AgentAvatarWidget",
    "AgentProfileForm",
    "AgentCapabilitiesEditor",
    "AgentPerformanceTab",
]
