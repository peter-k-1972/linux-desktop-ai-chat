"""PromptTemplatesPanel — Port-Pfad (Batch 2)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from app.gui.domains.operations.prompt_studio.panels.prompt_templates_panel import PromptTemplatesPanel
from app.prompts.prompt_models import Prompt
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    PromptTemplateMutationResult,
    PromptTemplateRowDto,
    PromptTemplatesState,
    UpdatePromptTemplateCommand,
)
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


@dataclass
class _Tpl:
    id: int = 7
    title: str = "T"
    description: str = ""
    content: str = ""


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0
        self._models = (_Tpl(),)
        self.deleted_ids: list[int] = []

    def load_prompt_templates(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptTemplatesState:
        self.calls += 1
        del filter_text
        if project_id is None:
            return PromptTemplatesState(phase="empty", empty_hint="x")
        return PromptTemplatesState(phase="ready", rows=(PromptTemplateRowDto(7),))

    def create_prompt_template(self, command: CreatePromptTemplateCommand) -> PromptTemplateMutationResult:
        del command
        return PromptTemplateMutationResult(ok=True)

    def update_prompt_template(self, command: UpdatePromptTemplateCommand) -> PromptTemplateMutationResult:
        del command
        return PromptTemplateMutationResult(ok=True)

    def copy_template_to_user_prompt(self, command) -> PromptStudioWorkspaceOpResult:  # noqa: ANN001
        del command
        return PromptStudioWorkspaceOpResult(ok=True)

    def delete_prompt_template(self, command: DeletePromptTemplateCommand) -> PromptTemplateMutationResult:
        self.deleted_ids.append(command.template_id)
        return PromptTemplateMutationResult(ok=True)

    @property
    def last_prompt_template_models(self) -> tuple:
        return self._models


def test_templates_port_path(qapp) -> None:
    port = _FakePort()
    p = PromptTemplatesPanel(prompt_studio_port=port)
    p._current_project_id = 1
    p.refresh()
    assert port.calls >= 1
    assert 7 in p._template_widgets


def test_templates_port_path_delete_uses_port(qapp, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.gui.domains.operations.prompt_studio.panels.prompt_templates_panel.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )
    port = _FakePort()
    p = PromptTemplatesPanel(prompt_studio_port=port)
    p._current_project_id = 1
    p.refresh()
    loads_before = port.calls
    tpl = Prompt(
        id=7,
        title="T",
        category="general",
        description="",
        content="",
        tags=[],
        prompt_type="template",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    p._on_delete(tpl)
    assert port.deleted_ids == [7]
    assert port.calls >= loads_before + 1
