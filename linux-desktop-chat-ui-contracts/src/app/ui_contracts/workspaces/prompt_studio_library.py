"""
Prompt Studio — Library-Panel (Batch 2 Lesen, Batch 7 Delete, Batch 8 version_count).

Nutzt dieselbe Projektion wie die zentrale Prompt-Liste (Slice 1): dieselben DTOs/Commands/States fürs Lesen.

Auf dem injizierten Port-Pfad setzt der Adapter ``version_count`` (über ``PromptListEntryDto`` /
``PromptLibraryRowDto``) für jede Zeile; das Library-Panel nutzt diesen Wert und ruft dafür kein
``count_versions`` auf dem Hauptpfad auf.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ui_contracts.workspaces.prompt_studio_list import (
    LoadPromptStudioListCommand as LoadPromptLibraryCommand,
    PromptListEntryDto as PromptLibraryRowDto,
    PromptStudioListState as PromptLibraryState,
    prompt_studio_list_loading_state as prompt_library_loading_state,
)


@dataclass(frozen=True, slots=True)
class DeletePromptLibraryCommand:
    prompt_id: int
    project_id: int | None
    filter_text: str = ""


@dataclass(frozen=True, slots=True)
class PromptLibraryMutationResult:
    ok: bool
    error_message: str | None = None


__all__ = (
    "DeletePromptLibraryCommand",
    "LoadPromptLibraryCommand",
    "PromptLibraryMutationResult",
    "PromptLibraryRowDto",
    "PromptLibraryState",
    "prompt_library_loading_state",
)
