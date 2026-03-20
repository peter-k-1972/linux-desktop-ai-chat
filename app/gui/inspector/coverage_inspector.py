"""
CoverageInspector – Inspector-Inhalt für Coverage-Details.

Failure Class, Guard-Zuordnung, Coverage-Status.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class CoverageInspector(QWidget):
    """Inspector für Coverage-Kontext im QA-&-Governance-Bereich."""

    def __init__(
        self,
        failure_class: str = "(keine)",
        guard: str = "—",
        coverage_status: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("coverageInspector")
        self._failure_class = failure_class
        self._guard = guard
        self._coverage_status = coverage_status
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Failure Class", self._failure_class),
            ("Guard-Zuordnung", self._guard),
            ("Coverage-Status", self._coverage_status),
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
