"""
Smoke Tests: Settings Workspace.

Prüft, dass Settings-Kategorien und -Panels ohne Fehler instanziiert werden können.
"""

import pytest

from PySide6.QtWidgets import QApplication

from app.core.config.settings_backend import InMemoryBackend
from app.services.infrastructure import init_infrastructure


@pytest.fixture
def qapp():
    """QApplication für GUI-Tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def _init_infrastructure_for_settings_panels():
    """Infrastructure mit InMemoryBackend für Settings-Panels."""
    init_infrastructure(settings_backend=InMemoryBackend())


def test_settings_categories_importable():
    """Settings-Kategorien sind importierbar."""
    from app.gui.domains.settings.categories import (
        ApplicationCategory,
        AppearanceCategory,
        AIModelsCategory,
        DataCategory,
        PrivacyCategory,
        AdvancedCategory,
        ProjectCategory,
        WorkspaceCategory,
    )
    assert ApplicationCategory is not None
    assert AppearanceCategory is not None
    assert AIModelsCategory is not None
    assert DataCategory is not None
    assert PrivacyCategory is not None
    assert AdvancedCategory is not None
    assert ProjectCategory is not None
    assert WorkspaceCategory is not None


def test_settings_workspace_creates(qapp):
    """SettingsWorkspace kann erstellt werden."""
    from app.gui.domains.settings.settings_workspace import SettingsWorkspace

    ws = SettingsWorkspace()
    assert ws is not None
    assert ws.get_current_category() in (
        "settings_application",
        "settings_appearance",
        "settings_ai_models",
        "settings_data",
        "settings_privacy",
        "settings_advanced",
        "settings_project",
        "settings_workspace",
    )


def test_ai_models_settings_panel_creates(qapp):
    """AIModelsSettingsPanel kann erstellt werden."""
    from app.gui.domains.settings.panels.ai_models_settings_panel import AIModelsSettingsPanel

    panel = AIModelsSettingsPanel()
    assert panel is not None


def test_data_settings_panel_creates(qapp):
    """DataSettingsPanel kann erstellt werden."""
    from app.gui.domains.settings.panels.data_settings_panel import DataSettingsPanel

    panel = DataSettingsPanel()
    assert panel is not None


def test_advanced_settings_panel_creates(qapp):
    """AdvancedSettingsPanel kann erstellt werden."""
    from app.gui.domains.settings.panels.advanced_settings_panel import AdvancedSettingsPanel

    panel = AdvancedSettingsPanel()
    assert panel is not None
