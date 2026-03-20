"""
ContextInspectionPanel – read-only display of context inspection output.

Pure viewer: displays all sections from adapter, no filtering, no transformation.
Calls ContextInspectionService, uses ContextInspectionViewAdapter.
No business logic, no resolver calls outside service, no mutation.
Panel does not influence request execution.
"""

from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from app.context.inspection import ContextInspectionViewModel
    from app.services.context_explain_service import ContextExplainRequest

from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QPlainTextEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt


def _lines_to_text(lines: list[str]) -> str:
    """Join lines; empty list → placeholder. No transformation."""
    if not lines:
        return "—"
    return "\n".join(lines)


class ContextInspectionPanel(QFrame):
    """
    Read-only panel displaying context inspection: summary, budget, sources,
    warnings, payload preview (optional toggle).

    Uses ContextInspectionService and ContextInspectionViewAdapter only.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contextInspectionPanel")
        self._chat_id: Optional[int] = None
        self._request: Optional["ContextExplainRequest"] = None
        self._show_payload_preview = False
        self._last_vm: Optional["ContextInspectionViewModel"] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._payload_toggle = QCheckBox("Payload-Vorschau anzeigen")
        self._payload_toggle.setChecked(False)
        self._payload_toggle.toggled.connect(self._on_payload_toggle_changed)
        layout.addWidget(self._payload_toggle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        self._summary_group = QGroupBox("Zusammenfassung")
        self._summary_edit = QPlainTextEdit()
        self._summary_edit.setReadOnly(True)
        self._summary_edit.setMaximumBlockCount(50)
        self._summary_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._summary_edit.setStyleSheet(
            "QPlainTextEdit { background: #1e293b; color: #cbd5e1; "
            "font-family: monospace; font-size: 11px; border: none; }"
        )
        gl = QVBoxLayout(self._summary_group)
        gl.addWidget(self._summary_edit)
        content_layout.addWidget(self._summary_group)

        self._budget_group = QGroupBox("Budget")
        self._budget_edit = QPlainTextEdit()
        self._budget_edit.setReadOnly(True)
        self._budget_edit.setMaximumBlockCount(100)
        self._budget_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._budget_edit.setStyleSheet(
            "QPlainTextEdit { background: #1e293b; color: #cbd5e1; "
            "font-family: monospace; font-size: 11px; border: none; }"
        )
        gl = QVBoxLayout(self._budget_group)
        gl.addWidget(self._budget_edit)
        content_layout.addWidget(self._budget_group)

        self._sources_group = QGroupBox("Quellen")
        self._sources_edit = QPlainTextEdit()
        self._sources_edit.setReadOnly(True)
        self._sources_edit.setMaximumBlockCount(100)
        self._sources_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._sources_edit.setStyleSheet(
            "QPlainTextEdit { background: #1e293b; color: #cbd5e1; "
            "font-family: monospace; font-size: 11px; border: none; }"
        )
        gl = QVBoxLayout(self._sources_group)
        gl.addWidget(self._sources_edit)
        content_layout.addWidget(self._sources_group)

        self._warnings_group = QGroupBox("Warnungen")
        self._warnings_edit = QPlainTextEdit()
        self._warnings_edit.setReadOnly(True)
        self._warnings_edit.setMaximumBlockCount(50)
        self._warnings_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._warnings_edit.setStyleSheet(
            "QPlainTextEdit { background: #1e293b; color: #cbd5e1; "
            "font-family: monospace; font-size: 11px; border: none; }"
        )
        gl = QVBoxLayout(self._warnings_group)
        gl.addWidget(self._warnings_edit)
        content_layout.addWidget(self._warnings_group)

        self._payload_group = QGroupBox("Payload-Vorschau")
        self._payload_edit = QPlainTextEdit()
        self._payload_edit.setReadOnly(True)
        self._payload_edit.setMaximumBlockCount(100)
        self._payload_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._payload_edit.setStyleSheet(
            "QPlainTextEdit { background: #1e293b; color: #cbd5e1; "
            "font-family: monospace; font-size: 11px; border: none; }"
        )
        gl = QVBoxLayout(self._payload_group)
        gl.addWidget(self._payload_edit)
        content_layout.addWidget(self._payload_group)
        self._payload_group.setVisible(False)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def set_chat_id(self, chat_id: Optional[int]) -> None:
        """Set chat to inspect. None = clear."""
        self._chat_id = chat_id
        self._request = None
        self._refresh()

    def set_request(self, request: Optional["ContextExplainRequest"]) -> None:
        """Set full request to inspect. None = clear."""
        self._request = request
        self._chat_id = request.chat_id if request else None
        self._refresh()

    def _on_payload_toggle_changed(self, checked: bool) -> None:
        self._show_payload_preview = checked
        self._payload_group.setVisible(checked)
        self._refresh()

    def _refresh(self) -> None:
        """Load inspection data and update display. Read-only; no mutation."""
        if self._chat_id is None and self._request is None:
            self._last_vm = None
            self._summary_edit.setPlainText("Kein Chat ausgewählt.")
            self._budget_edit.setPlainText("—")
            self._sources_edit.setPlainText("—")
            self._warnings_edit.setPlainText("—")
            self._payload_edit.setPlainText("—")
            return

        try:
            from app.services.context_explain_service import ContextExplainRequest
            from app.services.context_inspection_service import get_context_inspection_service
            from app.context.inspection import ContextInspectionViewAdapter

            request = self._request or ContextExplainRequest(chat_id=self._chat_id)
            result = get_context_inspection_service().inspect(request)
            vm = ContextInspectionViewAdapter.to_view_model(result)
            self._last_vm = vm

            self._summary_edit.setPlainText(_lines_to_text(vm.summary_lines))
            self._budget_edit.setPlainText(_lines_to_text(vm.budget_lines))
            self._sources_edit.setPlainText(_lines_to_text(vm.source_lines))
            self._warnings_edit.setPlainText(_lines_to_text(vm.warning_lines))

            if self._show_payload_preview:
                self._payload_edit.setPlainText(_lines_to_text(vm.payload_preview_lines))
            else:
                self._payload_edit.setPlainText("—")

            self._verify_display_matches_adapter(vm)
        except Exception as e:
            self._last_vm = None
            self._summary_edit.setPlainText(f"Fehler: {e}")
            self._budget_edit.setPlainText("—")
            self._sources_edit.setPlainText("—")
            self._warnings_edit.setPlainText("—")
            self._payload_edit.setPlainText("—")

    def get_displayed_content(self) -> Dict[str, str]:
        """Return current displayed text per section. For QA and dev verification."""
        return {
            "summary": self._summary_edit.toPlainText(),
            "budget": self._budget_edit.toPlainText(),
            "sources": self._sources_edit.toPlainText(),
            "warnings": self._warnings_edit.toPlainText(),
            "payload": self._payload_edit.toPlainText(),
        }

    def _verify_display_matches_adapter(self, vm: "ContextInspectionViewModel") -> None:
        """Dev-only: assert displayed lines equal adapter output. No-op when CONTEXT_DEBUG_ENABLED off."""
        try:
            from app.context.debug.context_debug_flag import is_context_debug_enabled
            if not is_context_debug_enabled():
                return
        except Exception:
            return
        displayed = self.get_displayed_content()
        expected_summary = _lines_to_text(vm.summary_lines)
        expected_budget = _lines_to_text(vm.budget_lines)
        expected_sources = _lines_to_text(vm.source_lines)
        expected_warnings = _lines_to_text(vm.warning_lines)
        expected_payload = _lines_to_text(vm.payload_preview_lines) if self._show_payload_preview else "—"
        assert displayed["summary"] == expected_summary, "Panel summary != adapter"
        assert displayed["budget"] == expected_budget, "Panel budget != adapter"
        assert displayed["sources"] == expected_sources, "Panel sources != adapter"
        assert displayed["warnings"] == expected_warnings, "Panel warnings != adapter"
        assert displayed["payload"] == expected_payload, "Panel payload != adapter"

    def refresh(self) -> None:
        """Public refresh for BasePanel compatibility."""
        self._refresh()
