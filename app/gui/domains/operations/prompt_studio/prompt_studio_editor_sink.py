"""
Prompt Studio — Editor-Speichern: Zustand aus :class:`PromptEditorSaveResultState` spiegeln.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QLabel

from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorSaveResultState,
    PromptStudioPromptSnapshotDto,
)


class PromptStudioEditorSink:
    def __init__(
        self,
        dirty_indicator: QLabel,
        *,
        on_success: Callable[[PromptStudioPromptSnapshotDto], None],
        on_error: Callable[[str], None],
    ) -> None:
        self._dirty_indicator = dirty_indicator
        self._on_success = on_success
        self._on_error = on_error

    def apply_save_result(self, state: PromptEditorSaveResultState) -> None:
        if state.phase == "saving":
            self._dirty_indicator.setText("• Speichern…")
            return
        if state.phase == "error":
            self._dirty_indicator.setText("")
            self._on_error(state.error_message or "Fehler beim Speichern.")
            return
        if state.phase == "success" and state.snapshot is not None:
            self._dirty_indicator.setText("")
            self._on_success(state.snapshot)
            return
        self._dirty_indicator.setText("")
