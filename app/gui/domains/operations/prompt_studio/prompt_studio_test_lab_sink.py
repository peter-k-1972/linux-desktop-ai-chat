"""
PromptStudioTestLabSink — Test-Lab-Combos aus Contract-Zuständen (Batch 5, read-only).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    PromptTestLabModelsState,
    PromptTestLabPromptsState,
    PromptTestLabRunPatch,
    PromptTestLabVersionsState,
)

if TYPE_CHECKING:
    from app.gui.domains.operations.prompt_studio.panels.prompt_test_lab import PromptTestLab


class PromptStudioTestLabSink:
    def __init__(self, panel: PromptTestLab) -> None:
        self._panel = panel

    def apply_prompts_state(self, state: PromptTestLabPromptsState) -> None:
        self._panel.mirror_test_lab_prompts_state(state)

    def apply_versions_state(self, state: PromptTestLabVersionsState) -> None:
        self._panel.mirror_test_lab_versions_state(state)

    def apply_models_state(self, state: PromptTestLabModelsState) -> None:
        self._panel.mirror_test_lab_models_state(state)

    def apply_run_patch(self, patch: PromptTestLabRunPatch) -> None:
        self._panel.mirror_test_lab_run_patch(patch)
