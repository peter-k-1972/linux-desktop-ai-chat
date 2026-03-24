"""
Settings — Legacy-Modal-Dialog (``SettingsDialog``), Qt-frei.

Ein atomarer Commit aller Felder, die der Modal-Dialog speichert (Parität zu
``save_and_close`` vor Port-Slice). Schreibpfad: Port → Adapter → ``AppSettings.save()``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LegacyModalThemeBucket = Literal["light", "dark"]
PromptStorageTypeModal = Literal["database", "directory"]


@dataclass(frozen=True, slots=True)
class SettingsLegacyModalCommit:
    """Snapshot der Widget-Werte beim Speichern (kein Teil-Patch — Dialog schreibt immer alles)."""

    model_id: str
    temperature: float
    max_tokens: int
    legacy_theme: LegacyModalThemeBucket
    think_mode: str
    auto_routing: bool
    cloud_escalation: bool
    cloud_via_local: bool
    overkill_mode: bool
    rag_enabled: bool
    rag_space: str
    rag_top_k: int
    self_improving_enabled: bool
    debug_panel_enabled: bool
    prompt_storage_type: PromptStorageTypeModal
    prompt_directory: str
    prompt_confirm_delete: bool
    ollama_api_key: str


class SettingsLegacyModalPortError(Exception):
    """Validierungs- oder Persistenzfehler für den Legacy-Settings-Modal."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
