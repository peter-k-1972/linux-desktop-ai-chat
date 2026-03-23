"""Dialog: Workflow duplizieren."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit


class WorkflowDuplicateDialog(QDialog):
    """Neue workflow_id und optional neuer Name."""

    def __init__(self, source_id: str, default_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workflow duplizieren")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self._wid = QLineEdit()
        self._wid.setPlaceholderText(f"neue ID (Quelle: {source_id})")
        layout.addRow("Neue Workflow-ID:", self._wid)
        self._name = QLineEdit()
        self._name.setText(default_name)
        layout.addRow("Name:", self._name)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def new_workflow_id(self) -> str:
        return (self._wid.text() or "").strip()

    def new_name(self) -> str:
        return (self._name.text() or "").strip()
