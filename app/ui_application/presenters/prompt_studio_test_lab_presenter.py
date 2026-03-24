"""
PromptStudioTestLabPresenter — Test-Lab: Lesen (Batch 5) + Run/Stream (Batch 6).
"""

from __future__ import annotations

from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import PromptStudioTestLabUiSink
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabModelsCommand,
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabRunPatch,
    RunPromptTestLabCommand,
)


class PromptStudioTestLabPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioTestLabUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_load_prompts(self, command: LoadPromptTestLabPromptsCommand) -> None:
        state = self._port.load_prompt_test_lab_prompts(command)
        self._sink.apply_prompts_state(state)

    def handle_load_versions(self, command: LoadPromptTestLabVersionsCommand) -> None:
        state = self._port.load_prompt_test_lab_versions(command)
        self._sink.apply_versions_state(state)

    async def handle_load_models_async(self) -> None:
        state = await self._port.load_prompt_test_lab_models(LoadPromptTestLabModelsCommand())
        self._sink.apply_models_state(state)

    async def handle_run_async(self, command: RunPromptTestLabCommand) -> None:
        self._sink.apply_run_patch(
            PromptTestLabRunPatch(
                replace_full_text="Wird ausgeführt…",
                phase="running",
                run_button_enabled=False,
            ),
        )
        full = ""
        try:
            async for chunk in self._port.stream_prompt_test_lab_run(command):
                if chunk.stream_error:
                    full = f"Fehler: {chunk.stream_error}"
                    self._sink.apply_run_patch(
                        PromptTestLabRunPatch(
                            replace_full_text=full,
                            phase="error",
                            run_button_enabled=True,
                            scroll_to_max=True,
                        ),
                    )
                    return
                if chunk.content_delta:
                    full += chunk.content_delta
                    self._sink.apply_run_patch(
                        PromptTestLabRunPatch(
                            replace_full_text=full,
                            phase="running",
                            scroll_to_max=True,
                        ),
                    )
            if not full:
                self._sink.apply_run_patch(
                    PromptTestLabRunPatch(
                        replace_full_text="(Keine Ausgabe)",
                        phase="success",
                        run_button_enabled=True,
                        scroll_to_max=True,
                    ),
                )
            else:
                self._sink.apply_run_patch(
                    PromptTestLabRunPatch(
                        phase="success",
                        run_button_enabled=True,
                        scroll_to_max=True,
                    ),
                )
        except Exception as e:
            self._sink.apply_run_patch(
                PromptTestLabRunPatch(
                    replace_full_text=f"Fehler: {e!s}",
                    phase="error",
                    run_button_enabled=True,
                    scroll_to_max=True,
                ),
            )
