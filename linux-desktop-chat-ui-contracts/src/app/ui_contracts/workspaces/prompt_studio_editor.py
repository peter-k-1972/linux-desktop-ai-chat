"""
Prompt Studio — Editor-Persistenz (Batch 3, Qt-frei).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

PromptEditorSavePhase = Literal["idle", "saving", "success", "error"]


@dataclass(frozen=True, slots=True)
class PromptStudioPromptSnapshotDto:
    """Minimaler Snapshot zur Rekonstruktion von ``Prompt`` im GUI nach Save/Open."""

    prompt_id: int
    title: str
    content: str
    description: str
    category: str
    scope: str
    project_id: int | None
    prompt_type: str
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SavePromptVersionEditorCommand:
    """Neue Version wie ``PromptService.save_version`` (operations ``prompt_editor_panel``)."""

    prompt_id: int
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class UpdatePromptMetadataEditorCommand:
    """Voll-Update wie ``PromptService.update`` (``panels/editor_panel``)."""

    prompt_id: int
    title: str
    content: str
    description: str
    category: str
    scope: str
    project_id: int | None


PromptEditorPersistCommand = Union[SavePromptVersionEditorCommand, UpdatePromptMetadataEditorCommand]


@dataclass(frozen=True, slots=True)
class PromptEditorSaveResultState:
    phase: PromptEditorSavePhase
    error_message: str | None = None
    snapshot: PromptStudioPromptSnapshotDto | None = None


def prompt_editor_save_saving_state() -> PromptEditorSaveResultState:
    return PromptEditorSaveResultState(phase="saving")


def prompt_editor_save_idle_state() -> PromptEditorSaveResultState:
    return PromptEditorSaveResultState(phase="idle")
