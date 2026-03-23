"""Smoke: Operations-Unternavigation und Nav-Registry bleiben konsistent."""

from app.core.navigation.navigation_registry import get_entry
from app.gui.domains.operations.operations_nav import OperationsNav


def test_operations_nav_titles_match_registry():
    """Jeder Operations-Workspace-Eintrag muss zum Sidebar-Titel im Registry passen."""
    for area_id, title in OperationsNav.WORKSPACES:
        entry = get_entry(area_id)
        assert entry is not None, f"Unbekannte area_id in OperationsNav: {area_id}"
        assert entry.title == title, (
            f"Titel-Mismatch für {area_id!r}: OperationsNav={title!r}, "
            f"registry={entry.title!r} — bitte angleichen."
        )
