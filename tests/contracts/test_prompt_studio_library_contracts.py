"""Prompt Studio Library — Contracts (Batch 2, Aliasse zu Slice 1)."""

from __future__ import annotations

from app.ui_contracts.workspaces.prompt_studio_library import (
    DeletePromptLibraryCommand,
    LoadPromptLibraryCommand,
    PromptLibraryMutationResult,
    PromptLibraryRowDto,
    PromptLibraryState,
    prompt_library_loading_state,
)


def test_delete_library_command() -> None:
    c = DeletePromptLibraryCommand(9, 2, "f")
    assert c.prompt_id == 9
    assert c.project_id == 2
    assert c.filter_text == "f"


def test_library_mutation_result() -> None:
    assert PromptLibraryMutationResult(ok=True).error_message is None


def test_library_command_alias() -> None:
    c = LoadPromptLibraryCommand(5, "q")
    assert c.project_id == 5
    assert c.filter_text == "q"


def test_library_row_dto_alias() -> None:
    r = PromptLibraryRowDto(1, "project", 3)
    assert r.prompt_id == 1
    assert r.version_count == 3


def test_library_state_and_loading() -> None:
    assert prompt_library_loading_state().phase == "loading"
    st = PromptLibraryState(phase="empty", empty_hint="x")
    assert st.empty_hint == "x"
