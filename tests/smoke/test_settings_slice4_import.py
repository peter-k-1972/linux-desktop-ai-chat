"""Smoke: Settings Slice 4 (AI Models skalar) — Module importierbar."""


def test_settings_ai_models_scalar_stack_imports() -> None:
    from app.gui.domains.settings.settings_ai_models_sink import SettingsAiModelsSink
    from app.gui.domains.settings.panels.ai_models_settings_panel import AIModelsSettingsPanel
    from app.ui_application.presenters.settings_ai_models_presenter import SettingsAiModelsPresenter
    from app.ui_contracts.workspaces.settings_ai_models import AiModelsScalarSettingsState

    assert SettingsAiModelsSink.__name__ == "SettingsAiModelsSink"
    assert AIModelsSettingsPanel.__name__ == "AIModelsSettingsPanel"
    assert SettingsAiModelsPresenter.__name__ == "SettingsAiModelsPresenter"
    assert AiModelsScalarSettingsState.__name__ == "AiModelsScalarSettingsState"
