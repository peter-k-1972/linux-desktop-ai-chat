"""AIModelsSettingsPanel — skalarer Port, Catalog-Slice vs. Legacy-Katalog."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
from PySide6.QtWidgets import QApplication

from app.gui.domains.settings.panels.ai_models_settings_panel import AIModelsSettingsPanel
from app.ui_contracts.workspaces.settings_ai_model_catalog import (
    AiModelCatalogEntryDto,
    AiModelCatalogPortLoadOutcome,
)
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
    LoadAiModelsScalarSettingsCommand,
    SetAiModelsTemperatureCommand,
)


class _FakePort:
    def __init__(self) -> None:
        self._scalar = AiModelsScalarSettingsState(
            temperature=1.0,
            max_tokens=8192,
            think_mode="low",
            chat_streaming_enabled=False,
            error=None,
        )
        self.writes: list[AiModelsScalarWritePatch] = []

    def load_appearance_state(self):  # pragma: no cover
        raise NotImplementedError

    def validate_theme_id(self, _tid: str) -> bool:  # pragma: no cover
        return False

    def persist_theme_choice(self, _tid: str) -> None:  # pragma: no cover
        raise NotImplementedError

    def load_advanced_settings_state(self):  # pragma: no cover
        raise NotImplementedError

    def persist_advanced_settings(self, _w) -> None:  # pragma: no cover
        raise NotImplementedError

    def load_data_settings_state(self):  # pragma: no cover
        raise NotImplementedError

    def persist_data_settings(self, _w) -> None:  # pragma: no cover
        raise NotImplementedError

    def load_ai_models_scalar_state(self) -> AiModelsScalarSettingsState:
        return self._scalar

    def persist_ai_models_scalar(self, write: AiModelsScalarWritePatch) -> None:
        self.writes.append(write)
        if write.temperature is not None:
            self._scalar = AiModelsScalarSettingsState(
                temperature=write.temperature,
                max_tokens=self._scalar.max_tokens,
                think_mode=self._scalar.think_mode,
                chat_streaming_enabled=self._scalar.chat_streaming_enabled,
                error=None,
            )


class _FakeCatalogPort:
    def __init__(self, outcome: AiModelCatalogPortLoadOutcome) -> None:
        self._outcome = outcome
        self.persisted: list[str] = []

    async def load_chat_selectable_catalog_for_settings(self) -> AiModelCatalogPortLoadOutcome:
        return self._outcome

    def persist_default_chat_model_id(self, model_id: str) -> None:
        self.persisted.append(model_id)


def _catalog_entry(sid: str) -> AiModelCatalogEntryDto:
    return AiModelCatalogEntryDto(
        selection_id=sid,
        display_short=sid,
        display_detail="",
        chat_selectable=True,
        asset_type="",
        storage_root_name="",
        path_hint="",
        usage_summary="",
        quota_summary="",
        usage_quality_note="",
    )


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def test_legacy_panel_without_port(qapp) -> None:
    panel = AIModelsSettingsPanel(settings_port=None)
    assert panel._presenter is None


def test_port_path_reflects_scalar_load(qapp) -> None:
    port = _FakePort()
    panel = AIModelsSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    assert panel.temp_spin.value() == 1.0
    assert panel.tokens_spin.value() == 8192
    assert panel.think_mode_combo.currentText() == "low"
    assert panel.stream_check.isChecked() is False


def test_port_path_temperature_command(qapp) -> None:
    port = _FakePort()
    panel = AIModelsSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    panel._presenter.handle_command(SetAiModelsTemperatureCommand(0.2))
    assert any(w.temperature == 0.2 for w in port.writes)
    assert panel.temp_spin.value() == 0.2


def test_port_path_invalid_temperature_shows_error(qapp) -> None:
    port = _FakePort()
    panel = AIModelsSettingsPanel(settings_port=port)
    panel._presenter.handle_command(LoadAiModelsScalarSettingsCommand())
    panel._presenter.handle_command(SetAiModelsTemperatureCommand(5.0))
    assert not panel._error_label.isHidden()
    assert "Temperatur" in panel._error_label.text()


def test_port_path_without_catalog_keeps_legacy_catalog_presenter_none(qapp) -> None:
    port = _FakePort()
    panel = AIModelsSettingsPanel(settings_port=port, catalog_port=None)
    assert panel._catalog_presenter is None


@pytest.mark.asyncio
async def test_port_path_with_catalog_loads_combo(qapp) -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(_catalog_entry("m1"),),
        default_selection_id="m1",
        placeholder_line="",
    )
    cport = _FakeCatalogPort(outcome)
    panel = AIModelsSettingsPanel(settings_port=_FakePort(), catalog_port=cport)
    assert panel._catalog_presenter is not None
    await panel._catalog_presenter.run_catalog_load_once()
    assert panel.model_combo.count() >= 1


@pytest.mark.asyncio
async def test_port_path_with_catalog_persist_on_change(qapp) -> None:
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_entries",
        entries=(_catalog_entry("m1"),),
        default_selection_id="m1",
        placeholder_line="",
    )
    cport = _FakeCatalogPort(outcome)
    panel = AIModelsSettingsPanel(settings_port=_FakePort(), catalog_port=cport)
    await panel._catalog_presenter.run_catalog_load_once()
    panel.model_combo.setCurrentIndex(0)
    panel._on_model_changed()
    assert cport.persisted
