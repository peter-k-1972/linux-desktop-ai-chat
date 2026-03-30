"""Prompt Studio Templates — Contracts (Batch 2)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

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


def test_template_row() -> None:
    r = PromptTemplateRowDto(42)
    assert asdict(r)["prompt_id"] == 42


def test_load_command() -> None:
    c = LoadPromptTemplatesCommand(3, "x")
    assert c.project_id == 3
    assert c.filter_text == "x"


def test_loading_state() -> None:
    assert prompt_templates_loading_state().phase == "loading"


def test_template_mutation_commands_asdict() -> None:
    assert asdict(CreatePromptTemplateCommand("a", "b", "c", "global", None))["title"] == "a"
    assert asdict(UpdatePromptTemplateCommand(1, "t", "", ""))["template_id"] == 1
    assert asdict(CopyPromptTemplateCommand(2, "project", 3))["source_template_id"] == 2
    assert asdict(DeletePromptTemplateCommand(4))["template_id"] == 4
    assert asdict(PromptTemplateMutationResult(ok=False, error_message="e"))["ok"] is False
