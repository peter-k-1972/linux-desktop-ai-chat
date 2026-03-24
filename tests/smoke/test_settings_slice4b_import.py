"""Smoke: Settings Slice 4b (AI Model Catalog) Stack importierbar."""

import pytest


def test_settings_slice4b_stack_imports() -> None:
    pytest.importorskip("sqlalchemy")
    from app.gui.domains.settings.settings_ai_model_catalog_sink import SettingsAiModelCatalogSink
    from app.gui.domains.settings.panels.ai_models_settings_panel import AIModelsSettingsPanel
    from app.ui_application.adapters.service_ai_model_catalog_adapter import ServiceAiModelCatalogAdapter
    from app.ui_application.presenters.settings_ai_model_catalog_presenter import (
        SettingsAiModelCatalogPresenter,
    )
    from app.ui_application.ports.ai_model_catalog_port import AiModelCatalogPort
    from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogState

    assert callable(ServiceAiModelCatalogAdapter().persist_default_chat_model_id)
    assert AIModelsSettingsPanel.__name__ == "AIModelsSettingsPanel"
    assert AiModelCatalogState.__name__ == "AiModelCatalogState"
    assert AiModelCatalogPort.__name__ == "AiModelCatalogPort"
    assert SettingsAiModelCatalogPresenter.__name__ == "SettingsAiModelCatalogPresenter"
    assert SettingsAiModelCatalogSink.__name__ == "SettingsAiModelCatalogSink"
