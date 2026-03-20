"""
Models Panels – Installed Models, Status, Details, Action-Fläche.

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


def _format_size(size_bytes: int | float | None) -> str:
    """Formatiert Bytes zu lesbarer Größe."""
    if size_bytes is None:
        return "—"
    try:
        n = float(size_bytes)
        if n >= 1e9:
            return f"{n / 1e9:.1f} GB"
        if n >= 1e6:
            return f"{n / 1e6:.1f} MB"
        if n >= 1e3:
            return f"{n / 1e3:.1f} KB"
        return f"{n:.0f} B"
    except (TypeError, ValueError):
        return "—"


class ModelListPanel(QFrame):
    """Liste verfügbarer Modelle von Ollama."""

    model_selected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelListPanel")
        self.setMinimumHeight(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        row = QHBoxLayout()
        title = QLabel("Verfügbare Modelle")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        row.addWidget(title)

        self._refresh_btn = QPushButton("Aktualisieren")
        self._refresh_btn.setObjectName("refreshModelsButton")
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
        self._table.setObjectName("modelListTable")
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Modell", "Provider", "Größe", "Status"])
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
            model_name = item.data(Qt.ItemDataRole.UserRole) or item.text()
            if model_name:
                self.model_selected.emit(model_name)

    def set_models(self, models: list) -> None:
        """Setzt die Modellliste. models: [{"name": str, "size": int?, ...}, ...]"""
        self._status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self._table.setRowCount(len(models))
        for row, m in enumerate(models):
            name = m.get("name") or m.get("model", "—")
            size = _format_size(m.get("size"))
            self._table.setItem(row, 0, QTableWidgetItem(name))
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, name)
            self._table.setItem(row, 1, QTableWidgetItem("Ollama"))
            self._table.setItem(row, 2, QTableWidgetItem(size))
            self._table.setItem(row, 3, QTableWidgetItem("Bereit"))
        self._status_label.setText(f"{len(models)} Modell(e)")

    def set_empty(self, message: str = "Keine Modelle – ist Ollama gestartet?") -> None:
        """Zeigt leeren Zustand."""
        self._table.setRowCount(0)
        self._status_label.setText(message)

    def set_loading(self, message: str = "Lade Modelle…") -> None:
        """Zeigt Ladezustand."""
        self._status_label.setText(message)

    def set_error(self, message: str) -> None:
        """Zeigt Fehlermeldung."""
        self._table.setRowCount(0)
        self._status_label.setStyleSheet("color: #dc2626; font-size: 11px;")
        self._status_label.setText(message)

    def _on_refresh(self) -> None:
        """Löst Neuladen aus. Parent verbindet refresh_requested mit _load_models."""
        self.refresh_requested.emit()


class ModelSummaryPanel(QFrame):
    """Modell-Details für ausgewähltes Modell."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelSummaryPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Modell-Details")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._name_label = QLabel("—")
        self._name_label.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 500;")
        layout.addWidget(self._name_label)

        self._provider_label = QLabel("Provider: —")
        self._provider_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._provider_label)

        self._size_label = QLabel("Größe: —")
        self._size_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._size_label)

        self._default_label = QLabel("")
        self._default_label.setStyleSheet("color: #059669; font-size: 12px; font-weight: 500;")
        layout.addWidget(self._default_label)

        layout.addStretch()

    def set_model(self, name: str, provider: str = "Ollama", size: str = "—", is_default: bool = False) -> None:
        """Setzt die Anzeige für ein Modell."""
        self._name_label.setText(name or "—")
        self._provider_label.setText(f"Provider: {provider}")
        self._size_label.setText(f"Größe: {size}")
        self._default_label.setText("✓ Standardmodell" if is_default else "")


class ModelStatusPanel(QFrame):
    """Modell-Status: Anzahl, Standard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelStatusPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Status")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._available_label = QLabel("Verfügbar: —")
        self._available_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self._available_label)

        self._default_label = QLabel("Standard: —")
        self._default_label.setStyleSheet("color: #334155; font-size: 12px;")
        layout.addWidget(self._default_label)

    def set_status(self, available_count: int, default_model: str) -> None:
        """Setzt Status-Anzeige."""
        self._available_label.setText(f"Verfügbar: {available_count} Modell(e)")
        self._default_label.setText(f"Standard: {default_model or '—'}")


class ModelActionPanel(QFrame):
    """Aktionen: Als Standard setzen."""

    set_default_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modelActionPanel")
        self._current_model: str | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("Aktionen")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._btn_default = QPushButton("Als Standard setzen")
        self._btn_default.setObjectName("setDefaultButton")
        self._btn_default.setStyleSheet(
            "QPushButton { background: #2563eb; color: white; padding: 8px 16px; "
            "border-radius: 6px; font-weight: 500; } "
            "QPushButton:hover { background: #1d4ed8; } "
            "QPushButton:disabled { background: #9ca3af; }"
        )
        self._btn_default.clicked.connect(self._on_set_default)
        self._btn_default.setEnabled(False)
        layout.addWidget(self._btn_default)

        layout.addStretch()

    def _on_set_default(self) -> None:
        if self._current_model:
            self.set_default_requested.emit(self._current_model)

    def set_current_model(self, model_name: str | None) -> None:
        """Setzt das aktuell ausgewählte Modell."""
        self._current_model = model_name
        self._btn_default.setEnabled(bool(model_name))
