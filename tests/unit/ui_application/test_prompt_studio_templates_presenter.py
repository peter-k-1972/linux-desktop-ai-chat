"""PromptStudioTemplatesPresenter — Batch 2."""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.prompt_studio_templates_presenter import PromptStudioTemplatesPresenter
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CopyPromptTemplateCommand,
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    LoadPromptTemplatesCommand,
    PromptTemplateMutationResult,
    PromptTemplateRowDto,
    PromptTemplatesState,
    UpdatePromptTemplateCommand,
    prompt_templates_loading_state,
)
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[PromptTemplatesState, tuple[Any, ...]]] = []

    def apply_templates_state(
        self,
        state: PromptTemplatesState,
        template_models: tuple[Any, ...] = (),
    ) -> None:
        self.calls.append((state, template_models))


class _Port:
    def __init__(self, view: PromptTemplatesState, models: tuple[Any, ...]) -> None:
        self._view = view
        self._models = models
        self.calls = 0
        self.last_create: CreatePromptTemplateCommand | None = None

    def load_prompt_templates(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptTemplatesState:
        self.calls += 1
        return self._view

    def create_prompt_template(self, command: CreatePromptTemplateCommand) -> PromptTemplateMutationResult:
        self.last_create = command
        return PromptTemplateMutationResult(ok=True)

    def update_prompt_template(self, command: UpdatePromptTemplateCommand) -> PromptTemplateMutationResult:
        del command
        return PromptTemplateMutationResult(ok=True)

    def copy_template_to_user_prompt(self, command: CopyPromptTemplateCommand) -> PromptStudioWorkspaceOpResult:
        del command
        return PromptStudioWorkspaceOpResult(ok=True)

    def delete_prompt_template(self, command: DeletePromptTemplateCommand) -> PromptTemplateMutationResult:
        del command
        return PromptTemplateMutationResult(ok=True)

    @property
    def last_prompt_template_models(self) -> tuple[Any, ...]:
        return self._models


def test_templates_presenter_create_refreshes() -> None:
    ready = PromptTemplatesState(phase="ready", rows=(PromptTemplateRowDto(1),))
    sink = _Sink()
    port = _Port(ready, ("m",))
    p = PromptStudioTemplatesPresenter(sink, port)
    loads_before = port.calls
    cmd = CreatePromptTemplateCommand("t", "", "", "global", None)
    r = p.handle_create_template(cmd, refresh_project_id=2, refresh_filter_text="f")
    assert r.ok
    assert port.last_create == cmd
    assert port.calls == loads_before + 1


def test_templates_presenter_applies_models() -> None:
    ready = PromptTemplatesState(phase="ready", rows=(PromptTemplateRowDto(1),))
    models = ("m",)
    sink = _Sink()
    port = _Port(ready, models)
    p = PromptStudioTemplatesPresenter(sink, port)
    p.handle_command(LoadPromptTemplatesCommand(2, "f"))
    assert len(sink.calls) == 2
    assert sink.calls[0][0].phase == prompt_templates_loading_state().phase
    assert sink.calls[1][0].phase == "ready"
    assert sink.calls[1][1] == models
    assert port.calls == 1
