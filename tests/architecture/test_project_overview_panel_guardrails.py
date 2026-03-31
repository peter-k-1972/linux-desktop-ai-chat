"""
Guardrail: migriertes ``ProjectOverviewPanel`` ohne direkte Host-/Service-Kopplung.
"""

from __future__ import annotations

import re

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "projects" / "panels" / "project_overview_panel.py"


@pytest.mark.architecture
def test_project_overview_panel_no_banned_direct_imports() -> None:
    text = PANEL.read_text(encoding="utf-8")
    banned_substrings = (
        "app.services.project_service",
        "app.gui.navigation.nav_areas",
        "app.gui.workspace.workspace_host",
        "app.gui.domains.operations.operations_context",
        "app.core.context.project_context_manager",
    )
    for banned in banned_substrings:
        assert banned not in text
    banned_calls = (
        r"get_project_service\s*\(",
        r"NavArea\b",
        r"WorkspaceHost\b",
        r"set_pending_context\s*\(",
        r"get_project_context_manager\s*\(",
    )
    for pattern in banned_calls:
        assert re.search(pattern, text) is None
