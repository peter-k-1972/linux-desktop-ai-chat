"""
QADrilldownView – Detailansicht für QA (Gap Report, Coverage, Orphan Backlog).
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

from app.qa.dashboard_adapter import QADashboardAdapter
from app.qa.drilldown_models import QADrilldownData
from app.resources.styles import get_theme_colors


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _qa_dir() -> Path:
    return _project_root() / "docs" / "qa"


class QADrilldownView(QWidget):
    """QA-Detailansicht: Gaps, Coverage-Achsen, Orphan-Backlog."""

    back_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.adapter = QADashboardAdapter()
        self.data: QADrilldownData | None = None
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
        title = QLabel("QA Drilldown")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Gap-Report
        self.gap_group = QGroupBox("Priorisierte Gaps")
        self.gap_group.setObjectName("gapGroup")
        gap_layout = QVBoxLayout(self.gap_group)
        self.gap_table = QTableWidget(0, 5)
        self.gap_table.setHorizontalHeaderLabels(["ID", "Titel", "Severity", "Subsystem", "Typ"])
        self.gap_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        gap_layout.addWidget(self.gap_table)
        self.gap_empty = QLabel("Keine priorisierten Gaps.")
        gap_layout.addWidget(self.gap_empty)
        content_layout.addWidget(self.gap_group)

        # Coverage Summary
        self.coverage_group = QGroupBox("Coverage Summary")
        self.coverage_group.setObjectName("coverageGroup")
        cov_layout = QVBoxLayout(self.coverage_group)
        self.coverage_label = QLabel("Lade …")
        self.coverage_label.setWordWrap(True)
        cov_layout.addWidget(self.coverage_label)
        content_layout.addWidget(self.coverage_group)

        # Orphan Backlog
        self.orphan_group = QGroupBox("Orphan Review Backlog")
        self.orphan_group.setObjectName("orphanGroup")
        orphan_layout = QVBoxLayout(self.orphan_group)
        self.orphan_label = QLabel("—")
        self.orphan_label.setWordWrap(True)
        orphan_layout.addWidget(self.orphan_label)
        content_layout.addWidget(self.orphan_group)

        # Quick Links
        links_layout = QHBoxLayout()
        for label, fn in [("Gap Report (MD)", "PHASE3_GAP_REPORT.md"), ("Coverage Map", "QA_COVERAGE_MAP.json")]:
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
        self.data = self.adapter.load_qa_drilldown()
        self._update_ui()

    def _update_ui(self):
        if not self.data:
            self.gap_empty.setText("Keine QA-Daten verfügbar.")
            self.gap_empty.setVisible(True)
            self.gap_table.setVisible(False)
            return

        # Gaps
        gaps = self.data.gap_items
        self.gap_table.setRowCount(len(gaps))
        if gaps:
            self.gap_empty.setVisible(False)
            self.gap_table.setVisible(True)
            for i, g in enumerate(gaps):
                self.gap_table.setItem(i, 0, QTableWidgetItem(g.id))
                self.gap_table.setItem(i, 1, QTableWidgetItem(g.title))
                self.gap_table.setItem(i, 2, QTableWidgetItem(g.severity))
                self.gap_table.setItem(i, 3, QTableWidgetItem(g.subsystem))
                self.gap_table.setItem(i, 4, QTableWidgetItem(g.gap_type))
        else:
            self.gap_empty.setVisible(True)
            self.gap_table.setVisible(False)
            self.gap_empty.setText("Keine priorisierten Gaps.")

        # Coverage
        lines = []
        for ax in self.data.coverage_axes:
            s = f"• {ax.axis}: {ax.strength}"
            if ax.gap_count:
                s += f" ({ax.gap_count} Gaps)"
            if ax.total_count:
                s += f" – {ax.covered_count}/{ax.total_count}"
            lines.append(s)
        self.coverage_label.setText("\n".join(lines) if lines else "Keine Coverage-Daten.")

        # Orphan
        ob = self.data.orphan_breakdown
        if ob:
            parts = [
                f"Review-Kandidaten: {ob.review_candidates}",
                f"Whitelisted: {ob.whitelisted}",
                f"Excluded: {ob.excluded_by_path}",
                f"Treat as: {ob.treat_as}",
                f"CI-Blocking: {ob.ci_blocking}",
            ]
            self.orphan_label.setText("\n".join(parts))
        else:
            self.orphan_label.setText("Keine Orphan-Daten.")
        self.orphan_label.setText(self.orphan_label.text() + f"\n\nLetzte Verifikation: {self.data.last_verification or '—'}")

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in [self.gap_group, self.coverage_group, self.orphan_group]:
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()
