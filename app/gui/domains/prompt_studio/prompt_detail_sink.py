"""
PromptDetailSink — PromptInspectorPanel aus :class:`PromptStudioDetailState` (Slice 2).
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.prompt_studio_detail import PromptStudioDetailState


class PromptDetailSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
        self._panel.apply_prompt_detail_state(state)
