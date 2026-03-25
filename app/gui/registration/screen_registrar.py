"""
Zentrale Screen-Registrierung — aufgeteilt in modulare Hilfsfunktionen.

Phase 1: alle Bereiche bleiben aktiv; keine Feature-Gates.
"""

from __future__ import annotations

from app.gui.domains.control_center import ControlCenterScreen
from app.gui.domains.dashboard import DashboardScreen
from app.gui.domains.operations import OperationsScreen
from app.gui.domains.qa_governance import QAGovernanceScreen
from app.gui.domains.runtime_debug import RuntimeDebugScreen
from app.gui.domains.settings import SettingsScreen
from app.gui.navigation.nav_areas import NavArea
from app.gui.registration.base_registrar import make_screen_factory
from app.gui.workspace.screen_registry import ScreenRegistry


def register_command_center_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.COMMAND_CENTER,
        make_screen_factory(DashboardScreen),
        "Kommandozentrale",
    )


def register_operations_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.OPERATIONS,
        make_screen_factory(OperationsScreen),
        "Operations",
    )


def register_control_center_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.CONTROL_CENTER,
        make_screen_factory(ControlCenterScreen),
        "Control Center",
    )


def register_qa_governance_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.QA_GOVERNANCE,
        make_screen_factory(QAGovernanceScreen),
        "QA & Governance",
    )


def register_runtime_debug_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.RUNTIME_DEBUG,
        make_screen_factory(RuntimeDebugScreen),
        "Runtime / Debug",
    )


def register_settings_screen(registry: ScreenRegistry) -> None:
    registry.register(
        NavArea.SETTINGS,
        make_screen_factory(SettingsScreen),
        "Settings",
    )


def register_all_navigation_area_screens(registry: ScreenRegistry) -> None:
    """Registriert alle Top-Level-Navigations-Screens (volle Shell)."""
    register_command_center_screen(registry)
    register_operations_screen(registry)
    register_control_center_screen(registry)
    register_qa_governance_screen(registry)
    register_runtime_debug_screen(registry)
    register_settings_screen(registry)
