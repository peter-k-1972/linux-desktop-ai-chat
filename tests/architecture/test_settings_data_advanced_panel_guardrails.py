"""
Guardrail: Data- und Advanced-Settings-Panels ohne get_infrastructure im Quelltext.

Legacy nutzt ServiceSettingsAdapter (Nachzieher zu Settings-Slices 2/3).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

DATA_PANEL = APP_ROOT / "gui" / "domains" / "settings" / "panels" / "data_settings_panel.py"
ADV_PANEL = APP_ROOT / "gui" / "domains" / "settings" / "panels" / "advanced_settings_panel.py"


@pytest.mark.architecture
@pytest.mark.parametrize("path", (DATA_PANEL, ADV_PANEL))
def test_settings_panel_no_get_infrastructure(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
@pytest.mark.parametrize("path", (DATA_PANEL, ADV_PANEL))
def test_settings_panel_no_get_service_pattern(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert re.search(r"get_\w+_service\s*\(", text) is None
