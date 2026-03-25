"""
SettingsAiModelsPresenter — skalare AI-Model-Parameter (Slice 4).

Kein Unified Model Catalog (async) — nur AppSettings-Felder.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import SettingsAiModelsUiSink
from app.ui_contracts.common.errors import SettingsErrorInfo
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarCommand,
    AiModelsScalarSettingsPatch,
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
    LoadAiModelsScalarSettingsCommand,
    MAX_TOKENS_MAX,
    MAX_TOKENS_MIN,
    SetAiModelsChatStreamingEnabledCommand,
    SetAiModelsMaxTokensCommand,
    SetAiModelsTemperatureCommand,
    SetAiModelsThinkModeCommand,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    THINK_MODES,
    SettingsAiModelsPortError,
    merge_ai_models_scalar_state,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsAiModelsPresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsAiModelsUiSink,
        port: SettingsOperationsPort | None = None,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._state = AiModelsScalarSettingsState(
            temperature=0.7,
            max_tokens=4096,
            think_mode="auto",
            chat_streaming_enabled=True,
            error=None,
        )

    @property
    def state(self) -> AiModelsScalarSettingsState:
        return self._state

    @property
    def port(self) -> SettingsOperationsPort | None:
        return self._port

    def handle_command(self, command: AiModelsScalarCommand) -> None:
        if self._port is None:
            self._sink.apply_patch(
                AiModelsScalarSettingsPatch(
                    error=SettingsErrorInfo(
                        code="backend_not_wired",
                        message="SettingsOperationsPort ist nicht injiziert.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
            )
            return

        if isinstance(command, LoadAiModelsScalarSettingsCommand):
            self._state = self._port.load_ai_models_scalar_state()
            self._sink.apply_full_state(self._state)
            return

        if isinstance(command, SetAiModelsTemperatureCommand):
            if command.value < TEMPERATURE_MIN or command.value > TEMPERATURE_MAX:
                patch = AiModelsScalarSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_temperature",
                        message=f"Temperatur muss zwischen {TEMPERATURE_MIN} und {TEMPERATURE_MAX} liegen.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_ai_models_scalar_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(AiModelsScalarWritePatch(temperature=command.value))
            return

        if isinstance(command, SetAiModelsMaxTokensCommand):
            if command.value < MAX_TOKENS_MIN or command.value > MAX_TOKENS_MAX:
                patch = AiModelsScalarSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_max_tokens",
                        message=f"Max. Tokens muss zwischen {MAX_TOKENS_MIN} und {MAX_TOKENS_MAX} liegen.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_ai_models_scalar_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(AiModelsScalarWritePatch(max_tokens=command.value))
            return

        if isinstance(command, SetAiModelsThinkModeCommand):
            if command.mode not in THINK_MODES:
                patch = AiModelsScalarSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_think_mode",
                        message=f"Ungültiger Thinking-Modus: {command.mode!r}",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_ai_models_scalar_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(AiModelsScalarWritePatch(think_mode=command.mode))
            return

        if isinstance(command, SetAiModelsChatStreamingEnabledCommand):
            self._persist_and_reload(
                AiModelsScalarWritePatch(chat_streaming_enabled=command.enabled),
            )
            return

    def _persist_and_reload(self, write: AiModelsScalarWritePatch) -> None:
        assert self._port is not None
        try:
            self._port.persist_ai_models_scalar(write)
        except SettingsAiModelsPortError as exc:
            patch = AiModelsScalarSettingsPatch(
                error=SettingsErrorInfo(
                    code=exc.code,
                    message=exc.message,
                    recoverable=exc.recoverable,
                ),
                has_error_update=True,
            )
            self._state = merge_ai_models_scalar_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        self._state = self._port.load_ai_models_scalar_state()
        self._sink.apply_full_state(self._state)
