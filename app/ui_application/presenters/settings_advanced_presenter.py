"""
SettingsAdvancedPresenter — Advanced/Debug zwischen Port und Sink.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import SettingsAdvancedUiSink
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedCommand,
    AdvancedSettingsPatch,
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
    CHAT_CONTEXT_MODES,
    LoadAdvancedSettingsCommand,
    SetChatContextModeCommand,
    SetContextDebugEnabledCommand,
    SetDebugPanelEnabledCommand,
    SettingsAdvancedPortError,
    merge_advanced_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsAdvancedPresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsAdvancedUiSink,
        port: SettingsOperationsPort | None = None,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._state = AdvancedSettingsState(
            debug_panel_enabled=True,
            context_debug_enabled=False,
            chat_context_mode="semantic",
            error=None,
        )

    @property
    def state(self) -> AdvancedSettingsState:
        return self._state

    @property
    def port(self) -> SettingsOperationsPort | None:
        return self._port

    def handle_command(self, command: AdvancedCommand) -> None:
        if self._port is None:
            self._sink.apply_patch(
                AdvancedSettingsPatch(
                    error=SettingsErrorInfo(
                        code="backend_not_wired",
                        message="SettingsOperationsPort ist nicht injiziert.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
            )
            return

        if isinstance(command, LoadAdvancedSettingsCommand):
            self._state = self._port.load_advanced_settings_state()
            self._sink.apply_full_state(self._state)
            return

        if isinstance(command, SetDebugPanelEnabledCommand):
            self._persist_and_reload(AdvancedSettingsWritePatch(debug_panel_enabled=command.enabled))
            return

        if isinstance(command, SetContextDebugEnabledCommand):
            self._persist_and_reload(AdvancedSettingsWritePatch(context_debug_enabled=command.enabled))
            return

        if isinstance(command, SetChatContextModeCommand):
            if command.mode not in CHAT_CONTEXT_MODES:
                patch = AdvancedSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_context_mode",
                        message=f"Ungültiger Chat-Kontext-Modus: {command.mode!r}",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_advanced_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(
                AdvancedSettingsWritePatch(chat_context_mode=command.mode),
            )
            return

    def _persist_and_reload(self, write: AdvancedSettingsWritePatch) -> None:
        assert self._port is not None
        try:
            self._port.persist_advanced_settings(write)
        except SettingsAdvancedPortError as exc:
            patch = AdvancedSettingsPatch(
                error=SettingsErrorInfo(
                    code=exc.code,
                    message=exc.message,
                    recoverable=exc.recoverable,
                ),
                has_error_update=True,
            )
            self._state = merge_advanced_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        self._state = self._port.load_advanced_settings_state()
        self._sink.apply_full_state(self._state)
