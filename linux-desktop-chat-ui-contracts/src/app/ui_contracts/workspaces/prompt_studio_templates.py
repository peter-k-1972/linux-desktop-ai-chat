"""
Prompt Studio — Templates-Panel (Batch 2 Lesen, Batch 7 Mutationen, Qt-frei).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.common.errors import SettingsErrorInfo

PromptTemplatesPhase = Literal["loading", "ready", "empty", "error"]


@dataclass(frozen=True, slots=True)
class PromptTemplateRowDto:
    """Korrelation Template-Zeile ↔ Modell im Adapter (nur ID nötig für UI-Widgets)."""

    prompt_id: int


@dataclass(frozen=True, slots=True)
class PromptTemplatesState:
    phase: PromptTemplatesPhase
    rows: tuple[PromptTemplateRowDto, ...] = ()
    error: SettingsErrorInfo | None = None
    empty_hint: str | None = None


@dataclass(frozen=True, slots=True)
class LoadPromptTemplatesCommand:
    project_id: int | None
    filter_text: str = ""


def prompt_templates_loading_state() -> PromptTemplatesState:
    return PromptTemplatesState(phase="loading")


@dataclass(frozen=True, slots=True)
class CreatePromptTemplateCommand:
    title: str
    description: str
    content: str
    scope: str
    project_id: int | None


@dataclass(frozen=True, slots=True)
class UpdatePromptTemplateCommand:
    template_id: int
    title: str
    description: str
    content: str


@dataclass(frozen=True, slots=True)
class CopyPromptTemplateCommand:
    source_template_id: int
    scope: str
    project_id: int | None


@dataclass(frozen=True, slots=True)
class DeletePromptTemplateCommand:
    template_id: int


@dataclass(frozen=True, slots=True)
class PromptTemplateMutationResult:
    ok: bool
    error_message: str | None = None
