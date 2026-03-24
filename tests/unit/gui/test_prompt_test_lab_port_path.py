"""PromptTestLab — injizierter Presenter-Pfad (Batch 5 read)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_test_lab import PromptTestLab
from app.gui.domains.operations.prompt_studio.prompt_studio_test_lab_sink import PromptStudioTestLabSink
from app.ui_application.presenters.prompt_studio_test_lab_presenter import PromptStudioTestLabPresenter
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabModelsState,
    PromptTestLabPromptRowDto,
    PromptTestLabPromptsState,
    PromptTestLabVersionRowDto,
    PromptTestLabVersionsState,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


async def test_load_prompts_async_delegates_to_presenter(qapp: QApplication, monkeypatch) -> None:
    calls: list[LoadPromptTestLabPromptsCommand] = []

    class _P:
        def load_prompt_test_lab_prompts(self, c: LoadPromptTestLabPromptsCommand) -> PromptTestLabPromptsState:
            calls.append(c)
            return PromptTestLabPromptsState(phase="ready", rows=())

        def load_prompt_test_lab_versions(self, c: LoadPromptTestLabVersionsCommand) -> PromptTestLabVersionsState:
            return PromptTestLabVersionsState(phase="ready", prompt_id=c.prompt_id, rows=())

        async def load_prompt_test_lab_models(self, c) -> PromptTestLabModelsState:  # noqa: ANN001
            return PromptTestLabModelsState(phase="ready", models=())

    lab = PromptTestLab()
    sink = PromptStudioTestLabSink(lab)
    pr = PromptStudioTestLabPresenter(sink, _P())  # type: ignore[arg-type]
    lab.attach_test_lab_presenter(pr)

    monkeypatch.setattr(
        "app.gui.domains.operations.prompt_studio.panels.prompt_test_lab.PromptTestLab._active_project_id",
        lambda self: 42,
    )

    await lab._load_prompts_async()
    assert len(calls) == 1
    assert calls[0].project_id == 42


async def test_load_models_async_delegates_to_presenter(qapp: QApplication) -> None:
    port = MagicMock()
    port.load_prompt_test_lab_prompts.return_value = PromptTestLabPromptsState(phase="ready", rows=())
    port.load_prompt_test_lab_versions.return_value = PromptTestLabVersionsState(phase="ready", prompt_id=0, rows=())
    port.load_prompt_test_lab_models = AsyncMock(
        return_value=PromptTestLabModelsState(phase="ready", models=("x",), default_model="x"),
    )

    lab = PromptTestLab()
    sink = PromptStudioTestLabSink(lab)
    pr = PromptStudioTestLabPresenter(sink, port)
    lab.attach_test_lab_presenter(pr)

    await lab._load_models_async()
    port.load_prompt_test_lab_models.assert_awaited_once()
    assert lab._model_combo.itemText(0) == "x"
