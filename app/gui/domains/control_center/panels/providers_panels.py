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

from app.gui.shared.layout_constants import (
    WIDGET_SPACING,
    apply_card_inner_layout,
)
from app.gui.themes.control_center_styles import (
    cc_body_label_style,
    cc_muted_caption_style,
    cc_name_emphasis_style,
    cc_offline_badge_style,
    cc_online_badge_style,
    cc_panel_frame_style,
    cc_refresh_button_style,
    cc_section_title_style,
    cc_status_error_style,
    cc_table_style,
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
        self.setStyleSheet(cc_panel_frame_style())
        layout = QVBoxLayout(self)
        apply_card_inner_layout(layout)
        layout.setSpacing(WIDGET_SPACING)

        row = QHBoxLayout()
        row.setSpacing(WIDGET_SPACING)
        title = QLabel("Provider")
        title.setStyleSheet(cc_section_title_style())
        row.addWidget(title)

        self._refresh_btn = QPushButton("Aktualisieren")
        self._refresh_btn.setObjectName("refreshProvidersButton")
        self._refresh_btn.setStyleSheet(cc_refresh_button_style())
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
        self._table.setStyleSheet(cc_table_style())
        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(cc_muted_caption_style())
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
        self._status_label.setStyleSheet(cc_muted_caption_style())
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
        self._status_label.setStyleSheet(cc_status_error_style())
        self._status_label.setText(message)


class ProviderStatusPanel(QFrame):
    """Provider-Status / Runtime-Verfügbarkeit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("providerStatusPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(cc_panel_frame_style())
        layout = QVBoxLayout(self)
        apply_card_inner_layout(layout)
        layout.setSpacing(WIDGET_SPACING)

        title = QLabel("Runtime-Verfügbarkeit")
        title.setStyleSheet(cc_section_title_style())
        layout.addWidget(title)

        self._ollama_label = QLabel("Ollama: —")
        self._ollama_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._ollama_label)

        self._version_label = QLabel("Version: —")
        self._version_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._version_label)

        self._models_label = QLabel("Modelle: —")
        self._models_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._models_label)

    def set_status(self, online: bool, version: str | None, model_count: int) -> None:
        """Setzt Status-Anzeige für Ollama."""
        if online:
            self._ollama_label.setText("Ollama: Online")
            self._ollama_label.setStyleSheet(cc_online_badge_style())
        else:
            self._ollama_label.setText("Ollama: Offline")
            self._ollama_label.setStyleSheet(cc_offline_badge_style())
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
        self.setStyleSheet(cc_panel_frame_style())
        layout = QVBoxLayout(self)
        apply_card_inner_layout(layout)
        layout.setSpacing(WIDGET_SPACING)

        title = QLabel("Provider-Details")
        title.setStyleSheet(cc_section_title_style())
        layout.addWidget(title)

        self._name_label = QLabel("—")
        self._name_label.setStyleSheet(cc_name_emphasis_style())
        layout.addWidget(self._name_label)

        self._endpoint_label = QLabel("Endpoint: —")
        self._endpoint_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._endpoint_label)

        self._status_label = QLabel("Status: —")
        self._status_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._status_label)

        self._models_label = QLabel("Modelle: —")
        self._models_label.setStyleSheet(cc_body_label_style())
        layout.addWidget(self._models_label)

        self._usage_label = QLabel("")
        self._usage_label.setStyleSheet(cc_muted_caption_style())
        self._usage_label.setWordWrap(True)
        layout.addWidget(self._usage_label)

        layout.addStretch()

    def set_provider(
        self,
        name: str,
        endpoint: str = "—",
        status: str = "—",
        model_count: int = 0,
        usage_summary: str = "",
    ) -> None:
        """Setzt die Anzeige für einen Provider."""
        self._name_label.setText(name or "—")
        self._endpoint_label.setText(f"Endpoint: {endpoint}")
        self._status_label.setText(f"Status: {status}")
        self._models_label.setText(f"Modelle: {model_count}")
        self._usage_label.setText(usage_summary or "")
