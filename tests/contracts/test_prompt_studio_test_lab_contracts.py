"""Prompt Studio Test Lab (Batch 5) — Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabModelsCommand,
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabModelsState,
    PromptTestLabPromptRowDto,
    PromptTestLabPromptsState,
    PromptTestLabRunPatch,
    PromptTestLabRunState,
    PromptTestLabStreamChunkDto,
    PromptTestLabVersionRowDto,
    PromptTestLabVersionsState,
    RunPromptTestLabCommand,
)


def test_prompt_row_dto() -> None:
    r = PromptTestLabPromptRowDto(prompt_id=7, display_title="T")
    assert r.prompt_id == 7


def test_prompts_state() -> None:
    st = PromptTestLabPromptsState(
        phase="ready",
        rows=(PromptTestLabPromptRowDto(1, "A"),),
    )
    assert len(st.rows) == 1


def test_version_row_dto() -> None:
    v = PromptTestLabVersionRowDto(
        version=2,
        display_label="v2 (01.01.2025)",
        title="t",
        content="c",
    )
    assert v.content == "c"


def test_versions_state() -> None:
    st = PromptTestLabVersionsState(phase="ready", prompt_id=3, rows=())
    assert st.prompt_id == 3


def test_models_state() -> None:
    st = PromptTestLabModelsState(phase="ready", models=("m1",), default_model="m1")
    assert st.models[0] == "m1"


def test_commands() -> None:
    assert LoadPromptTestLabPromptsCommand(1).project_id == 1
    assert LoadPromptTestLabVersionsCommand(9).prompt_id == 9
    assert isinstance(LoadPromptTestLabModelsCommand(), LoadPromptTestLabModelsCommand)


def test_run_command_and_stream_dto() -> None:
    c = RunPromptTestLabCommand("llama", "sys", "usr", 0.7, 2048)
    assert c.model_name == "llama"
    ch = PromptTestLabStreamChunkDto("x", None)
    assert ch.content_delta == "x"


def test_run_patch_and_state() -> None:
    p = PromptTestLabRunPatch(replace_full_text="t", phase="success", run_button_enabled=True)
    assert p.scroll_to_max is False
    st = PromptTestLabRunState(phase="error", output_text="e", run_button_enabled=True)
    assert st.output_text == "e"
