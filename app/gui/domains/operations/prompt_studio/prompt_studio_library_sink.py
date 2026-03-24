"""
PromptLibraryPanel — Spiegelung von :class:`PromptStudioListState` (Batch 2, gleiche Daten wie Slice 1).
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.prompt_studio_list import PromptStudioListState


class PromptStudioLibrarySink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def apply_full_state(self, state: PromptStudioListState, prompt_models: tuple[Any, ...] = ()) -> None:
        self._panel.apply_prompt_library_state(state, prompt_models)
