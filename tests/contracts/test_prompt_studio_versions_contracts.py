"""Prompt Studio Versions — Contracts (Batch 2 read; Batch 8: keine Panel-Mutations-DTOs nötig)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from dataclasses import asdict

from app.ui_contracts.workspaces.prompt_studio_versions import (
    LoadPromptVersionsCommand,
    PromptVersionPanelState,
    PromptVersionRowDto,
    prompt_versions_loading_state,
)


def test_version_row_asdict() -> None:
    r = PromptVersionRowDto(2, "t", "c", "2025-01-01T00:00:00")
    d = asdict(r)
    assert d["version"] == 2


def test_load_command() -> None:
    assert LoadPromptVersionsCommand(99).prompt_id == 99


def test_loading_state() -> None:
    st = prompt_versions_loading_state(7)
    assert st.phase == "loading"
    assert st.prompt_id == 7


def test_panel_state_empty() -> None:
    st = PromptVersionPanelState(phase="empty", prompt_id=1)
    assert st.rows == ()
