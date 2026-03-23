"""
LLM Calls Panels – Call History, Detail mit echten Daten aus DebugStore.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, QTimer
from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import get_debug_store
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_control_qss,
    rd_monospace_table_qss,
    rd_detail_text_edit_qss,
)


class LLMCallHistoryPanel(QFrame):
    """LLM Call History aus DebugStore (MODEL_CALL Events)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("llmCallHistoryPanel")
        self.setMinimumHeight(220)
        self._selected_event: AgentEvent | None = None
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1500)

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel("LLM Call History")
        title.setStyleSheet(rd_section_title_qss())
        header.addWidget(title)

        self._model_filter = QComboBox()
        self._model_filter.addItem("Alle Modelle")
        self._model_filter.setStyleSheet(rd_control_qss())
        self._model_filter.currentTextChanged.connect(self._refresh)
        header.addWidget(self._model_filter)
        header.addStretch()
        layout.addLayout(header)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Time", "Model", "Agent", "Duration", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(rd_monospace_table_qss())
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table)

    def _refresh(self) -> None:
        try:
            store = get_debug_store()
            events = store.get_event_history()
            model_calls = [e for e in events if e.event_type == EventType.MODEL_CALL]
            model_filter = self._model_filter.currentText()
            if model_filter and model_filter != "Alle Modelle":
                model_calls = [e for e in model_calls if (e.metadata.get("model_id") or e.message or "") == model_filter]

            all_events = store.get_event_history()
            models = sorted({e.metadata.get("model_id") or e.message or "unknown" for e in all_events if e.event_type == EventType.MODEL_CALL})
            self._model_filter.blockSignals(True)
            self._model_filter.clear()
            self._model_filter.addItem("Alle Modelle")
            for m in models:
                self._model_filter.addItem(m)
            idx = self._model_filter.findText(model_filter) if model_filter else 0
            if idx >= 0:
                self._model_filter.setCurrentIndex(idx)
            self._model_filter.blockSignals(False)

            self._table.setRowCount(len(model_calls))
            for row, ev in enumerate(model_calls):
                ts = ev.timestamp.strftime("%H:%M:%S") if ev.timestamp else ""
                model = ev.metadata.get("model_id") or ev.message or "—"
                agent = ev.agent_name or "—"
                dur = ev.metadata.get("duration_sec")
                dur_str = f"{dur:.1f}s" if dur is not None and dur > 0 else "—"
                status = "OK"
                item0 = QTableWidgetItem(ts)
                item0.setData(Qt.ItemDataRole.UserRole, ev)
                self._table.setItem(row, 0, item0)
                self._table.setItem(row, 1, QTableWidgetItem(model))
                self._table.setItem(row, 2, QTableWidgetItem(agent))
                self._table.setItem(row, 3, QTableWidgetItem(dur_str))
                self._table.setItem(row, 4, QTableWidgetItem(status))

            if not model_calls:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("—"))
                self._table.setItem(0, 1, QTableWidgetItem("—"))
                self._table.setItem(0, 2, QTableWidgetItem("Keine LLM-Aufrufe"))
                self._table.setItem(0, 3, QTableWidgetItem(""))
                self._table.setItem(0, 4, QTableWidgetItem(""))
        except Exception:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem("—"))
            self._table.setItem(0, 1, QTableWidgetItem("—"))
            self._table.setItem(0, 2, QTableWidgetItem("DebugStore nicht verfügbar"))
            self._table.setItem(0, 3, QTableWidgetItem(""))
            self._table.setItem(0, 4, QTableWidgetItem(""))

    def _on_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            self._selected_event = None
        else:
            item = self._table.item(row, 0)
            self._selected_event = item.data(Qt.ItemDataRole.UserRole) if item else None
        if hasattr(self.parent(), "on_llm_call_selected"):
            self.parent().on_llm_call_selected(self._selected_event)


class LLMCallDetailPanel(QFrame):
    """Detailansicht eines LLM-Aufrufs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("llmCallDetailPanel")
        self.setMinimumHeight(80)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("LLM Call Detail")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)
        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setStyleSheet(rd_detail_text_edit_qss())
        layout.addWidget(self._content)

    def set_event(self, event: AgentEvent | None) -> None:
        if not event:
            self._content.setPlaceholderText("LLM-Aufruf auswählen…")
            self._content.clear()
            return
        ts = event.timestamp.strftime("%H:%M:%S") if event.timestamp else ""
        model = event.metadata.get("model_id") or event.message or "—"
        agent = event.agent_name or "—"
        dur = event.metadata.get("duration_sec")
        dur_str = f"{dur:.1f}s" if dur is not None else "—"
        lines = [
            f"Zeit: {ts}",
            f"Modell: {model}",
            f"Agent: {agent}",
            f"Dauer: {dur_str}",
            f"Nachricht: {event.message or '—'}",
        ]
        if event.metadata:
            for k, v in event.metadata.items():
                if k not in ("model_id", "duration_sec") and v is not None:
                    lines.append(f"{k}: {v}")
        self._content.setPlainText("\n".join(lines))
