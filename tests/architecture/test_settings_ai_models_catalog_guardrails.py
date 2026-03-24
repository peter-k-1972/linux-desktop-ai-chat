"""
Guardrail: AI-Models-Settings-Panel ohne direkten Unified-Catalog-Service / ohne get_infrastructure.

Legacy-Katalog: ``ServiceAiModelCatalogAdapter``; skalare Legacy-Werte: ``ServiceSettingsAdapter``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.architecture.arch_guard_config import APP_ROOT

PANEL = APP_ROOT / "gui" / "domains" / "settings" / "panels" / "ai_models_settings_panel.py"


@pytest.mark.architecture
def test_ai_models_panel_no_unified_catalog_service_direct() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "get_unified_model_catalog_service" not in text


@pytest.mark.architecture
def test_ai_models_panel_no_get_infrastructure() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "get_infrastructure(" not in text


@pytest.mark.architecture
def test_ai_models_panel_no_get_service_pattern() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert re.search(r"get_\w+_service\s*\(", text) is None


@pytest.mark.architecture
def test_legacy_catalog_uses_catalog_adapter() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "async def _load_models_legacy" in text
    assert "ServiceAiModelCatalogAdapter" in text
    assert "load_chat_selectable_catalog_for_settings" in text
