"""PromptStudioLibrarySink — Batch 2."""

from __future__ import annotations

from app.gui.domains.operations.prompt_studio.prompt_studio_library_sink import PromptStudioLibrarySink
from app.ui_contracts.workspaces.prompt_studio_list import PromptStudioListState


class _Panel:
    def __init__(self) -> None:
        self.calls: list[PromptStudioListState] = []

    def apply_prompt_library_state(self, state: PromptStudioListState, prompt_models: tuple = ()) -> None:
        self.calls.append(state)


def test_library_sink_delegates() -> None:
    p = _Panel()
    PromptStudioLibrarySink(p).apply_full_state(PromptStudioListState(phase="empty", empty_hint="x"), ())
    assert len(p.calls) == 1
    assert p.calls[0].empty_hint == "x"
