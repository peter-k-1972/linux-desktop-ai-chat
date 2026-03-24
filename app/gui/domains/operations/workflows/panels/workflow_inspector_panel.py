"""Inspector: Konfiguration des ausgewählten Knotens."""

from __future__ import annotations

from typing import Callable, List, Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from shiboken6 import Shiboken
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.gui.domains.operations.workflows.config_json import format_node_config_json, parse_node_config_json
from app.workflows.models.definition import WorkflowNode
from app.workflows.models.run import NodeRun


class WorkflowInspectorPanel(QWidget):
    """Felder für einen WorkflowNode; Übernehmen ruft Callback auf."""

    apply_requested = Signal()

    def __init__(
        self,
        on_apply: Callable[..., Optional[str]],
        node_types: Optional[List[str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("workflowInspectorPanel")
        self._on_apply = on_apply
        self._node_types = node_types or ["start", "end", "noop"]
        self._current_id: Optional[str] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        title = QLabel("Workflow-Inspector")
        title.setObjectName("inspectorSectionTitle")
        outer.addWidget(title)

        self._stack = QStackedWidget()
        page_empty = QWidget()
        el = QVBoxLayout(page_empty)
        el.addWidget(
            QLabel("Wählen Sie einen Knoten im Prozessdiagramm (Canvas).")
        )
        el.addStretch()
        self._stack.addWidget(page_empty)

        page_form = QWidget()
        fv = QVBoxLayout(page_form)
        fl = QFormLayout()
        self._node_id = QLineEdit()
        self._node_type = QComboBox()
        self._node_type.setEditable(True)
        for t in self._node_types:
            self._node_type.addItem(t)
        self._title = QLineEdit()
        self._description = QTextEdit()
        self._description.setMaximumHeight(72)
        self._enabled = QCheckBox("Knoten aktiv (is_enabled)")
        self._config = QTextEdit()
        self._config.setPlaceholderText('JSON, z. B. {} oder {"merge": {"k": 1}}')
        self._config.setMinimumHeight(120)
        fl.addRow("node_id:", self._node_id)
        fl.addRow("node_type:", self._node_type)
        fl.addRow("title:", self._title)
        fl.addRow("description:", self._description)
        fl.addRow(self._enabled)
        fl.addRow("config (JSON):", self._config)

        run_title = QLabel("Ausgewählter Run (read-only)")
        run_title.setObjectName("inspectorSectionTitle")
        rf = QFont()
        rf.setBold(True)
        run_title.setFont(rf)
        fl.addRow(run_title)
        self._run_status = QLabel("—")
        self._run_status.setWordWrap(True)
        self._run_times = QLabel("—")
        self._run_times.setWordWrap(True)
        self._run_err = QLabel("—")
        self._run_err.setObjectName("workflowInspectorError")
        self._run_err.setWordWrap(True)
        fl.addRow("NodeRun-Status:", self._run_status)
        fl.addRow("Zeiten:", self._run_times)
        fl.addRow("Fehler:", self._run_err)

        self._err = QLabel("")
        self._err.setObjectName("workflowInspectorError")
        self._err.setWordWrap(True)
        self._err.hide()

        btn = QPushButton("Übernehmen")
        btn.clicked.connect(self._apply)

        fv.addLayout(fl)
        fv.addWidget(self._err)
        fv.addWidget(btn)
        fv.addStretch()
        self._stack.addWidget(page_form)
        outer.addWidget(self._stack, 1)

    def _run_labels_alive(self) -> bool:
        return all(
            Shiboken.isValid(w)
            for w in (self._run_status, self._run_times, self._run_err)
        )

    def clear(self) -> None:
        self._current_id = None
        if Shiboken.isValid(self._stack):
            self._stack.setCurrentIndex(0)
        if Shiboken.isValid(self._err):
            self._err.hide()
        self._clear_run_context()

    def _clear_run_context(self) -> None:
        if not self._run_labels_alive():
            return
        self._run_status.setText("—")
        self._run_times.setText("—")
        self._run_err.setText("—")

    def set_run_node_context(self, node_run: Optional[NodeRun]) -> None:
        """Kompakter Run-Kontext zum aktuell angezeigten Knoten (kein Ersatz für Run-Panel)."""
        if node_run is None:
            self._clear_run_context()
            return
        if not self._run_labels_alive():
            return
        self._run_status.setText(f"{node_run.status.value} · {node_run.node_run_id}")
        st = _fmt_ts(node_run.started_at)
        en = _fmt_ts(node_run.finished_at)
        self._run_times.setText(f"start: {st}\nende: {en}\nretries: {node_run.retry_count}")
        err = (node_run.error_message or "").strip()
        self._run_err.setText(err if err else "—")

    def show_node(self, node: WorkflowNode) -> None:
        self._current_id = node.node_id
        self._node_id.setText(node.node_id)
        idx = self._node_type.findText(node.node_type)
        if idx >= 0:
            self._node_type.setCurrentIndex(idx)
        else:
            self._node_type.setEditText(node.node_type)
        self._title.setText(node.title)
        self._description.setPlainText(node.description)
        self._enabled.setChecked(node.is_enabled)
        self._config.setPlainText(format_node_config_json(node.config))
        self._err.hide()
        self._stack.setCurrentIndex(1)

    def _apply(self) -> None:
        if self._current_id is None:
            return
        cfg, err = parse_node_config_json(self._config.toPlainText())
        if err:
            self._err.setText(err)
            self._err.show()
            return
        self._err.hide()
        msg = self._on_apply(
            old_node_id=self._current_id,
            new_node_id=self._node_id.text().strip(),
            node_type=self._node_type.currentText().strip(),
            title=self._title.text(),
            description=self._description.toPlainText(),
            is_enabled=self._enabled.isChecked(),
            config=cfg or {},
        )
        if msg:
            self._err.setText(msg)
            self._err.show()
            return
        self.apply_requested.emit()
        new_id = self._node_id.text().strip()
        if new_id:
            self._current_id = new_id


def _fmt_ts(dt: object) -> str:
    if dt is None:
        return "—"
    return dt.isoformat()
