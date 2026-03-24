"""AdvancedSettingsPanel — Port-Pfad vs. Legacy."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.settings.panels.advanced_settings_panel import AdvancedSettingsPanel
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
    LoadAdvancedSettingsCommand,
    SetChatContextModeCommand,
)


class _FakePort:
    def __init__(self) -> None:
        self._state = AdvancedSettingsState(
            debug_panel_enabled=True,
            context_debug_enabled=False,
            chat_context_mode="semantic",
            error=None,
        )
        self.writes: list[AdvancedSettingsWritePatch] = []

    def load_appearance_state(self):  # pragma: no cover
        raise NotImplementedError

    def validate_theme_id(self, _tid: str) -> bool:  # pragma: no cover
        return False

    def persist_theme_choice(self, _tid: str) -> None:  # pragma: no cover
        raise NotImplementedError

    def load_advanced_settings_state(self) -> AdvancedSettingsState:
        return self._state

    def persist_advanced_settings(self, write: AdvancedSettingsWritePatch) -> None:
        self.writes.append(write)
        if write.debug_panel_enabled is not None:
            self._state = AdvancedSettingsState(
                debug_panel_enabled=write.debug_panel_enabled,
                context_debug_enabled=self._state.context_debug_enabled,
                chat_context_mode=self._state.chat_context_mode,
                error=None,
            )
        if write.context_debug_enabled is not None:
            self._state = AdvancedSettingsState(
                debug_panel_enabled=self._state.debug_panel_enabled,
                context_debug_enabled=write.context_debug_enabled,
                chat_context_mode=self._state.chat_context_mode,
                error=None,
            )
        if write.chat_context_mode is not None:
            self._state = AdvancedSettingsState(
                debug_panel_enabled=self._state.debug_panel_enabled,
                context_debug_enabled=self._state.context_debug_enabled,
                chat_context_mode=write.chat_context_mode,  # type: ignore[arg-type]
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


def test_legacy_panel_loads_without_port(qapp) -> None:
    panel = AdvancedSettingsPanel(settings_port=None)
    assert panel._presenter is None
    assert panel.debug_panel_check.isEnabled()


def test_port_path_reflects_load(qapp) -> None:
    port = _FakePort()
    port._state = AdvancedSettingsState(
        debug_panel_enabled=False,
        context_debug_enabled=True,
        chat_context_mode="off",
        error=None,
    )
    panel = AdvancedSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    assert panel.debug_panel_check.isChecked() is False
    assert panel.context_debug_check.isChecked() is True
    assert panel.context_mode_combo.currentText() == "off"


def test_port_path_invalid_mode_shows_message(qapp) -> None:
    port = _FakePort()
    panel = AdvancedSettingsPanel(settings_port=port)
    assert panel._presenter is not None
    panel._presenter.handle_command(LoadAdvancedSettingsCommand())
    panel._presenter.handle_command(SetChatContextModeCommand("bad"))
    assert not panel._error_label.isHidden()
    assert "Ungültig" in panel._error_label.text()
