"""
Prompt Studio — Test Lab (Batch 5 read, Batch 6 run/stream).

Qt-frei, ORM-frei; serialisierbare DTOs/Zustände.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PromptTestLabPromptsPhase = Literal["ready", "error"]
PromptTestLabVersionsPhase = Literal["ready", "error"]
PromptTestLabModelsPhase = Literal["ready", "error", "unreachable"]


@dataclass(frozen=True, slots=True)
class PromptTestLabPromptRowDto:
    prompt_id: int
    display_title: str


@dataclass(frozen=True, slots=True)
class PromptTestLabPromptsState:
    phase: PromptTestLabPromptsPhase
    rows: tuple[PromptTestLabPromptRowDto, ...] = ()
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class PromptTestLabVersionRowDto:
    version: int
    display_label: str
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class PromptTestLabVersionsState:
    phase: PromptTestLabVersionsPhase
    prompt_id: int
    rows: tuple[PromptTestLabVersionRowDto, ...] = ()
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class PromptTestLabModelsState:
    phase: PromptTestLabModelsPhase
    models: tuple[str, ...] = ()
    default_model: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class LoadPromptTestLabPromptsCommand:
    project_id: int | None


@dataclass(frozen=True, slots=True)
class LoadPromptTestLabVersionsCommand:
    prompt_id: int


@dataclass(frozen=True, slots=True)
class LoadPromptTestLabModelsCommand:
    """Leeres Kommando — Lesen aller Modellnamen für die Test-Lab-Combo."""

    pass


# --- Batch 6: Run / Chat-Stream (vorbereitete Messages, kein Qt) ---

PromptTestLabRunPhase = Literal["running", "success", "error"]


@dataclass(frozen=True, slots=True)
class RunPromptTestLabCommand:
    """Chat-Aufruf wie bisher im Widget: System = aufbereiteter Prompt, User = Eingabetext."""

    model_name: str
    system_prompt_text: str
    user_message_text: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True, slots=True)
class PromptTestLabStreamChunkDto:
    """Ein normalisiertes Stream-Chunk aus dem Chat-Service."""

    content_delta: str
    stream_error: str | None = None


@dataclass(frozen=True, slots=True)
class PromptTestLabRunPatch:
    """Inkrementelles UI-Update für die Ergebnisansicht (nur Spiegelung)."""

    replace_full_text: str | None = None
    phase: PromptTestLabRunPhase | None = None
    run_button_enabled: bool | None = None
    scroll_to_max: bool = False


@dataclass(frozen=True, slots=True)
class PromptTestLabRunState:
    """Terminalzustand nach Lauf (optional für Tests/Logs)."""

    phase: PromptTestLabRunPhase
    output_text: str
    run_button_enabled: bool
