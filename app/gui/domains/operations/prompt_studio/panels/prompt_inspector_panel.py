"""
PromptInspectorPanel — Inspector-Spalte für Prompt Studio (Slice 2).

Wendet :class:`PromptStudioDetailState` an und hostet :class:`PromptStudioInspector`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.gui.inspector.prompt_studio_inspector import PromptStudioInspector
from app.prompts.prompt_models import Prompt
from app.ui_contracts.workspaces.prompt_studio_detail import PromptStudioDetailState

if TYPE_CHECKING:
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort


class PromptInspectorPanel(QWidget):
    """Stable host for prompt inspector content driven by port state."""

    def __init__(
        self,
        on_version_selected: Optional[Callable[[dict], None]] = None,
        parent=None,
        *,
        prompt_studio_port: Optional[PromptStudioPort] = None,
    ):
        super().__init__(parent)
        self.setObjectName("promptInspectorPanel")
        self._on_version_selected = on_version_selected
        self._prompt_studio_port = prompt_studio_port
        self._project_name: str | None = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._apply_placeholder("Wählen Sie einen Prompt aus.")

    def set_project_context_name(self, project_name: str | None) -> None:
        self._project_name = project_name

    def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if state.phase == "loading":
            self._apply_placeholder("Details werden geladen …")
            return
        if state.phase == "error":
            self._apply_placeholder(state.error_message or "Fehler.")
            return
        if state.detail is None:
            self._apply_placeholder("Wählen Sie einen Prompt aus.")
            return

        d = state.detail
        try:
            pid_int = int(d.prompt_id)
        except ValueError:
            self._apply_placeholder("Ungültige Prompt-ID.")
            return

        prompt = Prompt(
            id=pid_int,
            title=d.name,
            category="general",
            description="",
            content=d.content,
            tags=[],
            prompt_type="user",
            scope="global",
            project_id=None,
            created_at=None,
            updated_at=None,
        )
        inner = PromptStudioInspector(
            project_name=self._project_name,
            prompt=prompt,
            on_version_selected=self._on_version_selected,
            versions=None,
            prompt_studio_port=self._prompt_studio_port,
            parent=self,
        )
        self._layout.addWidget(inner)

    def _apply_placeholder(self, text: str) -> None:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName("promptInspectorPlaceholder")
        self._layout.addWidget(label)
