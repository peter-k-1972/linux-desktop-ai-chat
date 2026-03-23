"""Dialog: neuen Workflow anlegen."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
)


class WorkflowCreateDialog(QDialog):
    """Abfrage workflow_id, Name, optionale Beschreibung."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neuer Workflow")
        self.setMinimumWidth(420)
        layout = QFormLayout(self)
        self._wid = QLineEdit()
        self._wid.setPlaceholderText("eindeutige ID, z. B. my_workflow")
        layout.addRow("Workflow-ID:", self._wid)
        self._name = QLineEdit()
        self._name.setPlaceholderText("Anzeigename")
        layout.addRow("Name:", self._name)
        self._desc = QTextEdit()
        self._desc.setPlaceholderText("Beschreibung (optional)")
        self._desc.setMaximumHeight(80)
        layout.addRow("Beschreibung:", self._desc)
        hint = QLabel(
            "Projektzuordnung: der neue Workflow übernimmt das aktuell aktive Projekt "
            "(sichtbar in der Kopfzeile). Ohne aktives Projekt wird der Workflow global gespeichert."
        )
        hint.setWordWrap(True)
        hint.setObjectName("workflowCreateProjectHint")
        layout.addRow(hint)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def workflow_id(self) -> str:
        return (self._wid.text() or "").strip()

    def workflow_name(self) -> str:
        return (self._name.text() or "").strip()

    def description(self) -> str:
        return (self._desc.toPlainText() or "").strip()
