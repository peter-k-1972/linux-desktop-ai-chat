"""
ReplayInspector – Inspector-Inhalt für Replay-Details.

Replay-ID, Status, letzter Lauf, Ergebniszusammenfassung.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class ReplayInspector(QWidget):
    """Inspector für Replay-Kontext im QA-&-Governance-Bereich."""

    def __init__(
        self,
        replay_id: str = "(keine)",
        status: str = "—",
        last_run: str = "—",
        result_summary: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("replayInspector")
        self._replay_id = replay_id
        self._status = status
        self._last_run = last_run
        self._result_summary = result_summary
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Replay-ID", self._replay_id),
            ("Status", self._status),
            ("Letzter Lauf", self._last_run),
            ("Ergebniszusammenfassung", self._result_summary),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()
