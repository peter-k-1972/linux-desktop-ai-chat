"""
EventBus Panels – Event Stream aus DebugStore.
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
from app.debug.agent_event import AgentEvent
from app.debug.debug_store import get_debug_store
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_control_qss,
    rd_monospace_table_qss,
    rd_detail_text_edit_qss,
)


class EventStreamPanel(QFrame):
    """Event Stream aus DebugStore event_history."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("eventStreamPanel")
        self.setMinimumHeight(220)
        self._selected_event: AgentEvent | None = None
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1000)

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel("Event Stream")
        title.setStyleSheet(rd_section_title_qss())
        header.addWidget(title)

        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["All", "task_created", "task_started", "task_completed", "task_failed", "model_call", "tool_execution"])
        self._filter_combo.setStyleSheet(rd_control_qss())
        self._filter_combo.currentTextChanged.connect(self._refresh)
        header.addWidget(self._filter_combo)
        header.addStretch()
        layout.addLayout(header)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Zeit", "Typ", "Agent", "Payload"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(rd_monospace_table_qss())
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table)

    def _refresh(self) -> None:
        try:
            store = get_debug_store()
            events = store.get_event_history()
            typ_filter = self._filter_combo.currentText()
            if typ_filter and typ_filter != "All":
                events = [e for e in events if (e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)) == typ_filter]

            self._table.setRowCount(len(events))
            for row, ev in enumerate(events):
                ts = ev.timestamp.strftime("%H:%M:%S") if ev.timestamp else ""
                t = ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type)
                agent = ev.agent_name or "—"
                payload = (ev.message or "")[:50]
                if len(ev.message or "") > 50:
                    payload += "…"
                item0 = QTableWidgetItem(ts)
                item0.setData(Qt.ItemDataRole.UserRole, ev)
                self._table.setItem(row, 0, item0)
                self._table.setItem(row, 1, QTableWidgetItem(t))
                self._table.setItem(row, 2, QTableWidgetItem(agent))
                self._table.setItem(row, 3, QTableWidgetItem(payload))

            if not events:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("—"))
                self._table.setItem(0, 1, QTableWidgetItem("—"))
                self._table.setItem(0, 2, QTableWidgetItem("Keine Events"))
                self._table.setItem(0, 3, QTableWidgetItem(""))
        except Exception:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem("—"))
            self._table.setItem(0, 1, QTableWidgetItem("—"))
            self._table.setItem(0, 2, QTableWidgetItem("DebugStore nicht verfügbar"))
            self._table.setItem(0, 3, QTableWidgetItem(""))

    def _on_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            self._selected_event = None
        else:
            item = self._table.item(row, 0)
            self._selected_event = item.data(Qt.ItemDataRole.UserRole) if item else None
        if hasattr(self.parent(), "on_event_selected"):
            self.parent().on_event_selected(self._selected_event)


class EventDetailPanel(QFrame):
    """Detailansicht eines Events."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("eventDetailPanel")
        self.setMinimumHeight(80)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Event Detail")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)
        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setStyleSheet(rd_detail_text_edit_qss())
        layout.addWidget(self._content)

    def set_event(self, event: AgentEvent | None) -> None:
        if not event:
            self._content.setPlaceholderText("Event auswählen…")
            self._content.clear()
            return
        import json
        ts = event.timestamp.strftime("%H:%M:%S") if event.timestamp else ""
        t = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
        lines = [f"Zeit: {ts}", f"Typ: {t}", f"Agent: {event.agent_name or '—'}", f"Nachricht: {event.message or '—'}"]
        if event.metadata:
            lines.append("Metadata:")
            lines.append(json.dumps(event.metadata, indent=2, ensure_ascii=False))
        self._content.setPlainText("\n".join(lines))
