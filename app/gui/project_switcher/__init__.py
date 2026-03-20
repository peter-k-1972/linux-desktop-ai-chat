"""
Project Switcher – globaler Projektkontext-UI.

ProjectSwitcherButton: TopBar-Button öffnet ProjectSwitcherDialog bei Klick.
ProjectSwitcherDialog: Dialog zum Wechseln des aktiven Projekts.
"""

from app.gui.project_switcher.project_switcher_button import ProjectSwitcherButton
from app.gui.project_switcher.project_switcher_dialog import (
    ProjectSwitcherDialog,
    NewProjectDialog,
)

__all__ = ["ProjectSwitcherButton", "ProjectSwitcherDialog", "NewProjectDialog"]
