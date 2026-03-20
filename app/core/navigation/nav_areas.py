"""
NavArea – area IDs for navigation.

Core constants; app.gui.navigation.nav_areas re-exports for backward compatibility.
"""


class NavArea:
    """Constants for navigation areas."""

    COMMAND_CENTER = "command_center"
    PROJECT_HUB = "project_hub"
    OPERATIONS = "operations"
    CONTROL_CENTER = "control_center"
    QA_GOVERNANCE = "qa_governance"
    RUNTIME_DEBUG = "runtime_debug"
    SETTINGS = "settings"

    @classmethod
    def all_areas(cls) -> list[tuple[str, str]]:
        """(area_id, title) for main areas."""
        return [
            (cls.COMMAND_CENTER, "Kommandozentrale"),
            (cls.OPERATIONS, "Operations"),
            (cls.CONTROL_CENTER, "Control Center"),
            (cls.QA_GOVERNANCE, "QA & Governance"),
            (cls.RUNTIME_DEBUG, "Runtime / Debug"),
            (cls.SETTINGS, "Settings"),
        ]
