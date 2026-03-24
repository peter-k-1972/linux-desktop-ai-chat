"""Settings-Data-Contracts (Qt-frei)."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.settings_data import (
    DataSettingsPatch,
    DataSettingsState,
    DataSettingsWritePatch,
    LoadDataSettingsCommand,
    RAG_SPACE_IDS,
    SetRagTopKCommand,
    SettingsDataPortError,
    merge_data_state,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


def test_merge_prompt_directory_with_flag() -> None:
    base = DataSettingsState(
        rag_enabled=False,
        rag_space="default",
        rag_top_k=5,
        self_improving_enabled=False,
        prompt_storage_type="database",
        prompt_directory="/old",
        prompt_confirm_delete=True,
        error=None,
    )
    patch = DataSettingsPatch(prompt_directory="/new", has_prompt_directory_update=True)
    m = merge_data_state(base, patch)
    assert m.prompt_directory == "/new"


def test_merge_prompt_directory_without_flag_unchanged() -> None:
    base = DataSettingsState(
        rag_enabled=False,
        rag_space="default",
        rag_top_k=5,
        self_improving_enabled=False,
        prompt_storage_type="database",
        prompt_directory="/old",
        prompt_confirm_delete=True,
        error=None,
    )
    patch = DataSettingsPatch(prompt_directory="/ignored", has_prompt_directory_update=False)
    m = merge_data_state(base, patch)
    assert m.prompt_directory == "/old"


def test_merge_error_flag() -> None:
    base = DataSettingsState(
        rag_enabled=True,
        rag_space="default",
        rag_top_k=5,
        self_improving_enabled=False,
        prompt_storage_type="database",
        prompt_directory="",
        prompt_confirm_delete=True,
        error=None,
    )
    err = SettingsErrorInfo(code="x", message="m")
    m = merge_data_state(base, DataSettingsPatch(error=err, has_error_update=True))
    assert m.error == err


def test_write_patch_asdict() -> None:
    w = DataSettingsWritePatch(rag_enabled=True, prompt_directory_set=True, prompt_directory="/p")
    d = asdict(w)
    assert d["rag_enabled"] is True
    assert d["prompt_directory_set"] is True


def test_rag_space_ids_contains_default() -> None:
    assert "default" in RAG_SPACE_IDS


def test_commands_frozen() -> None:
    assert SetRagTopKCommand(7).top_k == 7
    assert isinstance(LoadDataSettingsCommand(), LoadDataSettingsCommand)


def test_port_error_attrs() -> None:
    exc = SettingsDataPortError("c", "m", recoverable=False)
    assert exc.code == "c"
    assert not exc.recoverable
