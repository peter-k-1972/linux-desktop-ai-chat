"""
Settings — ModelSettingsPanel (Studio): Routing, Assistant-Modell, skalare LLM-Flags.

Qt-frei. Nur Felder, die das Panel persistiert (Slice Model-Routing-Studio).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


@dataclass(frozen=True, slots=True)
class ModelRoutingStudioState:
    model: str
    auto_routing: bool
    cloud_escalation: bool
    cloud_via_local: bool
    web_search: bool
    overkill_mode: bool
    default_role: str
    temperature: float
    top_p: float
    max_tokens: int
    llm_timeout_seconds: int
    retry_without_thinking: bool
    chat_streaming_enabled: bool
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class ModelRoutingStudioWritePatch:
    """Nur gesetzte Felder schreiben; ein ``save()`` im Adapter pro Aufruf (wenn nicht leer)."""

    model: str | None = None
    auto_routing: bool | None = None
    cloud_escalation: bool | None = None
    cloud_via_local: bool | None = None
    web_search: bool | None = None
    overkill_mode: bool | None = None
    default_role: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    llm_timeout_seconds: int | None = None
    retry_without_thinking: bool | None = None
    chat_streaming_enabled: bool | None = None


@dataclass(frozen=True, slots=True)
class LoadModelRoutingStudioCommand:
    """Zustand aus dem Port laden und in den Sink spiegeln."""


@dataclass(frozen=True, slots=True)
class ApplyModelRoutingStudioPatchCommand:
    patch: ModelRoutingStudioWritePatch


ModelRoutingStudioCommand = Union[LoadModelRoutingStudioCommand, ApplyModelRoutingStudioPatchCommand]


class SettingsModelRoutingPortError(Exception):
    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
