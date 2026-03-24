"""DataSettingsPanel — Port-Pfad vs. Legacy."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.settings.panels.data_settings_panel import DataSettingsPanel
from app.ui_contracts.workspaces.settings_data import (
    DataSettingsState,
    DataSettingsWritePatch,
    LoadDataSettingsCommand,
    SetPromptDirectoryCommand,
    SetRagTopKCommand,
)


class _FakePort:
    def __init__(self) -> None:
        self._state = DataSettingsState(
            rag_enabled=True,
            rag_space="documentation",
            rag_top_k=7,
            self_improving_enabled=True,
            prompt_storage_type="directory",
            prompt_directory="/tmp/p",
            prompt_confirm_delete=False,
            error=None,
        )
        self.writes: list[DataSettingsWritePatch] = []

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

    def load_data_settings_state(self) -> DataSettingsState:
        return self._state

    def persist_data_settings(self, write: DataSettingsWritePatch) -> None:
        self.writes.append(write)
        if write.rag_top_k is not None:
            self._state = DataSettingsState(
                rag_enabled=self._state.rag_enabled,
                rag_space=self._state.rag_space,
                rag_top_k=write.rag_top_k,
                self_improving_enabled=self._state.self_improving_enabled,
                prompt_storage_type=self._state.prompt_storage_type,
                prompt_directory=self._state.prompt_directory,
                prompt_confirm_delete=self._state.prompt_confirm_delete,
                error=None,
            )
        if write.prompt_directory_set:
            self._state = DataSettingsState(
                rag_enabled=self._state.rag_enabled,
                rag_space=self._state.rag_space,
                rag_top_k=self._state.rag_top_k,
                self_improving_enabled=self._state.self_improving_enabled,
                prompt_storage_type=self._state.prompt_storage_type,
                prompt_directory=write.prompt_directory or "",
                prompt_confirm_delete=self._state.prompt_confirm_delete,
                error=None,
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
    panel = DataSettingsPanel(settings_port=None)
    assert panel._presenter is None


def test_port_path_reflects_load(qapp) -> None:
    port = _FakePort()
    panel = DataSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    assert panel.rag_enabled_check.isChecked()
    assert panel.rag_space_combo.currentText() == "documentation"
    assert panel.rag_top_k_spin.value() == 7
    assert panel.prompt_directory_edit.text() == "/tmp/p"


def test_port_path_set_directory_command(qapp) -> None:
    port = _FakePort()
    panel = DataSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    panel._presenter.handle_command(SetPromptDirectoryCommand("/opt/prompts"))
    assert any(
        w.prompt_directory_set and w.prompt_directory == "/opt/prompts" for w in port.writes
    )
    assert panel.prompt_directory_edit.text() == "/opt/prompts"


def test_port_path_invalid_top_k_shows_error(qapp) -> None:
    port = _FakePort()
    panel = DataSettingsPanel(settings_port=port)
    panel._presenter.handle_command(LoadDataSettingsCommand())
    panel._presenter.handle_command(SetRagTopKCommand(0))
    assert not panel._error_label.isHidden()
    assert "Top-K" in panel._error_label.text()
