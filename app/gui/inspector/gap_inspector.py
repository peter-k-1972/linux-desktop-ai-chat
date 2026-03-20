"""
GapInspector – Inspector-Inhalt für Gap-Details.

Gap-Typ, Priorität, Status, Review-Hinweise.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class GapInspector(QWidget):
    """Inspector für Gap-Kontext im QA-&-Governance-Bereich."""

    def __init__(
        self,
        gap_id: str = "(keine)",
        gap_type: str = "—",
        priority: str = "—",
        status: str = "—",
        review_hint: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("gapInspector")
        self._gap_id = gap_id
        self._gap_type = gap_type
        self._priority = priority
        self._status = status
        self._review_hint = review_hint
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Gap-ID", self._gap_id),
            ("Gap-Typ", self._gap_type),
            ("Priorität / Status", f"{self._priority} · {self._status}"),
            ("Review-Hinweise", self._review_hint),
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
