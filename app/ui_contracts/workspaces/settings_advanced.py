"""
Settings — Advanced / Debug (Qt-frei).

Slice 2: debug_panel_enabled, context_debug_enabled, chat_context_mode.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal, Union

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

ChatContextMode = Literal["neutral", "semantic", "off"]

CHAT_CONTEXT_MODES: tuple[ChatContextMode, ...] = ("neutral", "semantic", "off")


@dataclass(frozen=True, slots=True)
class AdvancedSettingsState:
    """Anzeige- und Persistenzzustand für Advanced-Panel."""

    debug_panel_enabled: bool
    context_debug_enabled: bool
    chat_context_mode: ChatContextMode
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class AdvancedSettingsPatch:
    """Teilupdate für Sink; None bei Wertfeldern = unverändert."""

    debug_panel_enabled: bool | None = None
    context_debug_enabled: bool | None = None
    chat_context_mode: ChatContextMode | None = None
    error: SettingsErrorInfo | None = None
    has_error_update: bool = False


@dataclass(frozen=True, slots=True)
class AdvancedSettingsWritePatch:
    """Nur gesetzte Felder werden an AppSettings geschrieben (ein save pro Aufruf)."""

    debug_panel_enabled: bool | None = None
    context_debug_enabled: bool | None = None
    chat_context_mode: str | None = None


def merge_advanced_state(
    base: AdvancedSettingsState,
    patch: AdvancedSettingsPatch,
) -> AdvancedSettingsState:
    dbg = patch.debug_panel_enabled if patch.debug_panel_enabled is not None else base.debug_panel_enabled
    ctx = patch.context_debug_enabled if patch.context_debug_enabled is not None else base.context_debug_enabled
    mode = patch.chat_context_mode if patch.chat_context_mode is not None else base.chat_context_mode
    err = patch.error if patch.has_error_update else base.error
    return replace(
        base,
        debug_panel_enabled=dbg,
        context_debug_enabled=ctx,
        chat_context_mode=mode,
        error=err,
    )


@dataclass(frozen=True, slots=True)
class LoadAdvancedSettingsCommand:
    """Zustand aus dem Port laden."""


@dataclass(frozen=True, slots=True)
class SetDebugPanelEnabledCommand:
    enabled: bool


@dataclass(frozen=True, slots=True)
class SetContextDebugEnabledCommand:
    enabled: bool


@dataclass(frozen=True, slots=True)
class SetChatContextModeCommand:
    mode: str


AdvancedCommand = Union[
    LoadAdvancedSettingsCommand,
    SetDebugPanelEnabledCommand,
    SetContextDebugEnabledCommand,
    SetChatContextModeCommand,
]


class SettingsAdvancedPortError(Exception):
    """Adapter/Persistenz-Fehler; Presenter mappt auf SettingsErrorInfo."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
