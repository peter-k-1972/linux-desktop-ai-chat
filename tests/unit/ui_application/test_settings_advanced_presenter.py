"""SettingsAdvancedPresenter — Qt-frei."""

from __future__ import annotations

from app.ui_application.presenters.settings_advanced_presenter import SettingsAdvancedPresenter
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
    LoadAdvancedSettingsCommand,
    SetChatContextModeCommand,
    SetContextDebugEnabledCommand,
    SetDebugPanelEnabledCommand,
    SettingsAdvancedPortError,
)


class _RecordingSink:
    def __init__(self) -> None:
        self.full: list[AdvancedSettingsState] = []
        self.patches: list = []

    def apply_full_state(self, state: AdvancedSettingsState) -> None:
        self.full.append(state)

    def apply_patch(self, patch) -> None:
        self.patches.append(patch)


class _FakePort:
    def __init__(self) -> None:
        self._state = AdvancedSettingsState(
            debug_panel_enabled=True,
            context_debug_enabled=False,
            chat_context_mode="semantic",
            error=None,
        )
        self.writes: list[AdvancedSettingsWritePatch] = []
        self.fail_next = False

    def load_advanced_settings_state(self) -> AdvancedSettingsState:
        return self._state

    def load_appearance_state(self):  # pragma: no cover
        raise NotImplementedError

    def validate_theme_id(self, _tid: str) -> bool:  # pragma: no cover
        return False

    def persist_theme_choice(self, _tid: str) -> None:  # pragma: no cover
        raise NotImplementedError

    def persist_advanced_settings(self, write: AdvancedSettingsWritePatch) -> None:
        self.writes.append(write)
        if self.fail_next:
            self.fail_next = False
            raise SettingsAdvancedPortError("persist_failed", "nope", recoverable=True)
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


def test_load_full_state() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAdvancedPresenter(sink, port)
    p.handle_command(LoadAdvancedSettingsCommand())
    assert len(sink.full) == 1
    assert sink.full[0].chat_context_mode == "semantic"


def test_set_debug_persists() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAdvancedPresenter(sink, port)
    p.handle_command(LoadAdvancedSettingsCommand())
    p.handle_command(SetDebugPanelEnabledCommand(False))
    assert port.writes == [AdvancedSettingsWritePatch(debug_panel_enabled=False)]
    assert sink.full[-1].debug_panel_enabled is False


def test_invalid_mode_patch_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAdvancedPresenter(sink, port)
    p.handle_command(LoadAdvancedSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetChatContextModeCommand("bogus"))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_context_mode"
        for patch in sink.patches
    )


def test_persist_failure_shows_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    port.fail_next = True
    p = SettingsAdvancedPresenter(sink, port)
    p.handle_command(LoadAdvancedSettingsCommand())
    p.handle_command(SetContextDebugEnabledCommand(True))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "persist_failed"
        for patch in sink.patches
    )


def test_no_port_backend_not_wired() -> None:
    sink = _RecordingSink()
    p = SettingsAdvancedPresenter(sink, None)
    p.handle_command(LoadAdvancedSettingsCommand())
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "backend_not_wired" for patch in sink.patches
    )
