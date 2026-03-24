"""
Prompt Studio — Versionen-Panel Lesepfad (Batch 2, Qt-frei).

Batch 8: Im aktuellen UI gibt es im ``PromptVersionPanel`` keine separaten
Versions-Mutations-Aktionen (kein Anlegen/Löschen/Umbenennen von Versionen im Panel).
Die Auswahl einer Version erfolgt nur per Signal mit bereits geladenen Daten; Persistenz
läuft weiter über den Editor-Pfad (explizit out of scope für dieses Batch-Slice).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

PromptVersionPanelPhase = Literal["loading", "ready", "empty", "error"]


@dataclass(frozen=True, slots=True)
class PromptVersionRowDto:
    """Eine gespeicherte Prompt-Version (wie Service-``list_versions``-Dict, serialisierbar)."""

    version: int
    title: str
    content: str
    created_at_iso: str | None


@dataclass(frozen=True, slots=True)
class PromptVersionPanelState:
    phase: PromptVersionPanelPhase
    prompt_id: int | None = None
    rows: tuple[PromptVersionRowDto, ...] = ()
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class LoadPromptVersionsCommand:
    prompt_id: int


def prompt_versions_loading_state(prompt_id: int) -> PromptVersionPanelState:
    return PromptVersionPanelState(phase="loading", prompt_id=prompt_id)
