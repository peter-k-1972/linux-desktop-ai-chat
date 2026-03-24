"""SettingsDataPresenter — Qt-frei."""

from __future__ import annotations

from app.ui_application.presenters.settings_data_presenter import SettingsDataPresenter
from app.ui_contracts.workspaces.settings_data import (
    DataSettingsState,
    DataSettingsWritePatch,
    LoadDataSettingsCommand,
    SetPromptDirectoryCommand,
    SetRagTopKCommand,
    SetRagSpaceCommand,
    SettingsDataPortError,
)


class _RecordingSink:
    def __init__(self) -> None:
        self.full: list[DataSettingsState] = []
        self.patches: list = []

    def apply_full_state(self, state: DataSettingsState) -> None:
        self.full.append(state)

    def apply_patch(self, patch) -> None:
        self.patches.append(patch)


class _FakePort:
    def __init__(self) -> None:
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
        self.writes: list[DataSettingsWritePatch] = []
        self.fail_next = False

    def load_data_settings_state(self) -> DataSettingsState:
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

    def persist_data_settings(self, write: DataSettingsWritePatch) -> None:
        self.writes.append(write)
        if self.fail_next:
            self.fail_next = False
            raise SettingsDataPortError("persist_failed", "nope", recoverable=True)
        if write.rag_enabled is not None:
            self._state = DataSettingsState(
                rag_enabled=write.rag_enabled,
                rag_space=self._state.rag_space,
                rag_top_k=self._state.rag_top_k,
                self_improving_enabled=self._state.self_improving_enabled,
                prompt_storage_type=self._state.prompt_storage_type,
                prompt_directory=self._state.prompt_directory,
                prompt_confirm_delete=self._state.prompt_confirm_delete,
                error=None,
            )
        if write.rag_space is not None:
            self._state = DataSettingsState(
                rag_enabled=self._state.rag_enabled,
                rag_space=write.rag_space,
                rag_top_k=self._state.rag_top_k,
                self_improving_enabled=self._state.self_improving_enabled,
                prompt_storage_type=self._state.prompt_storage_type,
                prompt_directory=self._state.prompt_directory,
                prompt_confirm_delete=self._state.prompt_confirm_delete,
                error=None,
            )
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


def test_load_full_state() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    assert len(sink.full) == 1
    assert sink.full[0].rag_space == "default"


def test_set_rag_space() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    p.handle_command(SetRagSpaceCommand("code"))
    assert any(w.rag_space == "code" for w in port.writes)
    assert sink.full[-1].rag_space == "code"


def test_invalid_rag_space_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetRagSpaceCommand("not_a_space"))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_rag_space"
        for patch in sink.patches
    )


def test_invalid_top_k_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    sink.patches.clear()
    p.handle_command(SetRagTopKCommand(99))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "invalid_rag_top_k"
        for patch in sink.patches
    )


def test_prompt_directory_trimmed() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    p.handle_command(SetPromptDirectoryCommand("  /tmp/x  "))
    assert any(
        w.prompt_directory_set and w.prompt_directory == "/tmp/x" for w in port.writes
    )


def test_persist_failure_error() -> None:
    sink = _RecordingSink()
    port = _FakePort()
    port.fail_next = True
    p = SettingsDataPresenter(sink, port)
    p.handle_command(LoadDataSettingsCommand())
    p.handle_command(SetRagSpaceCommand("notes"))
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "persist_failed"
        for patch in sink.patches
    )


def test_no_port_backend_not_wired() -> None:
    sink = _RecordingSink()
    p = SettingsDataPresenter(sink, None)
    p.handle_command(LoadDataSettingsCommand())
    assert any(
        patch.has_error_update and patch.error and patch.error.code == "backend_not_wired"
        for patch in sink.patches
    )
