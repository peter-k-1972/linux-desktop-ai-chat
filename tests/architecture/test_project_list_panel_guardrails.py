"""
Guardrail: migriertes ``ProjectListPanel`` ohne direkten ``project_service``-Import.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "operations" / "projects" / "panels" / "project_list_panel.py"


@pytest.mark.architecture
def test_project_list_panel_no_project_service_import() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "app.services.project_service" not in text
    assert re.search(r"get_project_service\s*\(", text) is None
