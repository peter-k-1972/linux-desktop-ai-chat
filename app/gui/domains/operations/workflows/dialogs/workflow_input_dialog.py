"""Dialog: initial_input für Test-Run / Re-Run (JSON)."""

from __future__ import annotations

import json
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)


class WorkflowInputDialog(QDialog):
    """JSON-Objekt als initial_input; leer -> {}."""

    def __init__(
        self,
        parent=None,
        *,
        window_title: Optional[str] = None,
        initial_input: Optional[dict] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(window_title or "Test-Run – Eingabe (JSON)")
        self.setMinimumSize(480, 320)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("initial_input als JSON-Objekt, z. B. {\"msg\": \"Hallo\"}"))
        self._edit = QTextEdit()
        self._edit.setPlaceholderText('{\n  "key": "value"\n}')
        self._edit.setObjectName("workflowInitialInputJson")
        if initial_input:
            try:
                self._edit.setPlainText(json.dumps(initial_input, ensure_ascii=False, indent=2))
            except (TypeError, ValueError):
                self._edit.setPlainText("{}")
        layout.addWidget(self._edit)
        self._error = QLabel("")
        self._error.setObjectName("workflowJsonError")
        self._error.setWordWrap(True)
        self._error.hide()
        layout.addWidget(self._error)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_ok(self) -> None:
        text = self._edit.toPlainText().strip()
        if not text:
            self._parsed = {}
            self.accept()
            return
        try:
            val = json.loads(text)
        except json.JSONDecodeError as e:
            self._error.setText(str(e))
            self._error.show()
            return
        if not isinstance(val, dict):
            self._error.setText("Es muss ein JSON-Objekt sein.")
            self._error.show()
            return
        self._parsed = val
        self.accept()

    def get_input(self) -> dict:
        return getattr(self, "_parsed", {})
