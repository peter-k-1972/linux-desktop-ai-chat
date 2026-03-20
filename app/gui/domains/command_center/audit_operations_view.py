"""
AuditOperationsView – Operative Sicht auf Audit-Follow-ups und Technical Debt.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from app.qa.operations_adapter import OperationsAdapter
from app.qa.operations_models import AuditOperationsData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


class AuditOperationsView(QWidget):
    """Audit Operations – Follow-ups, Technical Debt, strukturierte Darstellung."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = OperationsAdapter()
        self.data: AuditOperationsData | None = None
        self._init_ui()
        self._apply_theme()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)
        header.addStretch()
        title = QLabel("Audit / Technical Debt")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.summary_group = QGroupBox("Übersicht")
        self.summary_group.setObjectName("summaryGroup")
        sum_layout = QVBoxLayout(self.summary_group)
        self.summary_label = QLabel("—")
        self.summary_label.setWordWrap(True)
        sum_layout.addWidget(self.summary_label)
        content_layout.addWidget(self.summary_group)

        self.items_group = QGroupBox("Follow-up-Punkte")
        self.items_group.setObjectName("itemsGroup")
        items_layout = QVBoxLayout(self.items_group)
        self.items_table = QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Kategorie", "Datei", "Beschreibung", "Zeile"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(self.items_table)
        self.items_empty = QLabel("Keine Audit-Punkte oder AUDIT_REPORT.md nicht gefunden.")
        items_layout.addWidget(self.items_empty)
        content_layout.addWidget(self.items_group)

        open_btn = QPushButton("Audit Report öffnen")
        open_btn.clicked.connect(lambda: self._open_file("AUDIT_REPORT.md"))
        content_layout.addWidget(open_btn)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _open_file(self, filename: str):
        path = _project_root() / filename
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht vorhanden:\n{path}")

    def refresh(self):
        self.data = self.adapter.load_audit_operations()
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.summary_label.setText("Keine Audit-Daten.")
            self.items_empty.setVisible(True)
            self.items_table.setVisible(False)
            return

        d = self.data
        if d.by_category:
            parts = [f"{k}: {v}" for k, v in d.by_category.items()]
            self.summary_label.setText(f"Punkte nach Kategorie: {', '.join(parts)}")
        else:
            self.summary_label.setText("Keine Follow-up-Punkte im Audit Report.")

        if d.items:
            self.items_empty.setVisible(False)
            self.items_table.setVisible(True)
            self.items_table.setRowCount(len(d.items))
            for i, item in enumerate(d.items):
                self.items_table.setItem(i, 0, QTableWidgetItem(item.category))
                self.items_table.setItem(i, 1, QTableWidgetItem(item.source))
                self.items_table.setItem(i, 2, QTableWidgetItem(item.description))
                self.items_table.setItem(i, 3, QTableWidgetItem(item.location))
        else:
            self.items_empty.setVisible(True)
            self.items_table.setVisible(False)

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.summary_group, self.items_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
