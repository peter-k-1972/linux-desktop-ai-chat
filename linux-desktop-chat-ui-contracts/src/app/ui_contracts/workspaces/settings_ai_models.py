"""
Settings — AI Models, skalare Felder (Qt-frei).

Slice 4 (Teilschnitt): Temperatur, Max-Tokens, Think-Modus, Streaming-Flag.
Unified Model Catalog: Slice 4b → ``settings_ai_model_catalog`` + eigener Port/Adapter/Presenter.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal, Union

from app.ui_contracts.common.errors import SettingsErrorInfo

ThinkMode = Literal["auto", "off", "low", "medium", "high"]

THINK_MODES: tuple[ThinkMode, ...] = ("auto", "off", "low", "medium", "high")

TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 2.0
MAX_TOKENS_MIN = 0
MAX_TOKENS_MAX = 32768


@dataclass(frozen=True, slots=True)
class AiModelsScalarSettingsState:
    temperature: float
    max_tokens: int
    think_mode: ThinkMode
    chat_streaming_enabled: bool
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class AiModelsScalarSettingsPatch:
    temperature: float | None = None
    max_tokens: int | None = None
    think_mode: ThinkMode | None = None
    chat_streaming_enabled: bool | None = None
    error: SettingsErrorInfo | None = None
    has_error_update: bool = False


@dataclass(frozen=True, slots=True)
class AiModelsScalarWritePatch:
    temperature: float | None = None
    max_tokens: int | None = None
    think_mode: str | None = None
    chat_streaming_enabled: bool | None = None


def merge_ai_models_scalar_state(
    base: AiModelsScalarSettingsState,
    patch: AiModelsScalarSettingsPatch,
) -> AiModelsScalarSettingsState:
    t = patch.temperature if patch.temperature is not None else base.temperature
    mt = patch.max_tokens if patch.max_tokens is not None else base.max_tokens
    tm = patch.think_mode if patch.think_mode is not None else base.think_mode
    cs = (
        patch.chat_streaming_enabled
        if patch.chat_streaming_enabled is not None
        else base.chat_streaming_enabled
    )
    err = patch.error if patch.has_error_update else base.error
    return replace(
        base,
        temperature=t,
        max_tokens=mt,
        think_mode=tm,
        chat_streaming_enabled=cs,
        error=err,
    )


@dataclass(frozen=True, slots=True)
class LoadAiModelsScalarSettingsCommand:
    """Skalaren Zustand aus dem Port laden."""


@dataclass(frozen=True, slots=True)
class SetAiModelsTemperatureCommand:
    value: float


@dataclass(frozen=True, slots=True)
class SetAiModelsMaxTokensCommand:
    value: int


@dataclass(frozen=True, slots=True)
class SetAiModelsThinkModeCommand:
    mode: str


@dataclass(frozen=True, slots=True)
class SetAiModelsChatStreamingEnabledCommand:
    enabled: bool


AiModelsScalarCommand = Union[
    LoadAiModelsScalarSettingsCommand,
    SetAiModelsTemperatureCommand,
    SetAiModelsMaxTokensCommand,
    SetAiModelsThinkModeCommand,
    SetAiModelsChatStreamingEnabledCommand,
]


class SettingsAiModelsPortError(Exception):
    """Persistenz- oder Validierungsfehler (skalare AI-Models-Settings)."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
