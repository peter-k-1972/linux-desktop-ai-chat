"""Prompt Studio List (Slice 1) — Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts.workspaces.prompt_studio_list import (
    LoadPromptStudioListCommand,
    PromptListEntryDto,
    PromptStudioListState,
    prompt_studio_list_loading_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_entry_dto() -> None:
    e = PromptListEntryDto(prompt_id=1, list_section="global", version_count=2)
    assert e.prompt_id == 1
    assert e.version_count == 2


def test_load_command() -> None:
    c = LoadPromptStudioListCommand(3, "x")
    assert c.project_id == 3
    assert c.filter_text == "x"


def test_loading_state() -> None:
    assert prompt_studio_list_loading_state().phase == "loading"


def test_list_state_error() -> None:
    err = SettingsErrorInfo(code="c", message="m")
    st = PromptStudioListState(phase="error", error=err)
    assert st.error == err
