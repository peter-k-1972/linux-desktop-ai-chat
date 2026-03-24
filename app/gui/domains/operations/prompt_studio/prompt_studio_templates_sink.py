"""
PromptTemplatesPanel — Spiegelung von :class:`PromptTemplatesState` (Batch 2).
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.prompt_studio_templates import PromptTemplatesState


class PromptStudioTemplatesSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def apply_templates_state(
        self,
        state: PromptTemplatesState,
        template_models: tuple[Any, ...] = (),
    ) -> None:
        self._panel.apply_prompt_templates_state(state, template_models)
