"""
IncidentOperationsView – Übersicht Incidents, Bindings, Replay-Status.
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
from app.qa.operations_models import IncidentOperationsData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class IncidentOperationsView(QWidget):
    """Incident Operations – Incidents, Bindings, Replay-Readiness."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = OperationsAdapter()
        self.data: IncidentOperationsData | None = None
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
        title = QLabel("Incident Operations")
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

        self.incidents_group = QGroupBox("Incidents")
        self.incidents_group.setObjectName("incidentsGroup")
        inc_layout = QVBoxLayout(self.incidents_group)
        self.incidents_table = QTableWidget(0, 6)
        self.incidents_table.setHorizontalHeaderLabels(["ID", "Titel", "Status", "Severity", "Subsystem", "Binding"])
        self.incidents_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        inc_layout.addWidget(self.incidents_table)
        self.incidents_empty = QLabel("Keine Incidents.")
        inc_layout.addWidget(self.incidents_empty)
        content_layout.addWidget(self.incidents_group)

        self.warnings_group = QGroupBox("Warnungen")
        self.warnings_group.setObjectName("warningsGroup")
        warn_layout = QVBoxLayout(self.warnings_group)
        self.warnings_label = QLabel("—")
        self.warnings_label.setWordWrap(True)
        warn_layout.addWidget(self.warnings_label)
        content_layout.addWidget(self.warnings_group)

        links_layout = QHBoxLayout()
        for label, fn in [("Incident Index", "incidents/index.json"), ("Analytics", "incidents/analytics.json")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, f=fn: self._open_file(f))
            links_layout.addWidget(btn)
        links_layout.addStretch()
        content_layout.addLayout(links_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _open_file(self, filename: str):
        path = _qa_dir() / filename
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Datei nicht gefunden", f"Datei nicht vorhanden:\n{path}")

    def refresh(self):
        self.data = self.adapter.load_incident_operations()
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.summary_label.setText("Keine Incident-Daten.")
            return

        d = self.data
        self.summary_label.setText(
            f"Incidents: {d.incident_count} | Offen: {d.open_count} | "
            f"Gebunden: {d.bound_count} | Replay-ready: {d.replay_ready_count}"
        )

        if d.incidents:
            self.incidents_empty.setVisible(False)
            self.incidents_table.setVisible(True)
            self.incidents_table.setRowCount(len(d.incidents))
            for i, inc in enumerate(d.incidents):
                self.incidents_table.setItem(i, 0, QTableWidgetItem(inc.incident_id))
                self.incidents_table.setItem(i, 1, QTableWidgetItem(inc.title))
                self.incidents_table.setItem(i, 2, QTableWidgetItem(inc.status))
                self.incidents_table.setItem(i, 3, QTableWidgetItem(inc.severity))
                self.incidents_table.setItem(i, 4, QTableWidgetItem(inc.subsystem))
                self.incidents_table.setItem(i, 5, QTableWidgetItem(inc.binding_status or "—"))
        else:
            self.incidents_empty.setVisible(True)
            self.incidents_table.setVisible(False)

        if d.warnings:
            self.warnings_label.setText("\n".join(f"• {w}" for w in d.warnings))
        else:
            self.warnings_label.setText("Keine Warnungen.")

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.summary_group, self.incidents_group, self.warnings_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
