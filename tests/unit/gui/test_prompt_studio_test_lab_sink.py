"""PromptStudioTestLabSink (Batch 5)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_test_lab import PromptTestLab
from app.gui.domains.operations.prompt_studio.prompt_studio_test_lab_sink import PromptStudioTestLabSink
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    PromptTestLabModelsState,
    PromptTestLabPromptRowDto,
    PromptTestLabPromptsState,
    PromptTestLabRunPatch,
    PromptTestLabVersionRowDto,
    PromptTestLabVersionsState,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_sink_mirrors_prompts_versions_models(qapp: QApplication) -> None:
    lab = PromptTestLab()
    sink = PromptStudioTestLabSink(lab)
    sink.apply_prompts_state(
        PromptTestLabPromptsState(
            phase="ready",
            rows=(PromptTestLabPromptRowDto(9, "Nine"),),
        ),
    )
    assert lab._prompt_combo.count() == 1
    assert lab._prompt_combo.itemData(0) == 9
    sink.apply_versions_state(
        PromptTestLabVersionsState(
            phase="ready",
            prompt_id=9,
            rows=(
                PromptTestLabVersionRowDto(1, "v1", "T", "CONTENT"),
            ),
        ),
    )
    assert lab._version_combo.count() == 1
    assert lab._version_combo.itemData(0).get("content") == "CONTENT"
    sink.apply_models_state(PromptTestLabModelsState(phase="ready", models=("llama",), default_model="llama"))
    assert lab._model_combo.count() == 1
    assert lab._model_combo.currentText() == "llama"


def test_sink_applies_run_patch(qapp: QApplication) -> None:
    lab = PromptTestLab()
    sink = PromptStudioTestLabSink(lab)
    sink.apply_run_patch(
        PromptTestLabRunPatch(replace_full_text="out", run_button_enabled=False, scroll_to_max=False),
    )
    assert lab._result_text.toPlainText() == "out"
    assert not lab._run_btn.isEnabled()
    sink.apply_run_patch(PromptTestLabRunPatch(run_button_enabled=True))
    assert lab._run_btn.isEnabled()
