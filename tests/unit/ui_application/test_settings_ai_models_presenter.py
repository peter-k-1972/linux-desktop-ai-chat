"""SettingsAiModelsPresenter — skalare AI-Models-Settings."""

from __future__ import annotations

from typing import cast

from app.ui_application.presenters.settings_ai_models_presenter import SettingsAiModelsPresenter
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
    LoadAiModelsScalarSettingsCommand,
    SetAiModelsChatStreamingEnabledCommand,
    SetAiModelsMaxTokensCommand,
    SetAiModelsTemperatureCommand,
    SetAiModelsThinkModeCommand,
    SettingsAiModelsPortError,
    ThinkMode,
)


class _RecordingSink:
    def __init__(self) -> None:
        self.full: list[AiModelsScalarSettingsState] = []
        self.patches: list = []

    def apply_full_state(self, state: AiModelsScalarSettingsState) -> None:
        self.full.append(state)

    def apply_patch(self, patch) -> None:
        self.patches.append(patch)


class _FakePort:
    def __init__(self) -> None:
        self._state = AiModelsScalarSettingsState(
            temperature=0.8,
            max_tokens=2048,
            think_mode="medium",
            chat_streaming_enabled=False,
            error=None,
        )
        self.writes: list[AiModelsScalarWritePatch] = []
        self.fail_next = False

    def load_ai_models_scalar_state(self) -> AiModelsScalarSettingsState:
        return self._state

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

    def persist_ai_models_scalar(self, write: AiModelsScalarWritePatch) -> None:
        self.writes.append(write)
        if self.fail_next:
            self.fail_next = False
            raise SettingsAiModelsPortError("persist_failed", "nope", recoverable=True)
        if write.temperature is not None:
            self._state = AiModelsScalarSettingsState(
                temperature=write.temperature,
                max_tokens=self._state.max_tokens,
                think_mode=self._state.think_mode,
                chat_streaming_enabled=self._state.chat_streaming_enabled,
                error=None,
            )
        if write.max_tokens is not None:
            self._state = AiModelsScalarSettingsState(
                temperature=self._state.temperature,
                max_tokens=write.max_tokens,
                think_mode=self._state.think_mode,
                chat_streaming_enabled=self._state.chat_streaming_enabled,
                error=None,
            )
        if write.think_mode is not None:
            self._state = AiModelsScalarSettingsState(
                temperature=self._state.temperature,
                max_tokens=self._state.max_tokens,
                think_mode=cast(ThinkMode, write.think_mode),
                chat_streaming_enabled=self._state.chat_streaming_enabled,
                error=None,
            )
        if write.chat_streaming_enabled is not None:
            self._state = AiModelsScalarSettingsState(
                temperature=self._state.temperature,
                max_tokens=self._state.max_tokens,
                think_mode=self._state.think_mode,
                chat_streaming_enabled=write.chat_streaming_enabled,
                error=None,
            )


def test_load_full_state() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    assert len(sink.full) == 1
    assert sink.full[0].temperature == 0.8
    assert sink.full[0].think_mode == "medium"


def test_set_temperature() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    p.handle_command(SetAiModelsTemperatureCommand(1.1))
    assert any(w.temperature == 1.1 for w in port.writes)
    assert sink.full[-1].temperature == 1.1


def test_invalid_temperature_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetAiModelsTemperatureCommand(3.0))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_temperature"
        for patch in sink.patches
    )


def test_invalid_max_tokens_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetAiModelsMaxTokensCommand(400_000))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_max_tokens"
        for patch in sink.patches
    )


def test_invalid_think_mode_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetAiModelsThinkModeCommand("nope"))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_think_mode"
        for patch in sink.patches
    )


def test_set_streaming() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    p.handle_command(SetAiModelsChatStreamingEnabledCommand(True))
    assert any(w.chat_streaming_enabled is True for w in port.writes)
    assert sink.full[-1].chat_streaming_enabled is True


def test_persist_failure_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    port.fail_next = True
    p = SettingsAiModelsPresenter(sink, port)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    p.handle_command(SetAiModelsThinkModeCommand("high"))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "persist_failed"
        for patch in sink.patches
    )


def test_no_port_backend_not_wired() -> None:
    sink = _RecordingSink()
    p = SettingsAiModelsPresenter(sink, None)
    p.handle_command(LoadAiModelsScalarSettingsCommand())
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "backend_not_wired"
        for patch in sink.patches
    )
