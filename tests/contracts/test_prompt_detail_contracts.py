"""Prompt Studio Detail (Slice 2) — Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts.workspaces.prompt_studio_detail import (
    LoadPromptDetailCommand,
    PromptDetailDto,
    PromptStudioDetailState,
    prompt_studio_detail_loading_state,
)


def test_detail_dto() -> None:
    d = PromptDetailDto(
        prompt_id="1",
        name="T",
        content="c",
        version_count=2,
        last_modified="2025-01-01",
    )
    assert d.prompt_id == "1"
    assert d.version_count == 2


def test_load_command() -> None:
    c = LoadPromptDetailCommand("5", "9")
    assert c.prompt_id == "5"
    assert c.project_id == "9"
    assert LoadPromptDetailCommand("", None).project_id is None


def test_loading_state() -> None:
    assert prompt_studio_detail_loading_state().phase == "loading"


def test_detail_state_error() -> None:
    st = PromptStudioDetailState(phase="error", error_message="x")
    assert st.error_message == "x"
