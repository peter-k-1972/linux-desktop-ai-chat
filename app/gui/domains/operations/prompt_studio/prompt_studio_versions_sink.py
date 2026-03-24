"""
PromptVersionPanel — Spiegelung von :class:`PromptVersionPanelState` (Batch 2).
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.prompt_studio_versions import PromptVersionPanelState


class PromptStudioVersionsSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def apply_version_state(self, state: PromptVersionPanelState) -> None:
        self._panel.apply_prompt_version_panel_state(state)
