"""Smoke: Batch 5 — Prompt Studio Test Lab read wiring."""

from __future__ import annotations


def test_prompt_studio_batch5_modules_import() -> None:
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.prompt_studio_test_lab_presenter import PromptStudioTestLabPresenter
    from app.gui.domains.operations.prompt_studio.prompt_studio_test_lab_sink import PromptStudioTestLabSink
    from app.ui_contracts.workspaces import prompt_studio_test_lab as contracts

    assert hasattr(PromptStudioPort, "load_prompt_test_lab_prompts")
    assert PromptStudioTestLabPresenter.__name__ == "PromptStudioTestLabPresenter"
    assert PromptStudioTestLabSink.__name__ == "PromptStudioTestLabSink"
    assert hasattr(contracts, "LoadPromptTestLabModelsCommand")
