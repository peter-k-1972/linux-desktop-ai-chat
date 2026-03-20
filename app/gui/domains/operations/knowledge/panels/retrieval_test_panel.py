"""
RetrievalTestPanel – Retrieval-Test.

Query-Eingabe, Ausführung, Trefferanzeige.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Signal, Qt


def _panel_style() -> str:
    return (
        "background: white; border: 1px solid #e5e7eb; border-radius: 10px; "
        "padding: 12px;"
    )


class RetrievalTestPanel(QFrame):
    """Retrieval-Test: Query, Suchen, Treffer."""

    retrieval_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("retrievalTestPanel")
        self.setMinimumHeight(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Retrieval-Test")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        row = QHBoxLayout()
        self._query = QLineEdit()
        self._query.setPlaceholderText("Suchanfrage eingeben…")
        self._query.setStyleSheet(
            "QLineEdit { padding: 8px 12px; border: 1px solid #e5e7eb; "
            "border-radius: 6px; font-size: 13px; }"
        )
        self._query.returnPressed.connect(self._on_search)
        row.addWidget(self._query, 1)

        btn = QPushButton("Suchen")
        btn.setObjectName("searchButton")
        btn.setStyleSheet(
            """
            #searchButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            #searchButton:hover { background: #1d4ed8; }
            """
        )
        btn.clicked.connect(self._on_search)
        row.addWidget(btn)
        layout.addLayout(row)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self._status)

        results_label = QLabel("Treffer")
        results_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #374151;")
        layout.addWidget(results_label)

        self._results = QTextEdit()
        self._results.setReadOnly(True)
        self._results.setMinimumHeight(120)
        self._results.setStyleSheet(
            "QTextEdit { background: #f8fafc; border: 1px solid #e5e7eb; "
            "border-radius: 6px; padding: 8px; font-size: 12px; "
            "font-family: monospace; }"
        )
        self._results.setPlaceholderText("Treffer erscheinen hier.")
        layout.addWidget(self._results, 1)

    def _on_search(self) -> None:
        text = self._query.text().strip()
        if text:
            self.retrieval_requested.emit(text)

    def set_results(self, text: str) -> None:
        """Setzt die Trefferanzeige."""
        self._results.setPlainText(text or "Keine Treffer.")

    def set_status(self, text: str) -> None:
        """Setzt den Status-Text."""
        self._status.setText(text)

    def set_sending(self, sending: bool) -> None:
        """Deaktiviert während der Suche."""
        self._query.setEnabled(not sending)

    def get_query(self) -> str:
        """Liefert den aktuellen Query-Text."""
        return self._query.text().strip()

