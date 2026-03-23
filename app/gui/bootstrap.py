"""
Bootstrap – Registrierung aller Screens bei App-Start.

Zentrale Stelle für ScreenRegistry. Keine If/Else-Ketten.
"""

from app.gui.workspace.screen_registry import get_screen_registry
from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.dashboard import DashboardScreen
from app.gui.domains.operations import OperationsScreen
from app.gui.domains.control_center import ControlCenterScreen
from app.gui.domains.qa_governance import QAGovernanceScreen
from app.gui.domains.runtime_debug import RuntimeDebugScreen
from app.gui.domains.settings import SettingsScreen


def register_all_screens() -> None:
    """Registriert alle Screens in der ScreenRegistry."""

    def make_factory(screen_class):
        def factory():
            return screen_class()
        return factory

    registry = get_screen_registry()

    registry.register(
        NavArea.COMMAND_CENTER,
        make_factory(DashboardScreen),
        "Kommandozentrale",
    )
    registry.register(
        NavArea.OPERATIONS,
        make_factory(OperationsScreen),
        "Operations",
    )
    registry.register(
        NavArea.CONTROL_CENTER,
        make_factory(ControlCenterScreen),
        "Control Center",
    )
    registry.register(
        NavArea.QA_GOVERNANCE,
        make_factory(QAGovernanceScreen),
        "QA & Governance",
    )
    registry.register(
        NavArea.RUNTIME_DEBUG,
        make_factory(RuntimeDebugScreen),
        "Runtime / Debug",
    )
    registry.register(
        NavArea.SETTINGS,
        make_factory(SettingsScreen),
        "Settings",
    )
