"""
SettingsDataPresenter — Data/RAG/Prompt-Speicher zwischen Port und Sink.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import SettingsDataUiSink
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo
from app.ui_contracts.workspaces.settings_data import (
    DataCommand,
    DataSettingsPatch,
    DataSettingsState,
    DataSettingsWritePatch,
    LoadDataSettingsCommand,
    RAG_SPACE_IDS,
    SetPromptConfirmDeleteCommand,
    SetPromptDirectoryCommand,
    SetPromptStorageTypeCommand,
    SetRagEnabledCommand,
    SetRagSpaceCommand,
    SetRagTopKCommand,
    SetSelfImprovingEnabledCommand,
    SettingsDataPortError,
    merge_data_state,
)

_RAG_TOP_K_MIN = 1
_RAG_TOP_K_MAX = 20

if TYPE_CHECKING:
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsDataPresenter(BasePresenter):
    def __init__(
        self,
        sink: SettingsDataUiSink,
        port: SettingsOperationsPort | None = None,
    ) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._state = DataSettingsState(
            rag_enabled=False,
            rag_space="default",
            rag_top_k=5,
            self_improving_enabled=False,
            prompt_storage_type="database",
            prompt_directory="",
            prompt_confirm_delete=True,
            error=None,
        )

    @property
    def state(self) -> DataSettingsState:
        return self._state

    @property
    def port(self) -> SettingsOperationsPort | None:
        return self._port

    def handle_command(self, command: DataCommand) -> None:
        if self._port is None:
            self._sink.apply_patch(
                DataSettingsPatch(
                    error=SettingsErrorInfo(
                        code="backend_not_wired",
                        message="SettingsOperationsPort ist nicht injiziert.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
            )
            return

        if isinstance(command, LoadDataSettingsCommand):
            self._state = self._port.load_data_settings_state()
            self._sink.apply_full_state(self._state)
            return

        if isinstance(command, SetRagEnabledCommand):
            self._persist_and_reload(DataSettingsWritePatch(rag_enabled=command.enabled))
            return

        if isinstance(command, SetRagSpaceCommand):
            if command.space_id not in RAG_SPACE_IDS:
                patch = DataSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_rag_space",
                        message=f"Unbekannter RAG-Space: {command.space_id!r}",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_data_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(DataSettingsWritePatch(rag_space=command.space_id))
            return

        if isinstance(command, SetRagTopKCommand):
            if command.top_k < _RAG_TOP_K_MIN or command.top_k > _RAG_TOP_K_MAX:
                patch = DataSettingsPatch(
                    error=SettingsErrorInfo(
                        code="invalid_rag_top_k",
                        message=f"RAG Top-K muss zwischen {_RAG_TOP_K_MIN} und {_RAG_TOP_K_MAX} liegen.",
                        recoverable=True,
                    ),
                    has_error_update=True,
                )
                self._state = merge_data_state(self._state, patch)
                self._sink.apply_patch(patch)
                return
            self._persist_and_reload(DataSettingsWritePatch(rag_top_k=command.top_k))
            return

        if isinstance(command, SetSelfImprovingEnabledCommand):
            self._persist_and_reload(DataSettingsWritePatch(self_improving_enabled=command.enabled))
            return

        if isinstance(command, SetPromptStorageTypeCommand):
            self._persist_and_reload(DataSettingsWritePatch(prompt_storage_type=command.storage))
            return

        if isinstance(command, SetPromptDirectoryCommand):
            path = command.directory.strip()
            self._persist_and_reload(
                DataSettingsWritePatch(prompt_directory=path, prompt_directory_set=True),
            )
            return

        if isinstance(command, SetPromptConfirmDeleteCommand):
            self._persist_and_reload(DataSettingsWritePatch(prompt_confirm_delete=command.enabled))
            return

    def _persist_and_reload(self, write: DataSettingsWritePatch) -> None:
        assert self._port is not None
        try:
            self._port.persist_data_settings(write)
        except SettingsDataPortError as exc:
            patch = DataSettingsPatch(
                error=SettingsErrorInfo(
                    code=exc.code,
                    message=exc.message,
                    recoverable=exc.recoverable,
                ),
                has_error_update=True,
            )
            self._state = merge_data_state(self._state, patch)
            self._sink.apply_patch(patch)
            return

        self._state = self._port.load_data_settings_state()
        self._sink.apply_full_state(self._state)
