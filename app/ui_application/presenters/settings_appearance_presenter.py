"""
SettingsAppearancePresenter — Appearance/Theme zwischen Port und Sink.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import TYPE_CHECKING

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import SettingsAppearanceUiSink
from app.ui_contracts.common.errors import SettingsErrorInfo
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceCommand,
    AppearanceSettingsState,
    AppearanceStatePatch,
    LoadAppearanceSettingsCommand,
    SelectThemeCommand,
    SettingsAppearancePortError,
    merge_appearance_state,
)

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsAppearancePresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsAppearanceUiSink,
        port: SettingsOperationsPort | None = None,
        *,
        on_theme_choice_committed: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._state = AppearanceSettingsState(themes=(), selected_theme_id="", error=None)
        self._on_theme_choice_committed = on_theme_choice_committed

    @property
    def state(self) -> AppearanceSettingsState:
        return self._state

    @property
    def port(self) -> SettingsOperationsPort | None:
        return self._port

    def handle_command(self, command: AppearanceCommand) -> None:
        if self._port is None:
            self._sink.apply_patch(
                AppearanceStatePatch(
                    error=SettingsErrorInfo(
                        code="backend_not_wired",
                        message="SettingsOperationsPort ist nicht injiziert.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
            )
            return

        if isinstance(command, LoadAppearanceSettingsCommand):
            self._state = self._port.load_appearance_state()
            self._sink.apply_full_state(self._state)
            return

        if isinstance(command, SelectThemeCommand):
            self._handle_select(command.theme_id)
            return

    def _handle_select(self, theme_id: str) -> None:
        if not self._port.validate_theme_id(theme_id):
            patch = AppearanceStatePatch(
                error=SettingsErrorInfo(
                    code="unknown_theme",
                    message=f"Unbekanntes Theme: {theme_id!r}",
                    recoverable=True,
                ),
                has_error_update=True,
            )
            self._state = merge_appearance_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        previous = self._state.selected_theme_id
        if not self._sink.apply_selected_theme_visual(theme_id):
            patch = AppearanceStatePatch(
                error=SettingsErrorInfo(
                    code="theme_apply_failed",
                    message="Theme konnte nicht angewendet werden.",
                    recoverable=True,
                ),
                has_error_update=True,
            )
            self._state = merge_appearance_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        try:
            self._port.persist_theme_choice(theme_id)
        except SettingsAppearancePortError as exc:
            self._sink.apply_selected_theme_visual(previous)
            patch = AppearanceStatePatch(
                error=SettingsErrorInfo(
                    code=exc.code,
                    message=exc.message,
                    recoverable=exc.recoverable,
                ),
                has_error_update=True,
            )
            self._state = merge_appearance_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        self._state = replace(self._state, selected_theme_id=theme_id, error=None)
        self._sink.apply_patch(
            AppearanceStatePatch(
                selected_theme_id=theme_id,
                error=None,
                has_error_update=True,
            )
        )
        if self._on_theme_choice_committed is not None:
            self._on_theme_choice_committed(theme_id)
