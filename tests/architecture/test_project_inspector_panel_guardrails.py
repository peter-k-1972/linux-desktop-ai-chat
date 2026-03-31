"""
Guardrail: migriertes ``ProjectInspectorPanel`` ohne direkte Legacy-Rohdatenkopplung.
"""

from __future__ import annotations

import re

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "projects" / "panels" / "project_inspector_panel.py"


@pytest.mark.architecture
def test_project_inspector_panel_no_banned_direct_imports() -> None:
    text = PANEL.read_text(encoding="utf-8")
    banned_substrings = (
        "app.services.project_service",
        "app.projects.models",
        "format_context_rules_narrative",
        "format_default_context_policy_caption",
    )
    for banned in banned_substrings:
        assert banned not in text
    banned_calls = (
        r"get_project_service\s*\(",
        r"format_context_rules_narrative\s*\(",
        r"format_default_context_policy_caption\s*\(",
    )
    for pattern in banned_calls:
        assert re.search(pattern, text) is None
