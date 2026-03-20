"""
TestInspector – Inspector-Inhalt für Test-Details.

Test-ID, Kategorie, Status, Tags, Mapping.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class TestInspector(QWidget):
    """Inspector für Test-Kontext im QA-&-Governance-Bereich."""

    def __init__(
        self,
        test_id: str = "(keine)",
        category: str = "—",
        status: str = "—",
        tags: str = "—",
        mapping: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("testInspector")
        self._test_id = test_id
        self._category = category
        self._status = status
        self._tags = tags
        self._mapping = mapping
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Test-ID", self._test_id),
            ("Kategorie", self._category),
            ("Status", self._status),
            ("Tags / Mapping", f"{self._tags} · {self._mapping}"),
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
