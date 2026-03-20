"""
Providers Panels – Provider List, Status, Endpoint, Runtime.

Anbindung an Ollama über ChatBackend.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
)
from PySide6.QtCore import Signal, Qt


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class ProviderListPanel(QFrame):
    """Provider-Liste mit Endpoint und Status."""

    provider_selected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("providerListPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Provider")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        row.addWidget(title)

        self._refresh_btn = QPushButton("Aktualisieren")
        self._refresh_btn.setObjectName("refreshProvidersButton")
        self._refresh_btn.setStyleSheet(
            "QPushButton { background: #e0e7ff; color: #4338ca; padding: 6px 12px; "
            "border-radius: 6px; font-size: 12px; } "
            "QPushButton:hover { background: #c7d2fe; }"
        )
        self._refresh_btn.clicked.connect(self._on_refresh)
        row.addWidget(self._refresh_btn)
        row.addStretch()
        layout.addLayout(row)

        self._table = QTableWidget()
        self._table.setObjectName("providerListTable")
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Provider", "Typ", "Endpoint", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setRowCount(0)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self._status_label)

    def _on_cell_clicked(self, row: int, _col: int) -> None:
        item = self._table.item(row, 0)
        if item:
            name = item.data(Qt.ItemDataRole.UserRole) or item.text()
            if name:
                self.provider_selected.emit(name)

    def _on_refresh(self) -> None:
        self.refresh_requested.emit()

    def set_providers(self, providers: list) -> None:
        """Setzt Provider-Liste. providers: [{"name": str, "type": str, "endpoint": str, "status": str}, ...]"""
        self._status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self._table.setRowCount(len(providers))
        for row, p in enumerate(providers):
            name = p.get("name", "—")
            typ = p.get("type", "—")
            endpoint = p.get("endpoint", "—")
            status = p.get("status", "—")
            self._table.setItem(row, 0, QTableWidgetItem(name))
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, name)
            self._table.setItem(row, 1, QTableWidgetItem(typ))
            self._table.setItem(row, 2, QTableWidgetItem(endpoint))
            self._table.setItem(row, 3, QTableWidgetItem(status))
        self._status_label.setText(f"{len(providers)} Provider")

    def set_empty(self, message: str = "Keine Provider – ist Ollama gestartet?") -> None:
        self._table.setRowCount(0)
        self._status_label.setText(message)

    def set_loading(self, message: str = "Lade Provider…") -> None:
        self._status_label.setText(message)

    def set_error(self, message: str) -> None:
        self._table.setRowCount(0)
        self._status_label.setStyleSheet("color: #dc2626; font-size: 11px;")
        self._status_label.setText(message)


class ProviderStatusPanel(QFrame):
    """Provider-Status / Runtime-Verfügbarkeit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("providerStatusPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Runtime-Verfügbarkeit")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._ollama_label = QLabel("Ollama: —")
        self._ollama_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._ollama_label)

        self._version_label = QLabel("Version: —")
        self._version_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._version_label)

        self._models_label = QLabel("Modelle: —")
        self._models_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._models_label)

    def set_status(self, online: bool, version: str | None, model_count: int) -> None:
        """Setzt Status-Anzeige für Ollama."""
        if online:
            self._ollama_label.setText("Ollama: Online")
            self._ollama_label.setStyleSheet("color: #059669; font-size: 12px; font-weight: 500;")
        else:
            self._ollama_label.setText("Ollama: Offline")
            self._ollama_label.setStyleSheet("color: #dc2626; font-size: 12px;")
        self._version_label.setText(f"Version: {version or '—'}")
        self._models_label.setText(f"Modelle: {model_count}")


class ProviderSummaryPanel(QFrame):
    """Provider-Details für ausgewählten Provider."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("providerSummaryPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Provider-Details")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._name_label = QLabel("—")
        self._name_label.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 500;")
        layout.addWidget(self._name_label)

        self._endpoint_label = QLabel("Endpoint: —")
        self._endpoint_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._endpoint_label)

        self._status_label = QLabel("Status: —")
        self._status_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._status_label)

        self._models_label = QLabel("Modelle: —")
        self._models_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._models_label)

        layout.addStretch()

    def set_provider(
        self,
        name: str,
        endpoint: str = "—",
        status: str = "—",
        model_count: int = 0,
    ) -> None:
        """Setzt die Anzeige für einen Provider."""
        self._name_label.setText(name or "—")
        self._endpoint_label.setText(f"Endpoint: {endpoint}")
        self._status_label.setText(f"Status: {status}")
        self._models_label.setText(f"Modelle: {model_count}")
