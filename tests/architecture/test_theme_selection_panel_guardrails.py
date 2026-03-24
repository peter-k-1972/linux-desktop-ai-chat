"""
Guardrail: ThemeSelectionPanel darf weder get_infrastructure noch get_*_service nutzen.

Legacy-Persistenz läuft über ServiceSettingsAdapter.persist_theme_choice (Slice 1).
``get_theme_manager`` bleibt GUI-Registry — erlaubt.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL: Path = APP_ROOT / "gui" / "domains" / "settings" / "panels" / "theme_selection_panel.py"


@pytest.mark.architecture
def test_theme_selection_panel_no_get_infrastructure() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
def test_theme_selection_panel_no_get_service_pattern() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert re.search(r"get_\w+_service\s*\(", text) is None
