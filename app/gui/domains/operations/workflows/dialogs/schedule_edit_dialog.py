"""Dialog: Schedule anlegen/bearbeiten — keine Businesslogik, nur Eingaben."""

from __future__ import annotations

import json
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from app.workflows.scheduling.models import WorkflowSchedule


class ScheduleEditDialog(QDialog):
    """Pflicht: next_run_at (UTC ISO), workflow_id, JSON initial_input; optional Intervall."""

    def __init__(
        self,
        parent=None,
        *,
        schedule: Optional[WorkflowSchedule] = None,
        default_workflow_id: str = "",
    ):
        super().__init__(parent)
        self.setWindowTitle("Schedule bearbeiten" if schedule else "Schedule anlegen")
        self.setMinimumWidth(520)
        self._schedule = schedule

        root = QVBoxLayout(self)
        root.addWidget(
            QLabel(
                "next_run_at als UTC-ISO (z. B. 2026-03-22T14:30:00+00:00). "
                "Wiederholung: Intervall ≥ 60 s oder 0 für einmalig nach Ausführung."
            )
        )
        form = QFormLayout()
        self._wf_id = QLineEdit()
        self._wf_id.setObjectName("scheduleEditWorkflowId")
        wid = default_workflow_id or (schedule.workflow_id if schedule else "")
        self._wf_id.setText(wid)
        form.addRow("workflow_id", self._wf_id)

        self._next_run = QLineEdit()
        self._next_run.setObjectName("scheduleEditNextRunUtc")
        if schedule:
            self._next_run.setText(schedule.next_run_at)
        form.addRow("next_run_at (UTC)", self._next_run)

        self._input = QTextEdit()
        self._input.setObjectName("scheduleEditInitialInputJson")
        self._input.setPlaceholderText('{ "key": "value" }')
        raw_inp = schedule.initial_input_json if schedule else "{}"
        try:
            obj = json.loads(raw_inp)
            self._input.setPlainText(json.dumps(obj, ensure_ascii=False, indent=2))
        except (json.JSONDecodeError, TypeError):
            self._input.setPlainText(raw_inp)

        self._repeat = QSpinBox()
        self._repeat.setObjectName("scheduleEditRepeatSeconds")
        self._repeat.setRange(0, 86400 * 365)
        self._repeat.setSpecialValueText("—")
        self._repeat.setSuffix(" s")
        rep = 0
        if schedule:
            try:
                rj = json.loads(schedule.rule_json or "{}")
                if isinstance(rj, dict) and "repeat_interval_seconds" in rj:
                    rep = int(rj["repeat_interval_seconds"])
            except (json.JSONDecodeError, TypeError, ValueError):
                rep = 0
        if rep <= 0:
            self._repeat.setValue(0)
        else:
            self._repeat.setValue(rep)

        self._enabled = QCheckBox("Aktiv")
        self._enabled.setObjectName("scheduleEditEnabled")
        self._enabled.setChecked(True if schedule is None else schedule.enabled)

        form.addRow("initial_input (JSON)", self._input)
        form.addRow("repeat_interval_seconds (0 = kein)", self._repeat)
        row_en = QHBoxLayout()
        row_en.addWidget(self._enabled)
        row_en.addStretch()
        form.addRow("", row_en)
        root.addLayout(form)

        self._error = QLabel("")
        self._error.setObjectName("scheduleEditError")
        self._error.setWordWrap(True)
        self._error.hide()
        root.addWidget(self._error)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _on_ok(self) -> None:
        wf = self._wf_id.text().strip()
        if not wf:
            self._error.setText("workflow_id fehlt.")
            self._error.show()
            return
        nxt = self._next_run.text().strip()
        if not nxt:
            self._error.setText("next_run_at fehlt.")
            self._error.show()
            return
        text = self._input.toPlainText().strip()
        if not text:
            parsed_inp: dict = {}
        else:
            try:
                val = json.loads(text)
            except json.JSONDecodeError as e:
                self._error.setText(str(e))
                self._error.show()
                return
            if not isinstance(val, dict):
                self._error.setText("initial_input muss ein JSON-Objekt sein.")
                self._error.show()
                return
            parsed_inp = val
        rep = int(self._repeat.value())
        if rep != 0 and rep < 60:
            self._error.setText("Wiederholintervall muss 0 oder ≥ 60 Sekunden sein.")
            self._error.show()
            return
        rule = {}
        if rep > 0:
            rule["repeat_interval_seconds"] = rep
        self._result = {
            "workflow_id": wf,
            "next_run_at": nxt,
            "initial_input_json": json.dumps(parsed_inp, ensure_ascii=False, sort_keys=True),
            "rule_json": json.dumps(rule, ensure_ascii=False, sort_keys=True),
            "enabled": self._enabled.isChecked(),
        }
        self.accept()

    def get_result(self) -> dict:
        return getattr(self, "_result", {})
