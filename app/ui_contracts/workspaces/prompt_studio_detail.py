"""
Prompt Studio — Prompt-Detail / Inspector (Qt-frei, Slice 2 read-only).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PromptStudioDetailPhase = Literal["loading", "ready", "error"]


@dataclass(frozen=True, slots=True)
class PromptDetailDto:
    """Kompaktes Prompt-Detail für die UI (serialisierbar)."""

    prompt_id: str
    name: str
    content: str
    version_count: int
    last_modified: str | None


@dataclass(frozen=True, slots=True)
class PromptStudioDetailState:
    phase: PromptStudioDetailPhase
    detail: PromptDetailDto | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class LoadPromptDetailCommand:
    """Leeres ``prompt_id`` → kein ausgewählter Prompt (Inspector leeren)."""

    prompt_id: str
    project_id: str | None = None


def prompt_studio_detail_loading_state() -> PromptStudioDetailState:
    return PromptStudioDetailState(phase="loading", detail=None, error_message=None)
