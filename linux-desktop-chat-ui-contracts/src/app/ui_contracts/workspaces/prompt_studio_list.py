"""
Prompt Studio — Prompt-Liste (Qt-frei, Slice 1 read-only).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.common.errors import SettingsErrorInfo

PromptStudioListPhase = Literal["loading", "ready", "empty", "error"]


@dataclass(frozen=True, slots=True)
class PromptListEntryDto:
    """Eine Zeile in der Prompt-Liste."""

    prompt_id: int
    list_section: Literal["project", "global"]
    version_count: int = 1


@dataclass(frozen=True, slots=True)
class PromptStudioListState:
    phase: PromptStudioListPhase
    rows: tuple[PromptListEntryDto, ...] = ()
    error: SettingsErrorInfo | None = None
    empty_hint: str | None = None


@dataclass(frozen=True, slots=True)
class LoadPromptStudioListCommand:
    project_id: int | None
    filter_text: str = ""


def prompt_studio_list_loading_state() -> PromptStudioListState:
    return PromptStudioListState(phase="loading")
