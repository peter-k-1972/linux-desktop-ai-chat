"""
Settings — Data (RAG, Prompt-Speicherung), Qt-frei.

Slice 3: Spiegel der Felder aus ``DataSettingsPanel`` / AppSettings.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal, Union

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

PromptStorageType = Literal["database", "directory"]

RAG_SPACE_IDS: tuple[str, ...] = (
    "default",
    "documentation",
    "code",
    "notes",
    "projects",
)


@dataclass(frozen=True, slots=True)
class DataSettingsState:
    rag_enabled: bool
    rag_space: str
    rag_top_k: int
    self_improving_enabled: bool
    prompt_storage_type: PromptStorageType
    prompt_directory: str
    prompt_confirm_delete: bool
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class DataSettingsPatch:
    """Teilupdate für Sink; None bei Wertfeldern = unverändert (außer prompt_directory, siehe Flag)."""

    rag_enabled: bool | None = None
    rag_space: str | None = None
    rag_top_k: int | None = None
    self_improving_enabled: bool | None = None
    prompt_storage_type: PromptStorageType | None = None
    prompt_directory: str | None = None
    has_prompt_directory_update: bool = False
    prompt_confirm_delete: bool | None = None
    error: SettingsErrorInfo | None = None
    has_error_update: bool = False


@dataclass(frozen=True, slots=True)
class DataSettingsWritePatch:
    """Nur gesetzte Felder schreiben; ``prompt_directory=None`` = Feld überspringen, ``\"\"`` erlaubt."""

    rag_enabled: bool | None = None
    rag_space: str | None = None
    rag_top_k: int | None = None
    self_improving_enabled: bool | None = None
    prompt_storage_type: PromptStorageType | None = None
    prompt_directory: str | None = None
    prompt_directory_set: bool = False
    prompt_confirm_delete: bool | None = None


def merge_data_state(base: DataSettingsState, patch: DataSettingsPatch) -> DataSettingsState:
    rag_e = patch.rag_enabled if patch.rag_enabled is not None else base.rag_enabled
    space = patch.rag_space if patch.rag_space is not None else base.rag_space
    top_k = patch.rag_top_k if patch.rag_top_k is not None else base.rag_top_k
    si = patch.self_improving_enabled if patch.self_improving_enabled is not None else base.self_improving_enabled
    pst = patch.prompt_storage_type if patch.prompt_storage_type is not None else base.prompt_storage_type
    if patch.has_prompt_directory_update:
        pd = patch.prompt_directory if patch.prompt_directory is not None else ""
    else:
        pd = base.prompt_directory
    pcd = patch.prompt_confirm_delete if patch.prompt_confirm_delete is not None else base.prompt_confirm_delete
    err = patch.error if patch.has_error_update else base.error
    return replace(
        base,
        rag_enabled=rag_e,
        rag_space=space,
        rag_top_k=top_k,
        self_improving_enabled=si,
        prompt_storage_type=pst,
        prompt_directory=pd,
        prompt_confirm_delete=pcd,
        error=err,
    )


@dataclass(frozen=True, slots=True)
class LoadDataSettingsCommand:
    """Zustand aus dem Port laden."""


@dataclass(frozen=True, slots=True)
class SetRagEnabledCommand:
    enabled: bool


@dataclass(frozen=True, slots=True)
class SetRagSpaceCommand:
    space_id: str


@dataclass(frozen=True, slots=True)
class SetRagTopKCommand:
    top_k: int


@dataclass(frozen=True, slots=True)
class SetSelfImprovingEnabledCommand:
    enabled: bool


@dataclass(frozen=True, slots=True)
class SetPromptStorageTypeCommand:
    storage: PromptStorageType


@dataclass(frozen=True, slots=True)
class SetPromptDirectoryCommand:
    """Absoluter Pfad (kann leer sein); Trimmen im Presenter."""

    directory: str


@dataclass(frozen=True, slots=True)
class SetPromptConfirmDeleteCommand:
    enabled: bool


DataCommand = Union[
    LoadDataSettingsCommand,
    SetRagEnabledCommand,
    SetRagSpaceCommand,
    SetRagTopKCommand,
    SetSelfImprovingEnabledCommand,
    SetPromptStorageTypeCommand,
    SetPromptDirectoryCommand,
    SetPromptConfirmDeleteCommand,
]


class SettingsDataPortError(Exception):
    """Persistenz- oder Validierungsfehler Data-Settings."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
