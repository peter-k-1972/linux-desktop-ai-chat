"""PromptStudioTestLabPresenter (Batch 5)."""

from __future__ import annotations

from app.ui_application.presenters.prompt_studio_test_lab_presenter import PromptStudioTestLabPresenter
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabModelsCommand,
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabModelsState,
    PromptTestLabPromptRowDto,
    PromptTestLabPromptsState,
    PromptTestLabRunPatch,
    PromptTestLabStreamChunkDto,
    PromptTestLabVersionRowDto,
    PromptTestLabVersionsState,
    RunPromptTestLabCommand,
)


class _Sink:
    def __init__(self) -> None:
        self.prompts: PromptTestLabPromptsState | None = None
        self.versions: PromptTestLabVersionsState | None = None
        self.models: PromptTestLabModelsState | None = None
        self.run_patches: list[PromptTestLabRunPatch] = []

    def apply_prompts_state(self, state: PromptTestLabPromptsState) -> None:
        self.prompts = state

    def apply_versions_state(self, state: PromptTestLabVersionsState) -> None:
        self.versions = state

    def apply_models_state(self, state: PromptTestLabModelsState) -> None:
        self.models = state

    def apply_run_patch(self, patch: PromptTestLabRunPatch) -> None:
        self.run_patches.append(patch)


class _Port:
    def load_prompt_test_lab_prompts(self, command: LoadPromptTestLabPromptsCommand) -> PromptTestLabPromptsState:
        return PromptTestLabPromptsState(
            phase="ready",
            rows=(PromptTestLabPromptRowDto(1, "X"),),
        )

    def load_prompt_test_lab_versions(
        self,
        command: LoadPromptTestLabVersionsCommand,
    ) -> PromptTestLabVersionsState:
        return PromptTestLabVersionsState(
            phase="ready",
            prompt_id=command.prompt_id,
            rows=(PromptTestLabVersionRowDto(1, "v1", "t", "body"),),
        )

    async def load_prompt_test_lab_models(
        self,
        command: LoadPromptTestLabModelsCommand,
    ) -> PromptTestLabModelsState:
        del command
        return PromptTestLabModelsState(phase="ready", models=("m",), default_model="m")

    async def stream_prompt_test_lab_run(self, command):  # noqa: ANN001
        del command
        if False:
            yield PromptTestLabStreamChunkDto("", None)


def test_presenter_load_prompts_and_versions() -> None:
    sink = _Sink()
    pr = PromptStudioTestLabPresenter(sink, _Port())  # type: ignore[arg-type]
    pr.handle_load_prompts(LoadPromptTestLabPromptsCommand(2))
    assert sink.prompts is not None and sink.prompts.rows[0].display_title == "X"
    pr.handle_load_versions(LoadPromptTestLabVersionsCommand(1))
    assert sink.versions is not None and sink.versions.rows[0].content == "body"


async def test_presenter_load_models_async() -> None:
    sink = _Sink()
    pr = PromptStudioTestLabPresenter(sink, _Port())  # type: ignore[arg-type]
    await pr.handle_load_models_async()
    assert sink.models is not None and sink.models.models == ("m",)


async def test_presenter_run_streams_and_finishes() -> None:
    class _PStream(_Port):
        async def stream_prompt_test_lab_run(self, command):  # noqa: ANN001
            yield PromptTestLabStreamChunkDto("hi", None)

    sink = _Sink()
    pr = PromptStudioTestLabPresenter(sink, _PStream())  # type: ignore[arg-type]
    await pr.handle_run_async(
        RunPromptTestLabCommand("m", "sys", "user", 0.5, 512),
    )
    assert sink.run_patches[0].replace_full_text == "Wird ausgeführt…"
    assert any(p.replace_full_text == "hi" for p in sink.run_patches)
    assert sink.run_patches[-1].phase == "success"
    assert sink.run_patches[-1].run_button_enabled is True


async def test_presenter_run_stream_error() -> None:
    class _PErr(_Port):
        async def stream_prompt_test_lab_run(self, command):  # noqa: ANN001
            yield PromptTestLabStreamChunkDto("", stream_error="boom")

    sink = _Sink()
    pr = PromptStudioTestLabPresenter(sink, _PErr())  # type: ignore[arg-type]
    await pr.handle_run_async(
        RunPromptTestLabCommand("m", "s", "u", 0.1, 10),
    )
    assert any(p.replace_full_text == "Fehler: boom" for p in sink.run_patches)
    assert sink.run_patches[-1].phase == "error"
